# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from datetime import datetime
from datetime import  date
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError


class HrEmployeeInherited(models.Model):
    _inherit = 'hr.employee'

    resource_calendar_ids = fields.Many2one('resource.calendar', 'Working Hours',)
    availability = fields.Boolean(compute='search_time_off')
    qualification = fields.Boolean()



    def search_time_off(self):
        current_date = datetime.now()
        for rec in self:
            time_off = self.env['hr.leave'].search([('employee_id', '=', rec.id),
                                                    ('request_date_from', '<=', current_date),
                                                    ('request_date_to', '>=', current_date),
                                                    ('state', '=', 'validate')])
            if time_off:
                rec.availability = False
                if rec.availability == False:
                    if rec.name:
                        if rec.availability == False:
                            name_u = rec.name.split(" ")
                            if name_u[-1] == "(U)":
                                pass
                            else:
                                rec.name = rec.name + " (U)"
                        if rec.availability == True:
                            name_u = rec.name.split(" ")
                            if name_u[-1] == "(U)":
                                rec.name = (" ").join(name_u[:-1])
            else:
                rec.availability = True
                if rec.availability == True:
                    name_u = rec.name.split(" ")
                    if name_u[-1] == "(U)":
                        rec.name = (" ").join(name_u[:-1])

    def choose_employee(self):

        employee_id = self.env.context.get('active_id')
        if len(self.env.context.get('active_ids')) >= 2:
            raise ValidationError('You can only choose one employee at a time')
        else:
            contract_id = self.env['hr.contract'].search([('id', '=', self.env.context.get('contract_id'))])
            po = contract_id.write({'employee_id': employee_id})
            self.env.cr.commit()





class HrEmployeeShift(models.Model):
    _inherit = 'resource.calendar'

    def _get_default_attendance_ids(self):
        return [
            (0, 0, {'name': _('Monday Morning'), 'dayofweek': '0', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': _('Tuesday Morning'), 'dayofweek': '1', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': _('Wednesday Morning'), 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': _('Thursday Morning'), 'dayofweek': '3', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': _('Friday Morning'), 'dayofweek': '4', 'hour_from': 8, 'hour_to': 12}),
        ]

    color = fields.Integer(string='Color Index', help="Color")
    hr_department = fields.Many2one('hr.department', string="Department", help="Department")
    sequence = fields.Integer(string="Sequence", required=True, default=1, help="Sequence")
    attendance_ids = fields.One2many(
        'resource.calendar.attendance', 'calendar_id', 'Workingssss Time',
        copy=True, default=_get_default_attendance_ids)

    @api.constrains('sequence')
    def validate_seq(self):
        if self.hr_department.id:
            record = self.env['resource.calendar'].search([('hr_department', '=', self.hr_department.id),
                                                           ('sequence', '=', self.sequence),
                                                           ('company_id', '=', self.company_id.id)
                                                           ])
            if len(record) > 1:
                raise ValidationError("One record with same sequence is already active."
                                      "You can't activate more than one record  at a time")


