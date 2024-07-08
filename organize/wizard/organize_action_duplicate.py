# -*- coding: utf-8 -*-
from datetime import datetime, date
from dateutil import relativedelta
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import pytz
from odoo.osv import expression


class OrganizeActionDuplicate(models.TransientModel):
   _name = 'organize.action.duplicate'
   _description = "Organize Duplicate"

   start_datetime = fields.Datetime("Start ", readonly=True)
   end_datetime = fields.Datetime("Stop Date", readonly=True)
   slot_ids = fields.Many2many('organize.slot', string="Available slots")

   @api.onchange('start_datetime')
   def change_todate(self):
      current_uid = self.env.user
      tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
      self.end_datetime = self.start_datetime + relativedelta.relativedelta(days=7)
      start_date = datetime.strptime(str(self.start_datetime), '%Y-%m-%d %H:%M:%S').astimezone(tz)
      end_date = datetime.strptime(str(self.end_datetime), '%Y-%m-%d %H:%M:%S').astimezone(tz)
      organize = self.env['organize.slot'].search([('start_datetime', '>=', self.start_datetime), ('end_datetime', '<=', self.end_datetime)])
      organize2 = self.env['organize.slot'].search([('start_datetime', '<=', self.start_datetime), ('end_datetime', '>=', self.end_datetime)])
      for org in organize:
         self.slot_ids += org
      for org in organize2:
         self.slot_ids += org
      return {'domain': {'slot_ids': [('start_datetime', '>=', self.start_datetime), ('end_datetime', '<=', self.start_datetime)]}}

   def action_duplicate(self):
      for slot in self.slot_ids:
         data = [{
            'previous_template_id': slot.previous_template_id if slot.previous_template_id else False,
            'template_reset': slot.template_reset if slot.template_reset else False,
            'template_id': slot.template_id if slot.template_id else False,
            'employee_id': slot.employee_id.id if slot.employee_id.id else False,
            'role_id': slot.role_id.id if slot.role_id.id else False,
            'company_id': slot.company_id.id if slot.company_id.id else False,
            'start_datetime': slot.start_datetime if slot.start_datetime else False,
            'end_datetime': slot.end_datetime if slot.end_datetime else False,
            'allocated_percentage': slot.allocated_percentage if slot.allocated_percentage else False,
            'allocated_hours': slot.allocated_hours if slot.allocated_hours else False,
            'repeat': slot.repeat if slot.repeat else False,
            'repeat_interval': slot.repeat_interval if slot.repeat_interval else False,
            'repeat_type': slot.repeat_type if slot.repeat_type else False,
            'repeat_until': slot.repeat_until if slot.repeat_until else False,
            'name': slot.name if slot.name else False,

         }]
         new = self.env['organize.slot'].create(data)