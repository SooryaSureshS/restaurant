from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _


class HrAcessesLevel(models.Model):
    _name = 'hr.acceses.level'
    _rec_name = "acceses_level"

    acceses_level = fields.Char(string="Access Level")


class HrPayrollID(models.Model):
    _name = 'hr.payroll.id'
    _rec_name = "payroll"

    payroll = fields.Char(string="Payroll ID")


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    deputy_acesses = fields.Many2one('hr.acceses.level', string="Access Level")
    works_at = fields.Many2one('hubster.store', string="Works at")
    hired_on = fields.Date(string="Hired On")
    training = fields.Many2one('project.task', string="Add Training")
    employment_type = fields.Many2one('hr.contract', string="Employment Type")
    payroll_id = fields.Many2one('hr.payroll.id', string="Payroll ID")
    default_pay_rate = fields.Char(string="Pay rate(Default)")
    base_pay_rate = fields.Float(string="Base rate")
    pay_rates = fields.Char('Pay rates', compute='get_payrates')

    def get_payrates(self):
        for rec in self:
            if rec.default_pay_rate:
                default_pay_rate = str(rec.default_pay_rate)
            else:
                default_pay_rate = "Not mentioned"
            if rec.base_pay_rate:
                base_pay_rate = str(rec.base_pay_rate)
            else:
                base_pay_rate = "0.00"
            rec.pay_rates = default_pay_rate + base_pay_rate


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    attendance_salary = fields.Float(string="Salary",compute='onchange_employee_dates',readonly=True)

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee_dates(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        base_pay = self.employee_id.base_pay_rate
        week_attendance = self.env['hr.attendance'].search(
            [('check_in', '>=', self.date_from),
             ('check_in', '<=', self.date_to),
             ('employee_id', '=', self.employee_id.id)]).mapped('worked_hours')
        print(week_attendance,"week attendanceeeee")
        if week_attendance:
            self.attendance_salary = sum(week_attendance) * base_pay
        else:
            self.attendance_salary = 0

