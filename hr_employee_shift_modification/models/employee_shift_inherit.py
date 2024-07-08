from odoo import models, fields, api, _


class HrEmployeeShiftInherit(models.Model):
    _inherit = 'resource.calendar'

    employee_id= fields.Many2one('hr.employee', string="Employee")

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    resource_calendar_ids = fields.Many2one('resource.calendar', 'Working Hours',compute='_compute_practical_amount')

    def _compute_practical_amount(self):
        for line in self:
            employee_shift = self.env['resource.calendar'].search([('employee_id.id','=',line.id)],limit=1)
            if employee_shift:
                for x in employee_shift:
                    line.resource_calendar_ids = x.id
            else:
                line.resource_calendar_ids = False



