# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from datetime import datetime
from datetime import  date
from datetime import timedelta


class EmployeeTimesheetApprovalView(models.Model):
    _name = 'timesheet.approval'

    employee_id = fields.Many2one('hr.employee', string="Employee" ,states={'publish': [('readonly', True)]})
    scheduled_hours = fields.Float(string="Scheduled Hours" ,states={'publish': [('readonly', True)]})
    timesheet_hours = fields.Float(string="Timesheet Hours" ,states={'publish': [('readonly', True)]})
    hour_variance = fields.Float(string="Hour variance" ,states={'publish': [('readonly', True)]})
    scheduled_cost = fields.Float(string="Scheduled Cost" ,states={'publish': [('readonly', True)]})
    timesheet_wages = fields.Float(string="Timesheet Wages" ,states={'publish': [('readonly', True)]})
    cost_variance = fields.Float(string="Cost Variance" ,states={'publish': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('publish', 'Published'),
    ], 'Status', default='draft' ,readonly=True)
    attendance_id = fields.Integer(string="Attendance Id" ,states={'publish': [('readonly', True)]})



    @api.model
    def timesheet_data_creation(self):
        current_date = datetime.now()
        today = datetime.strftime(current_date, '%d-%m-%Y')

        attendance_details = self.env['hr.attendance'].search([])
        current_attandance = attendance_details.filtered(
            lambda line: datetime.strftime(line.create_date , '%d-%m-%Y') == today and line.check_out != False)

        if current_attandance:
            for entries in current_attandance:

                scheduled_cost =entries.employee_id.contract_id.resource_calendar_id.hours_per_day * entries.employee_id.timesheet_cost
                timesheet_wages = entries.worked_hours * entries.employee_id.timesheet_cost
                hour_variance = entries.employee_id.contract_id.resource_calendar_id.hours_per_day - entries.worked_hours
                cost_variance = scheduled_cost - timesheet_wages
                value = {
                'employee_id': entries.employee_id.id,
                'scheduled_hours':entries.employee_id.contract_id.resource_calendar_id.hours_per_day,
                'timesheet_hours': entries.worked_hours,
                'hour_variance':hour_variance,
                'scheduled_cost':scheduled_cost,
                'timesheet_wages':timesheet_wages,
                'cost_variance':cost_variance,
                'attendance_id':entries.id
                }

                timesheet_data_check = self.env['timesheet.approval'].search([('attendance_id','=',entries.id)])
                if timesheet_data_check:
                    pass
                else:

                    timesheet=self.env['timesheet.approval'].create(value)



    def action_publish(self):
        current_date = datetime.now()
        today = datetime.strftime(current_date, '%d-%m-%Y')
        selected_ids = self.env.context.get('active_ids')
        records = self.env['timesheet.approval'].browse(selected_ids)
        current_timesheet = records.filtered(
            lambda line: line.state == 'draft')
        for x in current_timesheet:
            x.state = 'publish'
        return self.env.ref('employee_shift_approval.report_timesheet_summary').report_action(self)

class TimesheetData(models.AbstractModel):
    _name = 'report.employee_shift_approval.report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        current_date = datetime.now()
        today = datetime.strftime(current_date, '%d-%m-%Y')
        datas = self.env['timesheet.approval'].search([('state', '=', 'publish'), ('id', '=', docids)])
        todays_data = datas.filtered(
            lambda line: datetime.strftime(line.create_date, '%d-%m-%Y') == today or line.state == 'publish')
        docs = todays_data
        return {
        'docs': docs,

        }


