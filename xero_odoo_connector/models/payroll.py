# -*- coding: utf-8 -*-
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip.run'

    xero_payrun_id = fields.Char()

    def set_employees_payrun_list_to_odoo(self, emp_payslip, tot_payslips, xero, company_id=False, options=None):
        worked_hrs = []
        input_data = []
        for xero_payslip in emp_payslip:
            xero_payslip = xero.json_load_object_hook(xero_payslip)
            batch_id = self.create([{
                'xero_payrun_id': xero_payslip.get('PayRunID'),
                'name': 'Payslip Batch For ' + xero_payslip.get('PayRunPeriodStartDate').strftime('%B')
                        + ' ' + str(xero_payslip.get('PayRunPeriodStartDate').year),
                'date_start': xero_payslip.get('PayRunPeriodStartDate'),
                'date_end': xero_payslip.get('PayRunPeriodEndDate')
            }])

            for data in xero_payslip.get('Payslips'):
                for xero_total_payslip in tot_payslips:
                    xero_total_payslip = xero.json_load_object_hook(xero_total_payslip)
                    if data.get('EmployeeID') == xero_total_payslip.get('Payslip').get('EmployeeID') and data.get(
                            'PayslipID') == xero_total_payslip.get('Payslip').get('PayslipID'):
                        sal_structure = self.env['hr.payroll.structure'].search([('code', '=', 'BASE')])
                        emp = self.env['hr.employee'].search(
                            [('xero_employee_id', '=', str(data.get('EmployeeID')))])
                        dep = self.env['hr.department'].search([('name', '=', 'Sales')])
                        if emp:
                            contract = self.env['hr.contract'].create([{
                                'name': (data.get('FirstName') or u'') + ' ' + (
                                        data.get('LastName') or u'') + ' ' + 'Contract',
                                'employee_id': emp.id,
                                'struct_id': sal_structure.id,
                                'wage': data.get('Wages'),
                                'department_id': dep.id
                            }])

                            if xero_payslip.get('PayRunStatus') == 'POSTED':
                                contract.write({'state': 'open'})
                            else:
                                contract.write({'state': 'draft'})
                        generate_payslip = self.env['hr.payslip.employees']
                        contract_ids = self.env['hr.contract'].search([('state', '=', 'open')])
                        if contract_ids:
                            employee_ids = []
                            for line in contract_ids:
                                employee_ids.append(line.employee_id)
                                generate_payslip.create({
                                    'employee_ids': [(4, line.employee_id.id)]
                                })
                                # generate_payslip.create([{
                                #         'name': line.employee_id.name,
                                #         'work_phone': line.employee_id.work_phone or None,
                                #         'work_email': line.employee_id.work_email or None,
                                #         'department_id': line.employee_id.department_id or None,
                                #         'job_id': line.employee_id.job_id or None,
                                #         'parent_id': line.employee_id.parent_id.name or None,
                                # }])
                                print(generate_payslip)
                            payslips = self.env['hr.payslip']
                            [run_data] = batch_id.read(
                                ['date_start', 'date_end', 'credit_note'])
                            from_date = run_data.get('date_start')
                            to_date = run_data.get('date_end')
                            if not employee_ids:
                                raise UserError(_("You must select employee(s) to generate payslip(s)."))
                            for employee in employee_ids:
                                slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id,
                                                                                        contract_id=False)
                                res = {
                                    'employee_id': employee.id,
                                    'name': slip_data['value'].get('name'),
                                    'struct_id': sal_structure.id,
                                    'contract_id': contract.id,
                                    'payslip_run_id': batch_id.id,
                                    'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                                    'worked_days_line_ids': [
                                        (0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                                    'date_from': from_date,
                                    'date_to': to_date,
                                    'credit_note': run_data.get('credit_note'),
                                    'company_id': employee.company_id.id,
                                }
                                payslips += self.env['hr.payslip'].create(res)

                                for i in xero_total_payslip.get('Payslip').get('EarningsLines'):
                                    existing_earnings_details = self.env['xero.earnings.rates'].search(
                                        [('earnings_rate_id', '=', i.get('EarningsRateID'))])
                                    working_hrs = {
                                        'payslip_id': payslips.id,
                                        'sequence': 10,
                                        'name': existing_earnings_details.name,
                                        'code': existing_earnings_details.id,
                                        'number_of_hours': i.get('NumberOfUnits'),
                                        'contract_id': contract.id
                                    }

                                    worked_hrs.append(working_hrs)
                                    input_details = {
                                        'payslip_id': payslips.id,
                                        'sequence': 10,
                                        'name': existing_earnings_details.name,
                                        'code': existing_earnings_details.id,
                                        'amount': i.get('RatePerUnit'),
                                        'contract_id': contract.id

                                    }
                                    input_data.append(input_details)
                                self.env['hr.payslip.worked_days'].create(worked_hrs)
                                self.env['hr.payslip.input'].create(input_data)
                            payslips.compute_sheet()
                            contract_ids.write({'state': 'cancel'})
                        # return {'type': 'ir.actions.act_window_close'}
