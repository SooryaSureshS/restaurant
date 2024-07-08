# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class OrganizeSend(models.TransientModel):
   _name = 'organize.send'
   _description = "Send Organize"

   @api.model
   def default_get(self, default_fields):
       res = super().default_get(default_fields)
       if 'slot_ids' in res and 'employee_ids' in default_fields:
           res['employee_ids'] = self.env['organize.slot'].browse(res['slot_ids'][0][2]).mapped('employee_id.id')
       return res

   start_datetime = fields.Datetime("Period", required=True)
   end_datetime = fields.Datetime("Stop Date", required=True)
   include_unassigned = fields.Boolean("Include Open Shifts", default=True)
   note = fields.Text("Extra Message")
   employee_ids = fields.Many2many('hr.employee', string="Employees",compute='_compute_slots_data', inverse='_inverse_employee_ids', store=True)
   slot_ids = fields.Many2many('organize.slot', compute='_compute_slots_data', store=True)

   @api.depends('start_datetime', 'end_datetime')
   def _compute_slots_data(self):
       for wiz in self:
           wiz.slot_ids = self.env['organize.slot'].search([('start_datetime', '>=', wiz.start_datetime),
                                                            ('end_datetime', '<=', wiz.end_datetime)])
           wiz.employee_ids = wiz.slot_ids.mapped('employee_id')

   def _inverse_employee_ids(self):
       for wiz in self:
           wiz.slot_ids = self.env['organize.slot'].search([('start_datetime', '>=', wiz.start_datetime),
                                                            ('start_datetime', '<=', wiz.end_datetime)])



   def action_send(self):
       if not self.employee_ids:
           raise UserError(_('Select the employees you would like to send the organize to.'))
       if self.include_unassigned:
           slot_to_send = self.slot_ids.filtered(lambda s: not s.employee_id or s.employee_id in self.employee_ids)
       else:
           slot_to_send = self.slot_ids.filtered(lambda s: s.employee_id in self.employee_ids)
       if not slot_to_send:
           raise UserError(_('This action is not allowed as there are no shifts planned for the selected time period.'))
       organize = self.env['organize.organize'].create({
           'start_datetime': self.start_datetime,
           'end_datetime': self.end_datetime,
           'include_unassigned': self.include_unassigned,
           'slot_ids': [(6, 0, slot_to_send.ids)],
       })
       slot_employees = slot_to_send.mapped('employee_id')
       open_slots = slot_to_send.filtered(lambda s: not s.employee_id and not s.is_past)
       employees_to_send = self.env['hr.employee']
       for employee in self.employee_ids:
           if employee in slot_employees:
               employees_to_send |= employee
           else:
               for slot in open_slots:
                   if not employee.organize_role_ids or not slot.role_id or slot.role_id in employee.organize_role_ids:
                       employees_to_send |= employee
       return organize._send_organize(message=self.note, employees=employees_to_send)

   def action_publish(self):
       slot_to_publish = self.slot_ids
       if not self.include_unassigned:
           slot_to_publish = slot_to_publish.filtered(lambda s: s.employee_id)
       slot_to_publish.write({
           'is_published': True,
           'publication_warning': False
       })
       return True


class SlotOrganizeSelectSend(models.TransientModel):
   _name = 'slot.organize.select.send'
   _description = "Select Employees and Send One Slot"

   @api.model
   def default_get(self, default_fields):
       res = super().default_get(default_fields)
       if 'employee_ids' in default_fields and res.get('slot_id') and 'employee_ids' not in res:
           slot = self.env['organize.slot'].browse(res['slot_id'])
           if slot:
               domain = [('company_id', '=', slot.company_id.id), ('work_email', '!=', False)]
               if slot.role_id:
                   domain = expression.AND([domain,
                       ['|', ('organize_role_ids', '=', False), ('organize_role_ids', 'in', slot.role_id.id)]])
               res['employee_ids'] = self.env['hr.employee'].sudo().search(domain).ids
       return res

   slot_id = fields.Many2one('organize.slot', "Shifts", required=True, readonly=True)
   company_id = fields.Many2one('res.company', related='slot_id.company_id')
   employee_ids = fields.Many2many('hr.employee', required=True, check_company=True, domain="[('work_email', '!=', False)]")

   def action_send(self):
       if self.slot_id.is_past and not self.slot_id.employee_id:
           raise UserError(_('You cannot send a past unassigned slot'))
       return self.slot_id._send_slot(self.employee_ids, self.slot_id.start_datetime, self.slot_id.end_datetime)