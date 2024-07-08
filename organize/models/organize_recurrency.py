# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models, _
from odoo.tools import get_timedelta
from odoo.exceptions import ValidationError
import uuid


class OrganizeRecurrency(models.Model):
   _name = 'organize.recurrency'
   _description = "Organize Recurrence"

   slot_ids = fields.One2many('organize.slot', 'recurrency_id', string="Related Organizing Entries")
   repeat_interval = fields.Integer("Repeat Every", default=1, required=True)
   repeat_type = fields.Selection([('forever', 'Forever'), ('until', 'Until')], string='Weeks', default='forever')
   repeat_until = fields.Datetime(string="Repeat Until")
   last_generated_end_datetime = fields.Datetime("Last Generated End Date", readonly=True)
   company_id = fields.Many2one('res.company', string="Company", readonly=True, required=True, default=lambda self: self.env.company)

   _sql_constraints = [
       ('check_repeat_interval_positive', 'CHECK(repeat_interval >= 1)', 'Recurrency repeat interval should be at least 1'),
       ('check_until_limit', "CHECK((repeat_type = 'until' AND repeat_until IS NOT NULL) OR (repeat_type != 'until'))", 'A recurrence repeating itself until a certain date must have its limit set'),
   ]

   @api.constrains('company_id', 'slot_ids')
   def _check_multi_company(self):
       for recurrency in self:
           if any(recurrency.company_id != organize.company_id for organize in recurrency.slot_ids):
               raise ValidationError(_('An shift must be in the same company as its recurrency.'))

   def name_get(self):
       result = []
       for recurrency in self:
           if recurrency.repeat_type == 'forever':
               name = _('Forever, every %s week(s)') % (recurrency.repeat_interval,)
           else:
               name = _('Every %s week(s) until %s') % (recurrency.repeat_interval, recurrency.repeat_until)
           result.append([recurrency.id, name])
       return result

   @api.model
   def _cron_schedule_next(self):
       companies = self.env['res.company'].search([])
       now = fields.Datetime.now()
       stop_datetime = None
       for company in companies:
           delta = get_timedelta(company.organize_generation_interval, 'month')

           recurrencies = self.search([
               '&',
               '&',
               ('company_id', '=', company.id),
               ('last_generated_end_datetime', '<', now + delta),
               '|',
               ('repeat_until', '=', False),
               ('repeat_until', '>', now - delta),
           ])
           recurrencies._repeat_slot(now + delta)

   def _repeat_slot(self, stop_datetime=False):
       OrganizeSlot = self.env['organize.slot']
       for recurrency in self:
           slot = OrganizeSlot.search([('recurrency_id', '=', recurrency.id)], limit=1, order='start_datetime DESC')

           if slot:
               recurrence_end_dt = False
               if recurrency.repeat_type == 'until':
                   recurrence_end_dt = recurrency.repeat_until

               if not stop_datetime:
                   stop_datetime = fields.Datetime.now() + get_timedelta(recurrency.company_id.organize_generation_interval, 'month')
               range_limit = min([dt for dt in [recurrence_end_dt, stop_datetime] if dt])

               recurrency_delta = get_timedelta(recurrency.repeat_interval, 'week')
               next_start = OrganizeSlot._add_delta_with_dst(slot.start_datetime, recurrency_delta)

               slot_values_list = []
               while next_start < range_limit:
                   slot_values = slot.copy_data({
                       'start_datetime': next_start,
                       'end_datetime': next_start + (slot.end_datetime - slot.start_datetime),
                       'recurrency_id': recurrency.id,
                       'company_id': recurrency.company_id.id,
                       'repeat': True,
                       'is_published': False
                   })[0]
                   slot_values_list.append(slot_values)
                   next_start = OrganizeSlot._add_delta_with_dst(next_start, recurrency_delta)

               if slot_values_list:
                   OrganizeSlot.create(slot_values_list)
                   recurrency.write({'last_generated_end_datetime': slot_values_list[-1]['start_datetime']})

           else:
               recurrency.unlink()

   def _delete_slot(self, start_datetime):
       slots = self.env['organize.slot'].search([
           ('recurrency_id', 'in', self.ids),
           ('start_datetime', '>=', start_datetime),
           ('is_published', '=', False),
       ])
       slots.unlink()


class Employee(models.Model):
   _inherit = "hr.employee"

   def _default_employee_token(self):
       return str(uuid.uuid4())

   default_organize_role_id = fields.Many2one('organize.role', string="Default Organize Role", groups='hr.group_hr_user')
   organize_role_ids = fields.Many2many('organize.role', string="Organizing Roles", groups='hr.group_hr_user', compute='_compute_organize_role_ids', store=True, readonly=False)
   employee_token = fields.Char('Security Token', default=_default_employee_token, copy=False, groups='hr.group_hr_user', readonly=True)

   _sql_constraints = [
       ('employee_token_unique', 'unique(employee_token)', 'Error: each employee token must be unique')
   ]

   def _init_column(self, column_name):
       if column_name == "employee_token":
           self.env.cr.execute("SELECT id FROM %s WHERE employee_token IS NULL" % self._table)
           acc_ids = self.env.cr.dictfetchall()
           query_list = [{'id': acc_id['id'], 'employee_token': self._default_employee_token()} for acc_id in acc_ids]
           query = 'UPDATE ' + self._table + ' SET employee_token = %(employee_token)s WHERE id = %(id)s;'
           self.env.cr._obj.executemany(query, query_list)
       else:
           super(Employee, self)._init_column(column_name)

   def _organize_get_url(self, organize):
       result = {}
       for employee in self:
           if employee.user_id and employee.user_id.has_group('organize.group_organize_user'):
               result[employee.id] = '/web?#action=organize.organize_action_open_shift'
           else:
               result[employee.id] = '/organize/%s/%s' % (organize.access_token, employee.employee_token)
       return result

   def _slot_get_url(self):
       action_id = self.env.ref('organize.organize_action_open_shift').id
       menu_id = self.env.ref('organize.organize_menu_root').id
       dbname = self.env.cr.dbname or [''],
       link = "/web?#action=%s&model=organize.slot&menu_id=%s&db=%s" % (action_id, menu_id, dbname[0])
       return {employee.id: link for employee in self}

   def action_view_organize(self):
       action = self.env["ir.actions.actions"]._for_xml_id("organize.organize_action_schedule_by_employee")
       action.update({
           'name': _('View Organize'),
           'domain': [('employee_id', 'in', self.ids)],
           'context': {
               'search_default_group_by_employee': True,
               'filter_employee_ids': self.ids,
               'hide_open_shift': True,
           }
       })
       return action

   @api.depends('default_organize_role_id')
   def _compute_organize_role_ids(self):
       for employee in self.filtered(lambda s: s.organize_role_ids is None):
           employee.organize_role_ids = False

       for employee in self.filtered(lambda s: s.default_organize_role_id):
           if employee.default_organize_role_id and employee.default_organize_role_id not in employee.organize_role_ids:
               employee.organize_role_ids |= employee.default_organize_role_id

   def write(self, vals):
       res = super(Employee, self).write(vals)

       if 'default_organize_role_id' in vals or 'organize_role_ids' in vals:
           self.env.add_to_compute(self._fields['organize_role_ids'], self)

       return res


class Company(models.Model):
   _inherit = 'res.company'

   organize_generation_interval = fields.Integer("Rate Of Shift Generation", required=True, readonly=False, default=6)
   organize_allow_self_unassign = fields.Boolean("Can Employee Un-Assign Themselves?", default=False)


class ResConfigSettings(models.TransientModel):
   _inherit = 'res.config.settings'

   organize_generation_interval = fields.Integer("Rate Of Shift Generation", required=True,
       related="company_id.organize_generation_interval", readonly=False)

   organize_allow_self_unassign = fields.Boolean("Allow Unassignment", default=False, readonly=False,
       related="company_id.organize_allow_self_unassign")