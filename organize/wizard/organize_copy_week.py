# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta, time
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import format_date, format_datetime
import pytz
import datetime
import calendar
from datetime import datetime

class OrganizeCopyWeek(models.TransientModel):
    _name = 'organize.copy.week'
    _description = "Copy Organize"

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        if 'slot_ids' in res and 'employee_ids' in default_fields:
            res['employee_ids'] = self.env['organize.slot'].browse(res['slot_ids'][0][2]).mapped('employee_id.id')
        return res

    start_datetime = fields.Datetime("Period", required=True)
    start_datetime1 = fields.Datetime("Select the week to copy", required=True)
    end_datetime = fields.Datetime("Stop Date", required=True)
    end_datetime1 = fields.Datetime("Stop Date Time", default=fields.Datetime.today())
    include_unassigned = fields.Boolean("Include Open Shifts", default=True)
    employee_ids = fields.Many2many('hr.employee', string="Employees", compute='_compute_slots_data',
                                    inverse='_inverse_employee_ids', store=True)
    slot_ids = fields.Many2many('organize.slot', string="Available slots")

    @api.onchange('start_datetime', 'end_datetime')
    def compute_date(self):
        # current_uid = self.env.user
        # tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
        # start_correct = datetime.strptime(start_date, '%Y-%m-%d').astimezone(tz)
        # start_date = datetime.strptime(str(self.start_datetime),'%Y-%m-%d %H:%M:%S').astimezone(tz)
        # end_date = datetime.strptime(str(self.end_datetime),  '%Y-%m-%d %H:%M:%S').astimezone(tz)
        return {'domain': {'slot_ids': [('start_datetime', '>=', self.start_datetime), ('end_datetime', '<=', self.end_datetime)]}}

    @api.depends('start_datetime', 'end_datetime')
    def compute_slots_data(self):
        for wiz in self:

            wiz.slot_ids = self.env['organize.slot'].search([('start_datetime', '>=', wiz.start_datetime),
                                                             ('end_datetime', '<=', wiz.end_datetime)])
            wiz.employee_ids = wiz.slot_ids.mapped('employee_id')

    def _inverse_employee_ids(self):
        for wiz in self:
            wiz.slot_ids = self.env['organize.slot'].search([('start_datetime', '>=', wiz.start_datetime),
                                                             ('start_datetime', '<=', wiz.end_datetime)])

    def action_send(self):
        date_start_copy = self.convert_datetime_zone(self.start_datetime1)
        org_slot = self.env['organize.slot']
        slots_to_copy = self.slot_ids
        new_slot_values = []
        for line in slots_to_copy:
            values = line.copy_data()[0]
            if values.get('start_datetime'):
                next_start_date = self.get_next_week_start_date(values.get('start_datetime'),
                                                                    date_start_copy)
            if values.get('end_datetime'):
                next_end_date =self.get_next_end_week_date(values.get('start_datetime'), values.get('end_datetime'),
                                                                    next_start_date)
            values['start_datetime'] = next_start_date - relativedelta(hours=5, minutes=30)
            values['end_datetime'] = next_end_date - relativedelta(hours=5, minutes=30)
            values['is_published'] = False
            new_slot_values.append(values)
        slots_to_copy.write({'was_copied': True})
        copy_org_slot = org_slot.create(new_slot_values)
        for rec in copy_org_slot:
            rec.get_employee_time_off()
        return copy_org_slot

    def get_next_week_start_date(self, prev_start_date, week_start_date):
        previous_date = self.convert_datetime_zone(prev_start_date)
        if week_start_date.isoweekday() == 7:
            week_start_date  = week_start_date + relativedelta(days=1)
        next_count = previous_date.isoweekday() - week_start_date.isoweekday()
        nxt_copy_date = week_start_date.date() + relativedelta(days=next_count)
        return datetime.combine(nxt_copy_date, previous_date.time())

    def get_next_end_week_date(self, start_date, end_date, nxt_start_date):
        previous_start_date = self.convert_datetime_zone(start_date)
        previous_end_date = self.convert_datetime_zone(end_date)
        days_count = (previous_end_date - previous_start_date).days
        nxt_end_date = nxt_start_date.date() + relativedelta(days=days_count)
        return datetime.combine(nxt_end_date, previous_end_date.time())

    def convert_datetime_zone(self, datetime_to_cvrt):
        current_uid = self.env.user
        tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
        cnvrt_datetime = datetime.strptime(str(datetime_to_cvrt), '%Y-%m-%d %H:%M:%S').astimezone(tz).replace(tzinfo=None)
        return cnvrt_datetime

    def _add_delta_with_dst(self, start, delta):
        try:
            tz = pytz.timezone(self._get_tz())
        except pytz.UnknownTimeZoneError:
            tz = pytz.UTC
        start = start.replace(tzinfo=pytz.utc).astimezone(tz).replace(tzinfo=None)
        result = start + delta
        return tz.localize(result).astimezone(pytz.utc).replace(tzinfo=None)

    def action_publish(self):
        slot_to_publish = self.slot_ids
        if not self.include_unassigned:
            slot_to_publish = slot_to_publish.filtered(lambda s: s.employee_id)
        slot_to_publish.write({
            'is_published': True,
            'publication_warning': False
        })
        return True

    def _get_tz(self):
        return (self.env.user.tz
                or self.employee_id.tz
                or self._context.get('tz')
                or self.company_id.resource_calendar_id.tz
                or 'UTC')
