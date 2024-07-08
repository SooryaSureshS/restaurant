# -*- coding: utf-8 -*-
from datetime import datetime, date
from dateutil import relativedelta
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import pytz


class OrganizeAction(models.TransientModel):
   _name = 'organize.action'
   _description = "Organize Action"

   start_datetime = fields.Datetime("Start ", readonly=True)
   end_datetime = fields.Datetime("Stop Date", readonly=True)
   slot_ids = fields.Many2many('organize.slot', string="Available slots")

   @api.onchange('start_datetime')
   def change_todate(self):
      current_uid = self.env.user
      tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
      self.end_datetime = self.start_datetime + relativedelta.relativedelta(days=7)
      # start_date = datetime.strptime(str(self.start_datetime), '%Y-%m-%d %H:%M:%S').astimezone(tz)
      # end_date = datetime.strptime(str(self.end_datetime), '%Y-%m-%d %H:%M:%S').astimezone(tz)
      organize = self.env['organize.slot'].search([('start_datetime', '>=', self.start_datetime), ('end_datetime', '<=', self.end_datetime)])
      for org in organize:
         # self.write({'slot_ids': org})
         self.slot_ids += org
      return {'domain': {'slot_ids': [('start_datetime', '>=', self.start_datetime), ('end_datetime', '<=', self.end_datetime)]}}

   def action_delete(self):
      for slot in self.slot_ids:
         print(slot.employee_id.name)
         slot.unlink()