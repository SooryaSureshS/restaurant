# -*- coding: utf-8 -*-
from datetime import date, datetime
import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class XeroEarnings(models.Model):
    _name = 'xero.earnings.rates'

    earnings_rate_id = fields.Char(store=True)
    name = fields.Char(store=True)
    earnings_type = fields.Char(store=True)


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    xero_leave_type_id = fields.Char()

    def set_employees_leave_to_odoo(self, leave_type, xero, company_id=False, options=None):
        leave_type_lst = []
        leave_type = xero.json_load_object_hook(leave_type)
        leave_type_lst = leave_type.get('LeaveTypes')
        if leave_type_lst:
            for type in leave_type_lst:
                existing_type = self.env['hr.leave.type'].search([('xero_leave_type_id', '=', type.get('LeaveTypeID'))])
                if not existing_type:
                    if type.get('TypeOfUnits') == 'Hours':
                        unit = 'hour'
                    type = self.create({
                        'xero_leave_type_id': type.get('LeaveTypeID'),
                        'name': type.get('Name'),
                        'request_unit': unit,
                        'responsible_id': self.env.uid,
                    })

        else:
            return
        earnings_rate_lst = leave_type.get('EarningsRates')
        if earnings_rate_lst:
            for earnings in earnings_rate_lst:
                existing_earnings_details = self.env['xero.earnings.rates'].search([('earnings_rate_id', '=', earnings.get('EarningsRateID'))])
                if not existing_earnings_details:
                    earnings_details = self.env['xero.earnings.rates'].create({
                        'earnings_rate_id':earnings.get('EarningsRateID'),
                        'name':earnings.get('Name'),
                        'earnings_type':earnings.get('EarningsType'),
                    })
        else:
            return
class HrLeaveApp(models.Model):
    _inherit = 'hr.leave'

    xero_leave_app_id = fields.Char()

    def set_employees_leave_app_to_odoo(self, leave, xero, company_id=False, options=None):
        for emp_leave in leave:
            emp_leave = xero.json_load_object_hook(emp_leave)
            existing_leave = self.env['hr.leave'].search(
                [('xero_leave_app_id', '=', emp_leave.get('LeaveApplicationID'))])
            if not existing_leave:
                emp = self.env['hr.employee'].search([('xero_employee_id', '=', str(emp_leave.get('EmployeeID')))])
                if emp:
                    for i in emp_leave.get('LeavePeriods'):
                        i = xero.json_load_object_hook(i)
                        type = self.env['hr.leave.type'].search(
                            [('xero_leave_type_id', '=', emp_leave.get('LeaveTypeID'))])
                        leave_id = self.create([{
                            'holiday_status_id': type.id,
                            'xero_leave_app_id': emp_leave.get('LeaveApplicationID'),
                            'request_date_from': i.get('PayPeriodStartDate'),
                            'request_date_to': i.get('PayPeriodEndDate'),
                            'employee_id': emp.id,
                            # 'department_id':existing_dep,
                        }])
                        if i.get('PayRunStatus') == 'PROCESSED':
                            leave_id.write({'state': 'validate'})
                            # contract.state = 'open'
                        else:
                            leave_id.write({'state': 'confirm'})
                else:
                    return
