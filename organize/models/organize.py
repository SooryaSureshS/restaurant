# -*- coding: utf-8 -*-
from ast import literal_eval
from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
import json
import logging
import pytz
import uuid
from math import ceil, modf
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import format_time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import format_date, format_datetime

_logger = logging.getLogger(__name__)


def days_span(start_datetime, end_datetime):
    if not isinstance(start_datetime, datetime):
        raise ValueError
    if not isinstance(end_datetime, datetime):
        raise ValueError
    end = datetime.combine(end_datetime, datetime.min.time())
    start = datetime.combine(start_datetime, datetime.min.time())
    duration = end - start
    return duration.days + 1


class Organize(models.Model):
    _name = 'organize.slot'
    _description = 'Organize Shift'
    _order = 'start_datetime,id desc'
    _rec_name = 'name'
    _check_company_auto = True

    def _default_start_datetime(self):
        return datetime.combine(fields.Datetime.now(), datetime.min.time())

    def _default_end_datetime(self):
        return datetime.combine(fields.Datetime.now(), datetime.max.time())

    name = fields.Text('Note')
    employee_id = fields.Many2one('hr.employee', "Employee", group_expand='_read_group_employee_id')
    work_email = fields.Char("Work Email", related='employee_id.work_email')
    department_id = fields.Many2one(related='employee_id.department_id', store=True)
    user_id = fields.Many2one('res.users', string="User", related='employee_id.user_id', store=True, readonly=True)
    manager_id = fields.Many2one(related='employee_id.parent_id')
    company_id = fields.Many2one('res.company', string="Company", required=True,
                                 compute="_compute_organize_slot_company_id", store=True, readonly=False)
    role_id = fields.Many2one('organize.role', string="Role", compute="_compute_role_id", store=True, readonly=False,
                              copy=True, group_expand='_read_group_role_id')
    color = fields.Integer("Color", related='role_id.color')
    was_copied = fields.Boolean("This Shift Was Copied From Previous Week", default=False, readonly=True)
    access_token = fields.Char("Security Token", default=lambda self: str(uuid.uuid4()), required=True, copy=False,
                               readonly=True)

    start_datetime = fields.Datetime(
        "Start Date", compute='_compute_datetime', store=True, readonly=False, required=True,
        copy=True, default=_default_start_datetime)
    end_datetime = fields.Datetime(
        "End Date", compute='_compute_datetime', store=True, readonly=False, required=True,
        copy=True, default=_default_end_datetime)
    allow_self_unassign = fields.Boolean('Let Employee Unassign Themselves',
                                         related='company_id.organize_allow_self_unassign')
    is_assigned_to_me = fields.Boolean('Is This Shift Assigned To The Current User',
                                       compute='_compute_is_assigned_to_me')
    overlap_slot_count = fields.Integer('Overlapping Slots', compute='_compute_overlap_slot_count')

    # *******************
    is_timeoff_overlap = fields.Boolean('Employee Time Off')
    timeoff_date_overlap = fields.Char('Employee Time Off Overlap')
    # *******************

    is_past = fields.Boolean('Is This Shift In The Past?', compute='_compute_past_shift')

    allocation_type = fields.Selection([
        ('organize', 'Organize'),
        ('forecast', 'Forecast')
    ], compute='_compute_allocation_type')
    allocated_hours = fields.Float("Allocated Hours", compute='_compute_allocated_hours', store=True, readonly=False)
    allocated_percentage = fields.Float("Allocated Time",
                                        compute='_compute_allocated_hours', store=True, readonly=False)
    working_days_count = fields.Integer("Number of Working Days", compute='_compute_working_days_count', store=True)

    is_published = fields.Boolean("Is The Shift Sent", default=False, readonly=True, copy=False)
    publication_warning = fields.Boolean(
        "Modified Since Last Publication", default=False, compute='_compute_publication_warning',
        store=True, readonly=True, copy=False)
    template_autocomplete_ids = fields.Many2many('organize.slot.template', store=False,
                                                 compute='_compute_template_autocomplete_ids')
    template_id = fields.Many2one('organize.slot.template', string='Shift Templates', compute='_compute_template_id',
                                  readonly=False, store=True)
    template_reset = fields.Boolean()
    previous_template_id = fields.Many2one('organize.slot.template')
    allow_template_creation = fields.Boolean(string='Allow Template Creation',
                                             compute='_compute_allow_template_creation')
    recurrency_id = fields.Many2one('organize.recurrency', readonly=True, index=True, ondelete="set null", copy=False)
    repeat = fields.Boolean("Repeat", compute='_compute_repeat', inverse='_inverse_repeat')
    repeat_interval = fields.Integer("Repeat every", default=1, compute='_compute_repeat_interval',
                                     inverse='_inverse_repeat')
    repeat_type = fields.Selection([('forever', 'Forever'), ('until', 'Until')], string='Repeat Type',
                                   default='forever', compute='_compute_repeat_type', inverse='_inverse_repeat')
    repeat_until = fields.Date("Repeat Until", compute='_compute_repeat_until', inverse='_inverse_repeat')
    confirm_delete = fields.Boolean('Confirm Slots Deletion', compute='_compute_confirm_delete')

    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    currency_symbol = fields.Char(string='Symbol', related="currency_id.symbol")
    employee_timesheet_cost = fields.Monetary('Employee Timesheet Cost', related="employee_id.timesheet_cost",
                                              currency_field='currency_id', groups="hr.group_hr_user", default=0.0)

    _sql_constraints = [
        ('check_start_date_lower_end_date', 'CHECK(end_datetime > start_datetime)',
         'Shift end date should be greater than its start date'),
        ('check_allocated_hours_positive', 'CHECK(allocated_hours >= 0)', 'You cannot have negative shift'),
    ]

    @api.depends('repeat_until')
    def _compute_confirm_delete(self):
        for line in self:
            if line.recurrency_id and line.repeat_until:
                line.confirm_delete = fields.Date.to_date(
                    line.recurrency_id.repeat_until) > line.repeat_until if line.recurrency_id.repeat_until else True
            else:
                line.confirm_delete = False

    @api.constrains('repeat_until')
    def _check_repeat_until(self):
        if any([line.repeat_until and line.repeat_until < line.start_datetime.date() for line in self]):
            raise UserError(_('The recurrence until date should be after the shift start date'))

    @api.onchange('repeat_until')
    def _onchange_repeat_until(self):
        self._check_repeat_until()

    @api.depends('employee_id.company_id')
    def _compute_organize_slot_company_id(self):
        for line in self:
            if line.employee_id:
                line.company_id = line.employee_id.company_id.id
            if not line.company_id.id:
                line.company_id = line.env.company

    @api.depends('start_datetime')
    def _compute_past_shift(self):
        now = fields.Datetime.now()
        for line in self:
            line.is_past = line.end_datetime < now

    @api.depends('employee_id', 'template_id')
    def _compute_role_id(self):
        for line in self:
            if not line.role_id:
                if line.employee_id.default_organize_role_id:
                    line.role_id = line.employee_id.default_organize_role_id
                else:
                    line.role_id = False

            if line.template_id:
                line.previous_template_id = line.template_id
                if line.template_id.role_id:
                    line.role_id = line.template_id.role_id
            elif line.previous_template_id and not line.template_id and line.previous_template_id.role_id == line.role_id:
                line.role_id = False

    @api.depends('user_id')
    def _compute_is_assigned_to_me(self):
        for line in self:
            line.is_assigned_to_me = line.user_id == self.env.user

    @api.depends('start_datetime', 'end_datetime')
    def _compute_allocation_type(self):
        for line in self:
            if line.start_datetime and line.end_datetime and line._get_slot_duration() < 24:
                line.allocation_type = 'organize'
            else:
                line.allocation_type = 'forecast'

    @api.depends('start_datetime', 'end_datetime', 'employee_id.resource_calendar_id', 'allocated_hours')
    def _compute_allocated_percentage(self):
        for line in self:
            if line.start_datetime and line.end_datetime and line.start_datetime != line.end_datetime:
                if line.allocation_type == 'organize':
                    line.allocated_percentage = 100 * line.allocated_hours / line._get_slot_duration()
                else:
                    if line.employee_id:
                        work_hours = line.employee_id._get_work_days_data_batch(line.start_datetime, line.end_datetime,
                                                                                compute_leaves=True)[
                            line.employee_id.id]['hours']
                        line.allocated_percentage = 100 * line.allocated_hours / work_hours if work_hours else 100
                    else:
                        line.allocated_percentage = 100

    @api.depends(
        'start_datetime', 'end_datetime', 'employee_id.resource_calendar_id',
        'company_id.resource_calendar_id', 'allocated_percentage')
    def _compute_allocated_hours(self):
        percentage_field = self._fields['allocated_percentage']
        self.env.remove_to_compute(percentage_field, self)
        for line in self:
            if line.start_datetime and line.end_datetime:
                # ratio = line.allocated_percentage / 100.0 or 1
                ratio = 1
                if line.allocation_type == 'organize':
                    line.allocated_hours = line._get_slot_duration() * ratio
                    line.allocated_percentage = line.allocated_hours
                else:
                    calendar = line.employee_id.resource_calendar_id or line.company_id.resource_calendar_id
                    hours = calendar.get_work_hours_count(line.start_datetime,
                                                          line.end_datetime) if calendar else line._get_slot_duration()
                    line.allocated_hours = hours * ratio
                    line.allocated_percentage = line.allocated_hours
            else:
                line.allocated_percentage = 0.0
                line.allocated_hours = 0.0


    @api.depends('start_datetime', 'end_datetime', 'employee_id')
    def _compute_working_days_count(self):
        for line in self:
            if line.employee_id:
                line.working_days_count = ceil(line.employee_id._get_work_days_data_batch(
                    line.start_datetime, line.end_datetime, compute_leaves=True
                )[line.employee_id.id]['days'])
            else:
                line.working_days_count = 0


    @api.depends('start_datetime', 'end_datetime', 'employee_id')
    def _compute_overlap_slot_count(self):
        if self.ids:
            self.flush(['start_datetime', 'end_datetime', 'employee_id'])
            query = """
                   SELECT S1.id,count(*) FROM
                       organize_slot S1, organize_slot S2
                   WHERE
                       S1.start_datetime < S2.end_datetime and S1.end_datetime > S2.start_datetime and S1.id <> S2.id and S1.employee_id = S2.employee_id
                       and S1.id in %s
                   GROUP BY S1.id;
               """
            self.env.cr.execute(query, (tuple(self.ids),))
            overlap_mapping = dict(self.env.cr.fetchall())
            for line in self:
                line.overlap_slot_count = overlap_mapping.get(line.id, 0)
        else:
            self.overlap_slot_count = 0


    def _get_slot_duration(self):
        self.ensure_one()
        return (self.end_datetime - self.start_datetime).total_seconds() / 3600.0


    def _get_domain_template_slots(self):
        domain = ['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)]
        if self.role_id:
            domain += ['|', ('role_id', '=', self.role_id.id), ('role_id', '=', False)]
        elif self.employee_id and self.employee_id.sudo().organize_role_ids:
            domain += ['|', ('role_id', 'in', self.employee_id.sudo().organize_role_ids.ids), ('role_id', '=', False)]
        return domain


    @api.depends('role_id', 'employee_id')
    def _compute_template_autocomplete_ids(self):
        domain = self._get_domain_template_slots()
        templates = self.env['organize.slot.template'].search(domain, order='start_time', limit=10)
        self.template_autocomplete_ids = templates + self.template_id


    @api.depends('employee_id', 'role_id', 'start_datetime', 'allocated_hours')
    def _compute_template_id(self):
        for line in self.filtered(lambda s: s.template_id):
            line.previous_template_id = line.template_id
            line.template_reset = False
            if line._different_than_template():
                line.template_id = False
                line.previous_template_id = False
                line.template_reset = True


    def _different_than_template(self, check_empty=True):
        self.ensure_one()
        template_fields = self._get_template_fields().items()
        for template_field, slot_field in template_fields:
            if self.template_id[template_field] or not check_empty:
                if template_field == 'start_time':
                    h = int(self.template_id.start_time)
                    m = round(modf(self.template_id.start_time)[0] * 60.0)
                    slot_time = self[slot_field].astimezone(pytz.timezone(self._get_tz()))
                    if slot_time.hour != h or slot_time.minute != m:
                        return True
                else:
                    if self[slot_field] != self.template_id[template_field]:
                        return True
        return False


    @api.depends('template_id', 'role_id', 'allocated_hours')
    def _compute_allow_template_creation(self):
        for line in self:
            values = self._prepare_template_values()
            domain = [(x, '=', values[x]) for x in values.keys()]
            existing_templates = self.env['organize.slot.template'].search(domain, limit=1)
            line.allow_template_creation = not existing_templates and line._different_than_template(check_empty=False)


    @api.depends('recurrency_id')
    def _compute_repeat(self):
        for line in self:
            if line.recurrency_id:
                line.repeat = True
            else:
                line.repeat = False


    @api.depends('recurrency_id.repeat_interval')
    def _compute_repeat_interval(self):
        for line in self:
            if line.recurrency_id:
                line.repeat_interval = line.recurrency_id.repeat_interval
            else:
                line.repeat_interval = False


    @api.depends('recurrency_id.repeat_until')
    def _compute_repeat_until(self):
        for line in self:
            if line.recurrency_id:
                line.repeat_until = line.recurrency_id.repeat_until
            else:
                line.repeat_until = False


    @api.depends('recurrency_id.repeat_type')
    def _compute_repeat_type(self):
        for line in self:
            if line.recurrency_id:
                line.repeat_type = line.recurrency_id.repeat_type
            else:
                line.repeat_type = False


    def _inverse_repeat(self):
        for line in self:
            if line.repeat and not line.recurrency_id.id:
                recurrency_values = {
                    'repeat_interval': line.repeat_interval,
                    'repeat_until': line.repeat_until if line.repeat_type == 'until' else False,
                    'repeat_type': line.repeat_type,
                    'company_id': line.company_id.id,
                }
                recurrence = self.env['organize.recurrency'].create(recurrency_values)
                line.recurrency_id = recurrence
                line.recurrency_id._repeat_slot()
            elif not line.repeat and line.recurrency_id.id and (
                    line.repeat_type == line.recurrency_id.repeat_type and
                    line.repeat_until == line.recurrency_id.repeat_until and
                    line.repeat_interval == line.recurrency_id.repeat_interval
            ):
                line.recurrency_id._delete_slot(line.end_datetime)
                line.recurrency_id.unlink()


    @api.depends('employee_id', 'template_id')
    def _compute_datetime(self):
        for line in self:
            user_tz = pytz.timezone(line._get_tz())
            employee = line.employee_id if line.employee_id else line.env.user.employee_id

            previous_end = line.end_datetime or False
            start = line.start_datetime or self._default_start_datetime()
            end = line.end_datetime or self._default_end_datetime()
            work_interval = employee._adjust_to_calendar(start, end)
            start_datetime, end_datetime = work_interval[employee] if employee and employee.tz == line.env.user.tz else (
                start, end)

            if not line.previous_template_id and not line.template_reset:
                if start_datetime and not line.start_datetime:
                    line.start_datetime = start_datetime.astimezone(pytz.utc).replace(tzinfo=None)
                if end_datetime and not line.end_datetime:
                    line.end_datetime = end_datetime.astimezone(pytz.utc).replace(tzinfo=None)

            if line.template_id and line.start_datetime:
                h = int(line.template_id.start_time)
                m = round(modf(line.template_id.start_time)[0] * 60.0)
                start = pytz.utc.localize(line.start_datetime).astimezone(user_tz)
                start = start.replace(hour=int(h), minute=int(m))
                line.start_datetime = start.astimezone(pytz.utc).replace(tzinfo=None)

                h, m = divmod(line.template_id.duration, 1)
                delta = timedelta(hours=int(h), minutes=int(m * 60))
                line.end_datetime = line.start_datetime + delta
                if previous_end:
                    line.end_datetime += previous_end.date() - line.end_datetime.date()


    @api.depends('start_datetime', 'end_datetime', 'employee_id')
    def _compute_publication_warning(self):
        with_warning = self.filtered(lambda t: t.employee_id and t.is_published)
        with_warning.update({'publication_warning': True})


    def _company_working_hours(self, start, end):
        company = self.company_id or self.env.company
        work_interval = company.resource_calendar_id._work_intervals(start, end)
        intervals = [(start, stop) for start, stop, attendance in work_interval]
        start_datetime, end_datetime = (intervals[0][0], intervals[-1][-1]) if intervals else (start, end)

        return (start_datetime, end_datetime)


    @api.model
    def default_get(self, fields_list):
        res = super(Organize, self).default_get(fields_list)

        if not res.get('employee_id') and 'start_datetime' in fields_list:
            start_datetime = fields.Datetime.from_string(res.get('start_datetime'))
            end_datetime = fields.Datetime.from_string(res.get('end_datetime')) if res.get('end_datetime') else False
            start = pytz.utc.localize(start_datetime)
            end = pytz.utc.localize(end_datetime) if end_datetime else self._default_end_datetime()
            opening_hours = self._company_working_hours(start, end)
            res['start_datetime'] = opening_hours[0].astimezone(pytz.utc).replace(tzinfo=None)

            if 'end_datetime' in fields_list:
                res['end_datetime'] = opening_hours[1].astimezone(pytz.utc).replace(tzinfo=None)

        return res


    def _init_column(self, column_name):
        if column_name != 'access_token':
            super(Organize, self)._init_column(column_name)
        else:
            query = """
                   UPDATE %(table_name)s
                   SET access_token = md5(md5(random()::varchar || id::varchar) || clock_timestamp()::varchar)::uuid::varchar
                   WHERE access_token IS NULL
               """ % {'table_name': self._table}
            self.env.cr.execute(query)


    def name_get(self):
        group_by = self.env.context.get('group_by', [])
        field_list = [fname for fname in self._name_get_fields() if fname not in group_by]
        is_calendar = self.env.context.get('organize_calendar_view', False)
        if is_calendar and self.env.context.get('organize_hide_employee', False):
            field_list.remove('employee_id')
        self = self.sudo()
        result = []
        for line in self:
            name = ' - '.join(
                [self._fields[fname].convert_to_display_name(line[fname], line) for fname in field_list if line[fname]][:3])
            if line.name:
                name = u'%s \U0001F4AC' % name

            result.append([line.id, name])
        return result


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('company_id') and vals.get('employee_id'):
                vals['company_id'] = self.env['hr.employee'].browse(vals.get('employee_id')).company_id.id
            if not vals.get('company_id'):
                vals['company_id'] = self.env.company.id
        return super().create(vals_list)


    def write(self, values):
        if any(fname in values.keys() for fname in self._get_fields_breaking_recurrency()) and not values.get(
                'recurrency_id'):
            values.update({'recurrency_id': False})
        if 'publication_warning' not in values and (set(values.keys()) & set(self._get_fields_breaking_publication())):
            values['publication_warning'] = True
        result = super(Organize, self).write(values)
        if any(key in ('repeat', 'repeat_type', 'repeat_until', 'repeat_interval') for key in values):
            for line in self:
                if line.recurrency_id and values.get('repeat') is None:
                    repeat_type = values.get('repeat_type') or line.recurrency_id.repeat_type
                    repeat_until = values.get('repeat_until') or line.recurrency_id.repeat_until
                    recurrency_values = {
                        'repeat_interval': values.get('repeat_interval') or line.recurrency_id.repeat_interval,
                        'repeat_until': repeat_until if repeat_type == 'until' else False,
                        'repeat_type': repeat_type,
                        'company_id': line.company_id.id,
                    }
                    line.recurrency_id.write(recurrency_values)
                    line.recurrency_id._delete_slot(recurrency_values.get('repeat_until'))
                    line.recurrency_id._repeat_slot()
        return result


    def action_unlink(self):
        self.unlink()
        return {'type': 'ir.actions.act_window_close'}


    def action_see_overlaping_slots(self):
        domain_map = self._get_overlap_domain()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'organize.slot',
            'name': _('Shifts in conflict'),
            'view_mode': 'gantt,list,form',
            'domain': domain_map[self.id],
            'context': {
                'initialDate': min([line.start_datetime for line in self.search(domain_map[self.id])])
            }
        }


    def action_open_employee_form(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': self.employee_id.id,
            'target': 'new',
            'view_mode': 'form'
        }


    def action_self_assign(self):
        self.ensure_one()
        if not self.check_access_rights('read', raise_exception=False):
            raise AccessError(_("You don't the right to self assign."))
        if self.employee_id:
            raise UserError(_("You can not assign yourself to an already assigned shift."))
        return self.sudo().write({'employee_id': self.env.user.employee_id.id if self.env.user.employee_id else False})


    def action_self_unassign(self):
        self.ensure_one()
        if not self.allow_self_unassign:
            raise UserError(_("The company does not allow you to self unassign."))
        if self.employee_id != self.env.user.employee_id:
            raise UserError(_("You can not unassign another employee than yourself."))
        return self.sudo().write({'employee_id': False})


    def action_create_template(self):
        values = self._prepare_template_values()
        domain = [(x, '=', values[x]) for x in values.keys()]
        existing_templates = self.env['organize.slot.template'].search(domain, limit=1)
        if not existing_templates:
            template = self.env['organize.slot.template'].create(values)
            self.write({'template_id': template.id, 'previous_template_id': template.id})
            message = _("Your template was successfully saved.")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            self.write({'template_id': existing_templates.id})


    @api.model
    def gantt_availability_check(self, start_date, end_date, scale, group_bys=None, rows=None):
        start_datetime = fields.Datetime.from_string(start_date)
        end_datetime = fields.Datetime.from_string(end_date)
        employee_ids = set()

        def tag_employee_rows(rows):
            for row in rows:
                group_bys = row.get('groupedBy')
                res_id = row.get('resId')
                if group_bys:
                    if group_bys[0] == 'employee_id' and res_id:
                        employee_id = res_id
                        employee_ids.add(employee_id)
                        row['employee_id'] = employee_id
                    elif 'employee_id' in group_bys:
                        tag_employee_rows(row.get('rows'))

        tag_employee_rows(rows)
        employees = self.env['hr.employee'].browse(employee_ids)
        leaves_mapping = employees.mapped('resource_id')._get_unavailable_intervals(start_datetime, end_datetime)
        company_leaves = self.env.company.resource_calendar_id._unavailable_intervals(
            start_datetime.replace(tzinfo=pytz.utc), end_datetime.replace(tzinfo=pytz.utc))

        def traverse(func, row):
            new_row = dict(row)
            if new_row.get('employee_id'):
                for sub_row in new_row.get('rows'):
                    sub_row['employee_id'] = new_row['employee_id']
            new_row['rows'] = [traverse(func, row) for row in new_row.get('rows')]
            return func(new_row)

        cell_dt = timedelta(hours=1) if scale in ['day', 'week'] else timedelta(hours=12)

        def inject_unavailability(row):
            new_row = dict(row)

            calendar = company_leaves
            if row.get('employee_id'):
                employee_id = self.env['hr.employee'].browse(row.get('employee_id'))
                if employee_id:
                    calendar = leaves_mapping[employee_id.resource_id.id]
            notable_intervals = filter(lambda interval: interval[1] - interval[0] >= cell_dt, calendar)
            new_row['unavailabilities'] = [{'start': interval[0], 'stop': interval[1]} for interval in notable_intervals]
            return new_row

        return [traverse(inject_unavailability, row) for row in rows]


    @api.model
    def get_unusual_days(self, date_from, date_to=None):
        employee = self.env.user.employee_id
        calendar = employee.resource_calendar_id
        if not calendar:
            return {}
        dfrom = datetime.combine(fields.Date.from_string(date_from), time.min).replace(tzinfo=pytz.utc)
        dto = datetime.combine(fields.Date.from_string(date_to), time.max).replace(tzinfo=pytz.utc)

        works = {d[0].date() for d in
                 calendar._work_intervals_batch(dfrom, dto, employee.resource_id)[employee.resource_id.id]}
        return {fields.Date.to_string(day.date()): (day.date() not in works) for day in rrule(DAILY, dfrom, until=dto)}


    @api.model
    def action_copy_previous_week(self, date_start_week, view_domain):
        date_end_copy = datetime.strptime(date_start_week, DEFAULT_SERVER_DATETIME_FORMAT)
        date_start_copy = date_end_copy - relativedelta(days=7)
        domain = [
            ('recurrency_id', '=', False),
            ('was_copied', '=', False)
        ]
        for dom in view_domain:
            if dom in ['|', '&', '!']:
                domain.append(dom)
            elif dom[0] == 'start_datetime':
                domain.append(('start_datetime', '>=', date_start_copy))
            elif dom[0] == 'end_datetime':
                domain.append(('end_datetime', '<=', date_end_copy))
            else:
                domain.append(tuple(dom))
        slots_to_copy = self.search(domain)

        new_slot_values = []
        for line in slots_to_copy:
            if not line.was_copied:
                values = line.copy_data()[0]
                if values.get('start_datetime'):
                    values['start_datetime'] = self._add_delta_with_dst(values['start_datetime'], relativedelta(days=7))
                if values.get('end_datetime'):
                    values['end_datetime'] = self._add_delta_with_dst(values['end_datetime'], relativedelta(days=7))
                values['is_published'] = False
                new_slot_values.append(values)
        result = {
            'start_date': date_start_copy,
            'end_date': date_end_copy,
            'slot_ids': []
        }
        return result

        @api.model
        def action_published_schedules(self):
            slots_to_copy = self.search([])
            new_slot_values = []
            for line in slots_to_copy:
                if line.is_published:
                    new_slot_values.append(line)
                    l = []
                    result = {
                        'start_date': self.start_datetime,
                        'end_date': self.end_datetime,
                        'slot_ids': []

                    }
                    for slot_values in new_slot_values:
                        l.append(slot_values.id)
            return l

    def date_range(self, start, end):
        delta = end - start
        days = [start + timedelta(days=i) for i in range(delta.days + 1)]
        return days

    def get_time_range(self, start, end):
        timerange = end.hour - start.hour
        time = [int(start.hour) + n for n in range(timerange)]
        return time

    def action_save(self):
        get_emloyee_time_off = self.get_employee_time_off()
        if get_emloyee_time_off:
            return {
                'name': _('Organize schedule time off'),
                'type': 'ir.actions.act_window',
                'res_model': 'organize.schedule.time.off',
                'nodestroy': True,
                'views': [(self.env.ref('organize.organize_schedule_time_off_form').id, 'form')],
                'target': 'new',
                'context': dict(
                    self.env.context,
                    organize_slot_id=self.id,
                    function="action_save"),
            }

    def employee_time_off_overlap(self, employee_time_off=None):
        if employee_time_off:
            self.is_timeoff_overlap = True
            self.timeoff_date_overlap = str(" ".join(employee_time_off))
            return True
        else:
            self.is_timeoff_overlap = False
            return False

    def _date_time_convert(self, datetime):
        current_uid = self.env.user
        tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
        datetime_rtn = datetime.strptime(str(datetime), '%Y-%m-%d %H:%M:%S').astimezone(tz)
        return datetime_rtn


    def get_employee_time_off(self):
        employee_time_off_lis = []
        hr_leave_obj = self.env['hr.leave']
        employee = self.employee_id
        start_datetime = self._date_time_convert(self.start_datetime)
        end_datetime = self._date_time_convert(self.end_datetime)
        start_date = start_datetime.date()
        start_time = start_datetime.time()
        end_date = end_datetime.date()
        end_time = end_datetime.time()
        date_range = self.date_range(start_date, end_date)
        get_time_range = self.get_time_range(start_time, end_time)
        if self.employee_id:
            employee_leave_ids = hr_leave_obj.search([('employee_id', '=', employee.id), ('state', '=', 'validate')])
            if employee_leave_ids:
                filtered_leave_ids = [employee_leave_ids.search([('request_date_from', '=', date)],limit=1) for
                                      date in date_range]
                # filtered_leave_ids = [employee_leave_ids.filtered(lambda line: line.request_date_from == date) for
                #                       date in date_range]
                for employee_time_off in filtered_leave_ids:
                    if employee_time_off:
                        if employee_time_off.request_unit_half:
                            if employee_time_off.request_date_from_period == 'am':
                                if start_time.hour < 12:
                                    employee_time_off_lis.extend([employee_time_off.duration_display, "Morning", 'on',
                                                                  str(employee_time_off.request_date_from), ','])
                                    continue
                            if employee_time_off.request_date_from_period == 'pm':
                                if end_time.hour > 12:
                                    employee_time_off_lis.extend([employee_time_off.duration_display, "Afternoon", 'on',
                                                                  str(employee_time_off.request_date_from), ','])
                                    continue
                        if not employee_time_off.request_unit_half and not employee_time_off.request_unit_hours:
                            employee_time_off_lis.extend([str(employee_time_off.request_date_from), ','])
                            continue
                        if employee_time_off.request_unit_hours:
                            requested_hour_from = employee_time_off.request_hour_from
                            if not len(requested_hour_from) <= 2:
                                requested_hour_from = requested_hour_from[:-3]
                            if int(requested_hour_from) in get_time_range:
                                employee_time_off_lis.extend(
                                    [employee_time_off.request_hour_from, '-', employee_time_off.request_hour_to, 'on',
                                     str(employee_time_off.request_date_from), ','])
                                continue
        action = self.employee_time_off_overlap(employee_time_off_lis)
        if action:
            return True
        return False

    def action_send(self):
        self.ensure_one()
        if not self.env.context.get('function') == "action_yes":
            get_emloyee_time_off = self.get_employee_time_off()
            if get_emloyee_time_off:
                return {
                    'name': _('Organize schedule time off'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'organize.schedule.time.off',
                    'nodestroy': True,
                    'views': [(self.env.ref('organize.organize_schedule_time_off_form').id, 'form')],
                    'target': 'new',
                    'context': dict(
                        self.env.context,
                        organize_slot_id=self.id,
                        function="action_send"),
                }
        if not self.employee_id or not self.employee_id.work_email:
            self.is_published = True
            domain = [('company_id', '=', self.company_id.id), ('work_email', '!=', False)]
            if self.role_id:
                domain = expression.AND([
                    domain,
                    ['|', ('organize_role_ids', '=', False), ('organize_role_ids', 'in', self.role_id.id)]])
            employee_ids = self.env['hr.employee'].sudo().search(domain)
            return self._send_slot(employee_ids, self.start_datetime, self.end_datetime)
        self._send_slot(self.employee_id, self.start_datetime, self.end_datetime)

    def action_publish(self):
        if not self.env.context.get('function') == "action_yes":
            get_emloyee_time_off = self.get_employee_time_off()
            if get_emloyee_time_off:
                return {
                    'name': _('Organize schedule time off'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'organize.schedule.time.off',
                    'nodestroy': True,
                    'views': [(self.env.ref('organize.organize_schedule_time_off_form').id, 'form')],
                    'target': 'new',
                    'context': dict(
                        self.env.context,
                        organize_slot_id=self.id,
                        function="action_publish"),
                }
        self.write({
            'is_published': True,
            'publication_warning': False,
        })

    def _add_delta_with_dst(self, start, delta):
        try:
            tz = pytz.timezone(self._get_tz())
        except pytz.UnknownTimeZoneError:
            tz = pytz.UTC
        start = start.replace(tzinfo=pytz.utc).astimezone(tz).replace(tzinfo=None)
        result = start + delta
        return tz.localize(result).astimezone(pytz.utc).replace(tzinfo=None)


    def _name_get_fields(self):
        return ['employee_id', 'role_id']


    def _get_fields_breaking_publication(self):
        return [
            'employee_id',
            'start_datetime',
            'end_datetime',
            'role_id',
        ]


    def _get_fields_breaking_recurrency(self):
        return [
            'employee_id',
            'role_id',
        ]


    @api.model
    def _get_template_fields(self):
        return {'role_id': 'role_id', 'start_time': 'start_datetime'}


    def _get_tz(self):
        return (self.env.user.tz
                or self.employee_id.tz
                or self._context.get('tz')
                or self.company_id.resource_calendar_id.tz
                or 'UTC')


    def _get_overlap_domain(self):
        domain_mapping = {}
        for line in self:
            domain_mapping[line.id] = [
                '&',
                '&',
                ('employee_id', '!=', False),
                ('employee_id', '=', line.employee_id.id),
                '&',
                ('start_datetime', '<', line.end_datetime),
                ('end_datetime', '>', line.start_datetime)
            ]
        return domain_mapping


    def _prepare_template_values(self):
        destination_tz = pytz.timezone(self._get_tz())
        start_datetime = pytz.utc.localize(self.start_datetime).astimezone(destination_tz)
        end_datetime = pytz.utc.localize(self.end_datetime).astimezone(destination_tz)
        total_seconds = (end_datetime - start_datetime).total_seconds()
        m, s = divmod(total_seconds, 60)
        h, m = divmod(m, 60)

        return {
            'start_time': start_datetime.hour + start_datetime.minute / 60.0,
            'duration': h + (m / 60.0),
            'role_id': self.role_id.id
        }


    def _read_group_employee_id(self, employees, domain, order):
        dom_tuples = [(dom[0], dom[1]) for dom in domain if isinstance(dom, list) and len(dom) == 3]
        employee_ids = self.env.context.get('filter_employee_ids', False)
        employee_domain = [('id', 'in', employee_ids)] if employee_ids else []
        all_employees = self.env['hr.employee'].search(employee_domain)
        if employee_ids or len(all_employees) < 20:
            return all_employees
        elif self._context.get('organize_expand_employee') and ('start_datetime', '<=') in dom_tuples and (
                'end_datetime', '>=') in dom_tuples:
            filters = self._expand_domain_dates(domain)
            return self.env['organize.slot'].search(filters).mapped('employee_id')
        return employees


    def _read_group_role_id(self, roles, domain, order):
        dom_tuples = [(dom[0], dom[1]) for dom in domain if isinstance(dom, list) and len(dom) == 3]
        if self._context.get('organize_expand_role') and ('start_datetime', '<=') in dom_tuples and (
                'end_datetime', '>=') in dom_tuples:
            filters = self._expand_domain_dates(domain)
            return self.env['organize.slot'].search(filters).mapped('role_id')
        return roles


    def _expand_domain_dates(self, domain):
        filters = []
        for dom in domain:
            if len(dom) == 3 and dom[0] == 'start_datetime' and dom[1] == '<=':
                max_date = dom[2] if dom[2] else datetime.now()
                max_date = max_date if isinstance(max_date, date) else datetime.strptime(max_date, '%Y-%m-%d %H:%M:%S')
                max_date = max_date + timedelta(days=30)
                filters.append((dom[0], dom[1], max_date))
            elif len(dom) == 3 and dom[0] == 'end_datetime' and dom[1] == '>=':
                min_date = dom[2] if dom[2] else datetime.now()
                min_date = min_date if isinstance(min_date, date) else datetime.strptime(min_date, '%Y-%m-%d %H:%M:%S')
                min_date = min_date - timedelta(days=30)
                filters.append((dom[0], dom[1], min_date))
            else:
                filters.append(dom)
        return filters


    def _format_start_end_datetime(self, record_env, tz=None, lang_code=False):
        destination_tz = pytz.timezone(tz)
        start_datetime = pytz.utc.localize(self.start_datetime).astimezone(destination_tz).replace(tzinfo=None)
        end_datetime = pytz.utc.localize(self.end_datetime).astimezone(destination_tz).replace(tzinfo=None)
        return (
            format_datetime(record_env, self.start_datetime, tz=tz, dt_format='short', lang_code=lang_code),
            format_datetime(record_env, self.end_datetime, tz=tz, dt_format='short', lang_code=lang_code)
        )


    def _send_slot(self, employee_ids, start_datetime, end_datetime, include_unassigned=True, message=None):
        if not include_unassigned:
            self = self.filtered(lambda s: s.employee_id)
        if not self:
            return False

        employee_with_backend = employee_ids.filtered(
            lambda e: e.user_id and e.user_id.has_group('organize.group_organize_user'))
        employee_without_backend = employee_ids - employee_with_backend
        organize = False
        if len(self) > 1 or employee_without_backend:
            organize = self.env['organize.organize'].create({
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'include_unassigned': include_unassigned,
                'slot_ids': [(6, 0, self.ids)],
            })
        if len(self) > 1:
            return organize._send_organize(message=message, employees=employee_ids)

        self.ensure_one()

        template = self.env.ref('organize.email_template_single')
        employee_url_map = {**employee_without_backend.sudo()._organize_get_url(organize),
                            **employee_with_backend._slot_get_url()}

        view_context = dict(self._context)
        view_context.update({
            'open_shift_available': not self.employee_id,
            'mail_subject': _('Organize: new open shift available'),
        })

        if self.employee_id:
            employee_ids = self.employee_id
            if self.allow_self_unassign:
                if employee_ids.filtered(lambda e: e.user_id and e.user_id.has_group('organize.group_organize_user')):
                    unavailable_link = '/organize/unassign/%s/%s' % (self.employee_id.sudo().employee_token, self.id)
                else:
                    unavailable_link = '/organize/%s/%s/unassign/%s?message=1' % (
                        organize.access_token, self.employee_id.sudo().employee_token, self.id)
                view_context.update({'unavailable_link': unavailable_link})
            view_context.update({'mail_subject': _('Organize: new shift')})

        mails_to_send_ids = []
        for employee in employee_ids.filtered(lambda e: e.work_email):
            if not self.employee_id and employee in employee_with_backend:
                view_context.update(
                    {'available_link': '/organize/assign/%s/%s' % (employee.sudo().employee_token, self.id)})
            elif not self.employee_id:
                view_context.update({'available_link': '/organize/%s/%s/assign/%s?message=1' % (
                    organize.access_token, employee.sudo().employee_token, self.id)})
            start_datetime, end_datetime = self._format_start_end_datetime(employee.env, tz=employee.tz,
                                                                           lang_code=employee.user_partner_id.lang)
            view_context.update({
                'link': employee_url_map[employee.id],
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'employee_name': employee.name,
                'work_email': employee.work_email,
            })
            mail_id = template.with_context(view_context).send_mail(self.id, notif_layout='mail.mail_notification_light')
            mails_to_send_ids.append(mail_id)

        mails_to_send = self.env['mail.mail'].sudo().browse(mails_to_send_ids)
        if mails_to_send:
            mails_to_send.send()

        self.write({
            'is_published': True,
            'publication_warning': False,
        })


    def _filter_slots_front_end(self, employee):
        return self


class OrganizeRole(models.Model):
    _name = 'organize.role'
    _description = "Organize Role"
    _order = 'sequence'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    color = fields.Integer("Color", default=0)
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    sequence = fields.Integer()


class OrganizeOrganize(models.Model):
    _name = 'organize.organize'
    _description = 'Schedule'

    @api.model
    def _default_access_token(self):
        return str(uuid.uuid4())

    start_datetime = fields.Datetime("Start Date", required=True)
    end_datetime = fields.Datetime("Stop Date", required=True)
    include_unassigned = fields.Boolean("Includes Open Shifts", default=True)
    access_token = fields.Char("Security Token", default=_default_access_token, required=True, copy=False,
                               readonly=True)
    slot_ids = fields.Many2many('organize.slot')
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)

    @api.depends('start_datetime', 'end_datetime')
    def _compute_display_name(self):
        for organize in self:
            tz = pytz.timezone(self.env.user.tz or 'UTC')
            start_datetime = pytz.utc.localize(organize.start_datetime).astimezone(tz).replace(tzinfo=None)
            end_datetime = pytz.utc.localize(organize.end_datetime).astimezone(tz).replace(tzinfo=None)
            organize.display_name = _('Organize from %s to %s') % (
                format_date(self.env, start_datetime), format_date(self.env, end_datetime))

    def _send_organize(self, message=None, employees=False):
        email_from = self.env.user.email or self.env.user.company_id.email or ''
        sent_slots = self.env['organize.slot']
        for organize in self:
            slots = organize.slot_ids
            slots_open = slots.filtered(lambda line: not line.employee_id) if organize.include_unassigned else 0
            employees = employees or slots.mapped('employee_id')
            employee_url_map = employees.sudo()._organize_get_url(organize)
            template = self.env.ref('organize.email_template_organize_organize', raise_if_not_found=False)
            template_context = {
                'slot_unassigned_count': slots_open and len(slots_open),
                'slot_total_count': slots and len(slots),
                'message': message,
            }
            if template:
                for employee in self.env['hr.employee.public'].browse(employees.ids):
                    if employee.work_email:
                        template_context['employee'] = employee
                        destination_tz = pytz.timezone(self.env.user.tz or 'UTC')
                        template_context['start_datetime'] = pytz.utc.localize(organize.start_datetime).astimezone(
                            destination_tz).replace(tzinfo=None)
                        template_context['end_datetime'] = pytz.utc.localize(organize.end_datetime).astimezone(
                            destination_tz).replace(tzinfo=None)
                        template_context['organize_url'] = employee_url_map[employee.id]
                        template_context['assigned_new_shift'] = bool(
                            slots.filtered(lambda line: line.employee_id.id == employee.id))
                        template.with_context(**template_context).send_mail(organize.id, email_values={
                            'email_to': employee.work_email, 'email_from': email_from},
                                                                            notif_layout='mail.mail_notification_light')
            sent_slots |= slots
        sent_slots.write({
            'is_published': True,
            'publication_warning': False
        })
        return True
