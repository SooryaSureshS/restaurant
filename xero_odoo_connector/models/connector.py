# -*- coding: utf-8 -*-

import base64
import datetime
import json
import re
import requests

from odoo import api, fields, models, _
from odoo.exceptions import Warning
from werkzeug import urls


class ErrorLog(models.Model):
    _name = 'error.log'
    _description = 'Error Log'

    name = fields.Char(string='Name')
    model = fields.Char(string='Model')
    base_id = fields.Char(string='Base Id')
    detail = fields.Char(string='Details')
    date_operation = fields.Datetime(string='Opration / Export Date')


class XeroXero(models.Model):
    _name = 'xero.xero'
    _description = 'Xero'

    name = fields.Char(string='App Name', required=True)
    clientkey = fields.Char(string='Client ID', required=True)
    clientsecret = fields.Char(string='Client Secret Key', required=True)
    xero_referral_id = fields.Char(string='Xero Referral ID')
    access_token_url = fields.Char(string='Access Token URL', readonly=True, store=True,
                                   default='https://identity.xero.com/connect/token')
    authorization_url = fields.Char(string='Authorization URL', readonly=True, store=True,
                                    default='https://login.xero.com/identity/connect/authorize')
    redirect_url = fields.Char(string='Redirect URL', required=True, default="http://localhost:8069/xero/callback")
    scopes = fields.Char(string='Scopes',
                         default='offline_access accounting.transactions openid profile email accounting.contacts accounting.settings payroll.employees payroll.employees.read payroll.payruns payroll.payruns.read payroll.payslip payroll.payslip.read payroll.timesheets payroll.timesheets.read payroll.settings payroll.settings.read')
    oauth2_redirect_url = fields.Char(string='OAuth2.0 Redirect URL')

    authorize_url = fields.Char(string="Authorize URL", default="https://login.xero.com/identity/connect/authorize")
    access_token_url = fields.Char(string="Access Token URL", default="https://identity.xero.com/connect/token")

    access_token = fields.Char(string='Access Token')
    refresh_access_token = fields.Char(string='Refresh Access Token')

    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)

    options = fields.Selection([('create', 'Add'), ('update', 'Modify'), ('both', 'Add-Modify')], string='Options',
                               default='create')
    no_product = fields.Boolean(string='Not mendatory products in invoice ?')
    sale_journal_id = fields.Many2one('account.journal', string='Default Sale Journal')
    purchase_journal_id = fields.Many2one('account.journal', string='Default Purchase Journal')
    misc_journal_id = fields.Many2one('account.journal', string='Default Miscellaneous Journal')
    journal_ids = fields.Many2many('account.journal', string='Payment Journals')
    inventory_options = fields.Boolean(string='Inventory Options')
    manual_import = fields.Boolean(string='Manual Import')
    manual_export = fields.Boolean(string='Manual Export')
    mapped_categ_id = fields.Many2one('product.category', string='Mapped Category', required=False)
    unmapped_categ_id = fields.Many2one('product.category', string='Unmapped Category', required=False)
    inventory_account_id = fields.Many2one('account.account', string='Inventory Adjustment Account')

    date_export_history_partner = fields.Datetime(string='Partner Export Date History')
    date_create_import_history_partner = fields.Datetime(string='Partner Import Create Date History')
    date_update_import_history_partner = fields.Datetime(string='Partner Import Update Date History')

    date_create_import_history_employee = fields.Datetime(string='Employee Import Create Date History')
    date_update_import_history_employee = fields.Datetime(string='Employee Import Update Date History')

    date_export_history_product = fields.Datetime(string='Product Export Date History')
    date_create_import_history_product = fields.Datetime(string='Product Import Create Date History')
    date_update_import_history_product = fields.Datetime(string='Product Import Update Date History')

    date_export_history_journal = fields.Datetime(string='Journal Export Date History')
    date_create_import_history_journal = fields.Datetime(string='Journal Import Create Date History')
    date_update_import_history_journal = fields.Datetime(string='Journal Import Update Date History')

    date_export_history_invoice = fields.Datetime(string='Invoice Export Date History')
    date_create_import_history_invoice = fields.Datetime(string='Invoice Import Create Date History')
    date_update_import_history_invoice = fields.Datetime(string='Invoice Import Update Date History')

    date_export_history_refund = fields.Datetime(string='Refund Export Date History')
    date_create_import_history_refund = fields.Datetime(string='Refund Import Create Date History')
    date_update_import_history_refund = fields.Datetime(string='Refund Import Update Date History')

    inactive_export = fields.Boolean(string='Disable Export', default=False)
    import_export_refund = fields.Selection([('import', 'Import'), ('export', 'Export')], string='Refund Invoices',
                                            default='import')

    def authorize_and_get_token(self):
        self.ensure_one()
        encoded_params = urls.url_encode({
            'scope': self.scopes,
            'redirect_uri': self.redirect_url,
            'client_id': self.clientkey,
            'response_type': 'code',
            'state': self.id
        })

        target_url = '%s?%s' % (self.authorize_url, encoded_params)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': target_url,
        }

    @api.model
    def RefereshToken(self):
        xero_accounts = self.env['xero.xero'].search(
            [('clientkey', '!=', False), ('clientsecret', '!=', False), ('access_token_url', '!=', False),
             ('refresh_access_token', '!=', False)])
        if xero_accounts:
            for xero_account in xero_accounts:

                auth_header = 'Basic ' + base64.b64encode(
                    (xero_account.clientkey + ':' + xero_account.clientsecret).encode()).decode()
                headers = {
                    'Accept': 'application/json',
                    'content-type': 'application/x-www-form-urlencoded',
                    'Authorization': auth_header
                }
                payload = {
                    'refresh_token': xero_account.refresh_access_token,
                    'grant_type': 'refresh_token'
                }
                r = requests.post(xero_account.access_token_url, data=payload, headers=headers)
                if r.status_code != 200:
                    return r.text
                bearer_raw = json.loads(r.text)

                if bearer_raw.get('access_token'):
                    xero_account.access_token = str(bearer_raw.get('access_token').strip())

                if bearer_raw.get('refresh_token'):
                    xero_account.refresh_access_token = str(bearer_raw.get('refresh_token').strip())

    def parse_date(self, string, force_datetime=False):
        # Takes a Xero formatted date, e.g. '/Date(1426849200000+1300)/'
        DATE = re.compile(
            r'^(\/Date\((?P<timestamp>-?\d+)((?P<offset_h>[-+]\d\d)(?P<offset_m>\d\d))?\)\/)'
            r'|'
            r'((?P<year>\d{4})-(?P<month>[0-2]\d)-0?(?P<day>[0-3]\d)'
            r'T'
            r'(?P<hour>[0-5]\d):(?P<minute>[0-5]\d):(?P<second>[0-6]\d))$'
        )
        matches = DATE.match(string)
        if not matches:
            return None

        values = dict([
            (k, v if v[0] in '+-' else int(v)) for k, v in matches.groupdict().items() if v and int(v)
        ])

        if 'timestamp' in values:
            value = datetime.datetime.utcfromtimestamp(0) + datetime.timedelta(
                hours=int(values.get('offset_h', 0)),
                minutes=int(values.get('offset_m', 0)),
                seconds=int(values['timestamp']) / 1000.0
            )
            return value

            if not value.time():
                return value.date()
            return value

        if len(values) > 3 or force_datetime:
            return datetime.datetime(**values)
        return date(**values)

    def json_load_object_hook(self, dct):
        for key, value in dct.items():
            if isinstance(value, str) and value.startswith('/') and value.endswith('/'):
                value = self.parse_date(value)
                if value:
                    dct[key] = value
        return dct

    def get_import_data_xeroapi(self, endpoint, custom_headers=None):
        headers = {
            'authorization': "Bearer %s" % self.access_token,
            'xero-tenant-id': self.xero_referral_id,
            'accept': "application/json",
        }
        if custom_headers is not None:
            headers.update(custom_headers)
        url = "https://api.xero.com/api.xro/2.0/"
        response = requests.request("GET", url + endpoint, headers=headers)
        if response.status_code == 200:
            res = json.loads(response.text)
            return res
        return False

    def get_import_data_xeroapi_emp(self, endpoint, custom_headers=None):
        headers = {
            'authorization': "Bearer %s" % self.access_token,
            'xero-tenant-id': self.xero_referral_id,
            'accept': "application/json",
        }
        if custom_headers is not None:
            headers.update(custom_headers)
        url = "https://api.xero.com/payroll.xro/1.0/"
        response = requests.request("GET", url + endpoint, headers=headers)
        if response.status_code == 200:
            res = json.loads(response.text)
            return res
        return False

    def get_import_data_xeroapi_emp_full_details(self, endpoint, custom_headers=None):
        headers = {
            'authorization': "Bearer %s" % self.access_token,
            'xero-tenant-id': self.xero_referral_id,
            'accept': "application/json",
        }
        if custom_headers is not None:
            headers.update(custom_headers)
        url = "https://api.xero.com/payroll.xro/1.0/Employees/"
        # au
        response = requests.request("GET", url + endpoint, headers=headers)
        if response.status_code == 200:
            res = json.loads(response.text)
            # print(res,"res json")
            return res
        return False

    def get_import_data_xeroapi_payrun_full_details(self, endpoint, custom_headers=None):
        headers = {
            'authorization': "Bearer %s" % self.access_token,
            'xero-tenant-id': self.xero_referral_id,
            'accept': "application/json",
        }
        if custom_headers is not None:
            headers.update(custom_headers)
        url = "https://api.xero.com/payroll.xro/1.0/PayRuns/"
        # au
        response = requests.request("GET", url + endpoint, headers=headers)
        if response.status_code == 200:
            res = json.loads(response.text)
            return res
        return False

    def get_import_data_xeroapi_payslip_full_details(self, endpoint, custom_headers=None):
        headers = {
            'authorization': "Bearer %s" % self.access_token,
            'xero-tenant-id': self.xero_referral_id,
            'accept': "application/json",
        }
        if custom_headers is not None:
            headers.update(custom_headers)
        url = "https://api.xero.com/payroll.xro/1.0/Payslip/"
        # au
        response = requests.request("GET", url + endpoint, headers=headers)
        if response.status_code == 200:
            res = json.loads(response.text)
            return res
        return False

    def put_data_xeroapi(self, endpoint, data, custom_headers=None):
        headers = {
            'authorization': "Bearer %s" % self.access_token,
            'xero-tenant-id': self.xero_referral_id,
            'accept': "application/json",
        }
        if custom_headers is not None:
            headers.update(custom_headers)
        url = "https://api.xero.com/api.xro/2.0/"
        response = requests.request("PUT", url + endpoint, data=data, headers=headers)
        if response.status_code == 200:
            res = json.loads(response.text)
            return res
        return False

    def save_data_xeroapi(self, endpoint, data, custom_headers=None):
        headers = {
            'authorization': "Bearer %s" % self.access_token,
            'xero-tenant-id': self.xero_referral_id,
            'accept': "application/json",
        }
        if custom_headers is not None:
            headers.update(custom_headers)
        url = "https://api.xero.com/api.xro/2.0/"
        response = requests.request("SAVE", url + endpoint, data=data, headers=headers)
        if response.status_code == 200:
            res = json.loads(response.text)
            return res
        return False

    @api.model
    def BaseSchedularXeroImport(self):
        for record in self.search([('active', '=', True)]):
            if record.access_token and record.xero_referral_id:
                # Xero Get Currency
                record.xero_get_currency()
                # Xero Get Account
                record.xero_get_account()
                # Xero Get Bank Account
                record.xero_get_bank_account()
                # Xero Get Tax
                record.xero_get_tax()
                # Xero Get Contacts
                record.xero_get_contact()

                # Xero Get Product
                if not record.no_product:
                    record.xero_get_product()
                # Xero Get Invoice
                record.xero_get_invoice()
                # Xero Get Journal
                record.xero_get_journal()

                # Xero Get Refund Invoices
                record.xero_get_refund_invoices()

    @api.model
    def BaseSchedularXeroExport(self):
        for record in self.search([('active', '=', True)]):
            if record.access_token and record.xero_tenant_id:
                # Export Taxes
                tax_rates = self.get_import_data_xeroapi('TaxRates')
                self.env['account.tax'].export_tax(tax_rates.get('TaxRates'), self, company=record.company_id.id,
                                                   disable_export=record.export_disable)
                # Export Accounts
                account_list = self.get_import_data_xeroapi('Accounts')
                self.env['account.account'].export_account(account_list.get('Accounts'), self,
                                                           company=record.company_id.id,
                                                           disable_export=record.export_disable)
                # Export Bank Accounts
                bank_account_list = self.get_import_data_xeroapi('Accounts?where=Type%3D%3D%22BANK%22')
                self.env['res.partner.bank'].export_bank_account(bank_account_list.get('Accounts'), self,
                                                                 company=record.company_id.id,
                                                                 disable_export=record.export_disable)
                # Export Contact Groups
                group_list = self.get_import_data_xeroapi('ContactGroups')
                self.env['res.partner.category'].export_contact_group(group_list.get('ContactGroups'), self)
                # Export Contacts
                record.export_contact()
                # Export Products
                record.export_product()
                # Export invoices
                record.export_invoice()
                record.export_payment()
                # Export credit Notes
                if record.import_export_creditnotes == 'export':
                    record.export_credit_notes()
                    record.export_credit_notes_payment()
                # Export Inventory Adjustments
                self.env['stock.move.line'].create_inventory_adjustments(self, company=record.company_id.id)
                # Export Attachment
                self.env['ir.attachment'].export_attachments(self, company=record.company_id.id)

    def xero_get_currency(self):
        self.ensure_one()
        if not self.access_token or not self.xero_referral_id:
            raise Warning(_('Authentication Failed !\nPlease authenticate again.'))
        res = self.get_import_data_xeroapi('Currencies')
        self.env['res.currency'].set_currency_to_odoo(res.get('Currencies'), res)

    def xero_get_tax(self):
        if not self.access_token or not self.xero_referral_id:
            raise Warning(_('Authentication Failed !\nPlease authenticate again.'))
        res = self.get_import_data_xeroapi('TaxRates')
        self.env['account.tax'].set_tax_to_odoo(res.get('TaxRates'), self, company_id=self.company_id.id,
                                                options=self.options)

    def xero_get_account(self):
        self.ensure_one()
        if not self.access_token or not self.xero_referral_id:
            raise Warning(_('Authentication Failed !\nPlease authenticate again.'))
        res = self.get_import_data_xeroapi('Accounts')
        print(res, "account")
        self.env['account.account'].set_coa_to_odoo(res.get('Accounts'), self, company_id=self.company_id.id,
                                                    options=self.options)

    def xero_get_bank_account(self):
        self.ensure_one()
        if not self.access_token or not self.xero_referral_id:
            raise Warning(_('Authentication Failed !\nPlease authenticate again.'))
        res = self.get_import_data_xeroapi('Accounts?where=Type%3D%3D%22BANK%22')
        self.env['res.partner.bank'].set_bank_account_to_odoo(res.get('Accounts'), self, options=self.options,
                                                              company_id=self.company_id.id)

    def xero_get_contact(self):
        self.ensure_one()
        if not self.access_token or not self.xero_referral_id:
            raise Warning(_('Authentication Failed !\nPlease authenticate again.'))
        res = self.get_import_data_xeroapi('ContactGroups')
        self.env['res.partner.category'].set_partner_group_to_odoo(res.get('ContactGroups'))
        page = 0
        while True:
            page += 1
            contact_list = []
            if self.date_create_import_history_partner and self.options == 'create':
                res = self.get_import_data_xeroapi('Contacts?page=%s' % str(page), {
                    'If-Modified-Since': self.date_create_import_history_partner.strftime('%a, %d %b %Y %H:%M:%S GMT')})
                contact_list = res.get('Contacts')
            elif self.date_update_import_history_partner and self.options == 'update':
                res = self.get_import_data_xeroapi('Contacts?page=%s' % str(page), {
                    'If-Modified-Since': self.date_update_import_history_partner.strftime('%a, %d %b %Y %H:%M:%S GMT')})
                contact_list = res.get('Contacts')
            elif self.options == 'both' and self.date_create_import_history_partner and self.date_update_import_history_partner:
                min_date = min(self.date_create_import_history_partner, self.date_update_import_history_partner)
                res = self.get_import_data_xeroapi('Contacts?page=%s' % str(page), {
                    'If-Modified-Since': min_date.strftime('%a, %d %b %Y %H:%M:%S GMT')})
                contact_list = res.get('Contacts')
            else:
                res = self.get_import_data_xeroapi('Contacts?page=%s' % str(page))
                contact_list = res.get('Contacts')
            if contact_list:
                self.env['res.partner'].set_partner_to_odoo(contact_list, self, company_id=self.company_id.id,
                                                            options=self.options)
            else:
                break
        #
        if self.options == 'create':
            self.date_create_import_history_partner = fields.Datetime.now()
        elif self.options == 'update':
            self.date_update_import_history_partner = fields.Datetime.now()
        elif self.options == 'both':
            self.date_create_import_history_partner = fields.Datetime.now()
            self.date_update_import_history_partner = fields.Datetime.now()

    def xero_get_employee(self):
        self.ensure_one()
        if not self.access_token or not self.xero_referral_id:
            raise Warning(_('Authentication Failed !\nPlease authenticate again.'))
        res = self.get_import_data_xeroapi('Contacts')
        page = 0
        while True:
            page += 1
            employee_list = []
            employee_full_list = []
            if self.date_create_import_history_employee and self.options == 'create':
                res = self.get_import_data_xeroapi_emp('Employees?page=%s' % str(page), {
                    'If-Modified-Since': self.date_update_import_history_employee.strftime(
                        '%a, %d %b %Y %H:%M:%S GMT')})
                employee_list = res.get('Employees')
            elif self.date_create_import_history_employee and self.options == 'update':
                res = self.get_import_data_xeroapi_emp('Employees?page=%s' % str(page), {
                    'If-Modified-Since': self.date_update_import_history_employee.strftime(
                        '%a, %d %b %Y %H:%M:%S GMT')})
                employee_list = res.get('Employees')
            elif self.options == 'both' and self.date_create_import_history_employee and self.date_update_import_history_employee:
                min_date = min(self.date_create_import_history_employee, self.date_update_import_history_employee)
                res = self.get_import_data_xeroapi_emp('Employees?page=%s' % str(page), {
                    'If-Modified-Since': min_date.strftime('%a, %d %b %Y %H:%M:%S GMT')})
                employee_list = res.get('Employees')
            else:
                res = self.get_import_data_xeroapi_emp('Employees?page=%s' % str(page))
                employee_list = res.get('Employees')
            if employee_list:
                for xero_employee in employee_list:
                    xx = str(xero_employee.get('EmployeeID'))
                    res = self.get_import_data_xeroapi_emp_full_details(xx)
                    employee_full_list = res.get('Employees')
                    self.env['hr.employee'].set_employees_to_odoo(employee_full_list, self,
                                                                  company_id=self.company_id.id, options=self.options)
            else:
                break

    def xero_get_employee_payslip(self):
        self.ensure_one()
        payruns_full_list = []
        employee_payslip_list = []
        payitem_lst = []
        tot_payslips_only = []
        if not self.access_token or not self.xero_referral_id:
            raise Warning(_('Authentication Failed !\nPlease authenticate again.'))
        res = self.get_import_data_xeroapi_emp('PayItems')
        payitem_lst = res.get('PayItems')
        if payitem_lst:
            self.env['hr.leave.type'].set_employees_leave_to_odoo(payitem_lst, self, company_id=self.company_id.id,
                                                                  options=self.options)
        else:
            return
        page = 0
        while True:
            page += 1
            employee_list = []
            employee_full_list = []
            payroll_calender_list = []
            leave_application_list = []
            payslip_lst = []
            if self.date_create_import_history_employee and self.options == 'create':
                res = self.get_import_data_xeroapi_emp('PayRuns?page=%s' % str(page), {
                    'If-Modified-Since': self.date_update_import_history_employee.strftime(
                        '%a, %d %b %Y %H:%M:%S GMT')})
                payrun_list = res.get('PayRuns')
                calender = self.get_import_data_xeroapi_emp('PayrollCalendars?page=%s' % str(page), {
                    'If-Modified-Since': self.date_update_import_history_employee.strftime(
                        '%a, %d %b %Y %H:%M:%S GMT')})
                payroll_calender_list = calender.get('PayrollCalendars')
                leave_app = self.get_import_data_xeroapi_emp('LeaveApplications?page=%s' % str(page), {
                    'If-Modified-Since': self.date_update_import_history_employee.strftime(
                        '%a, %d %b %Y %H:%M:%S GMT')})
                leave_application_list = leave_app.get('LeaveApplications')
            elif self.date_create_import_history_employee and self.options == 'update':
                res = self.get_import_data_xeroapi_emp('PayRuns?page=%s' % str(page), {
                    'If-Modified-Since': self.date_update_import_history_employee.strftime(
                        '%a, %d %b %Y %H:%M:%S GMT')})
                payrun_list = res.get('PayRuns')
                calender = self.get_import_data_xeroapi_emp('PayrollCalendars?page=%s' % str(page), {
                    'If-Modified-Since': self.date_update_import_history_employee.strftime(
                        '%a, %d %b %Y %H:%M:%S GMT')})
                payroll_calender_list = calender.get('PayrollCalendars')
                leave_app = self.get_import_data_xeroapi_emp('LeaveApplications?page=%s' % str(page), {
                    'If-Modified-Since': self.date_update_import_history_employee.strftime(
                        '%a, %d %b %Y %H:%M:%S GMT')})
                leave_application_list = leave_app.get('LeaveApplications')
            elif self.options == 'both' and self.date_create_import_history_employee and self.date_update_import_history_employee:
                min_date = min(self.date_create_import_history_employee, self.date_update_import_history_employee)
                res = self.get_import_data_xeroapi_emp('PayRuns?page=%s' % str(page), {
                    'If-Modified-Since': min_date.strftime('%a, %d %b %Y %H:%M:%S GMT')})
                payrun_list = res.get('PayRuns')
                calender = self.get_import_data_xeroapi_emp('PayrollCalendars?page=%s' % str(page), {
                    'If-Modified-Since': self.date_update_import_history_employee.strftime(
                        '%a, %d %b %Y %H:%M:%S GMT')})
                payroll_calender_list = calender.get('PayrollCalendars')
                leave_app = self.get_import_data_xeroapi_emp('LeaveApplications?page=%s' % str(page), {
                    'If-Modified-Since': self.date_update_import_history_employee.strftime(
                        '%a, %d %b %Y %H:%M:%S GMT')})
                leave_application_list = leave_app.get('LeaveApplications')
            else:
                res = self.get_import_data_xeroapi_emp('PayRuns?page=%s' % str(page))
                if res:
                    payrun_list = res.get('PayRuns')
                    calender = self.get_import_data_xeroapi_emp('PayrollCalendars?page=%s' % str(page))
                    payroll_calender_list = calender.get('PayrollCalendars')
                    leave_app = self.get_import_data_xeroapi_emp('LeaveApplications?page=%s' % str(page))
                    if leave_app:
                        leave_application_list = leave_app.get('LeaveApplications')
                        if leave_application_list:
                            self.env['hr.leave'].set_employees_leave_app_to_odoo(leave_application_list, self,
                                                                                 company_id=self.company_id.id,
                                                                                 options=self.options)
                        else:
                            break
                    if payrun_list:
                        for xero_payrun in payrun_list:
                            xx = str(xero_payrun.get('PayRunID'))
                            run = 'PayRuns' + '/' + xx
                            res = self.get_import_data_xeroapi_payrun_full_details(xx)
                            if res:
                                payruns_list = res.get('PayRuns')
                                if payruns_list:
                                    for i in payruns_list:
                                        payslip_new_lst = i.get('Payslips')
                                        for slip_data in payslip_new_lst:
                                            str_payslip = str(slip_data.get('PayslipID'))
                                            payslip_lst = self.get_import_data_xeroapi_payslip_full_details(str_payslip)
                                            if payslip_lst:
                                                tot_payslips = payslip_lst.get('Payslip')
                                                tot_payslips_only.append(payslip_lst)
                                        self.env['hr.payslip.run'].set_employees_payrun_list_to_odoo(
                                            payruns_list, tot_payslips_only, self,
                                            company_id=self.company_id.id,
                                            options=self.options)

    def xero_get_product(self):
        if not self.access_token or not self.xero_referral_id:
            raise Warning(_('Authentication Failed !\nPlease authenticate again.'))
        if self.date_create_import_history_product and self.options == 'create':
            product_list = self.get_import_data_xeroapi('Items', {
                'If-Modified-Since': self.date_create_import_history_product.strftime('%a, %d %b %Y %H:%M:%S GMT')})
        elif self.date_update_import_history_product and self.options == 'update':
            product_list = self.get_import_data_xeroapi('Items', {
                'If-Modified-Since': self.date_update_import_history_product.strftime('%a, %d %b %Y %H:%M:%S GMT')})
        elif self.options == 'both' and self.date_create_import_history_product and self.date_update_import_history_product:
            min_date = min(self.date_create_import_history_product, self.date_update_import_history_product)
            product_list = self.get_import_data_xeroapi('Items', {
                'If-Modified-Since': min_date.strftime('%a, %d %b %Y %H:%M:%S GMT')})
        else:
            product_list = self.get_import_data_xeroapi('Items')
        self.env['product.product'].set_product_to_odoo(product_list.get('Items'), self, self.mapped_categ_id,
                                                        self.unmapped_categ_id, company_id=self.company_id.id,
                                                        options=self.options)
        if self.options == 'create':
            self.date_create_import_history_product = fields.Datetime.now()
        elif self.options == 'update':
            self.date_update_import_history_product = fields.Datetime.now()
        else:
            self.date_create_import_history_product = fields.Datetime.now()
            self.date_update_import_history_product = fields.Datetime.now()

    def xero_get_invoice(self):
        if not self.access_token or not self.xero_referral_id:
            raise Warning(_('Authentication Failed !\nPlease authenticate again.'))
        page = 0
        while True:
            page += 1
            invoice_list = []
            if self.date_create_import_history_invoice and self.options == 'create':
                res = self.get_import_data_xeroapi('Invoices?page=%s' % str(page), {
                    'If-Modified-Since': self.date_create_import_history_invoice.strftime('%a, %d %b %Y %H:%M:%S GMT')})
                invoice_list = res.get('Invoices')
            elif self.date_update_import_history_invoice and self.options == 'update':
                res = self.get_import_data_xeroapi('Invoices?page=%s' % str(page), {
                    'If-Modified-Since': self.date_update_import_history_invoice.strftime('%a, %d %b %Y %H:%M:%S GMT')})
                invoice_list = res.get('Invoices')
            elif self.options == 'both' and self.date_create_import_history_invoice and self.date_update_import_history_invoice:
                min_date = min(self.date_create_import_history_invoice, self.date_update_import_history_invoice)
                res = self.get_import_data_xeroapi('Invoices?page=%s' % str(page), {
                    'If-Modified-Since': min_date.strftime('%a, %d %b %Y %H:%M:%S GMT')})
                invoice_list = res.get('Invoices')
            else:
                res = self.get_import_data_xeroapi('Invoices?page=%s' % str(page))
                invoice_list = res.get('Invoices')

            if invoice_list:
                self.env['account.move'].set_invoice_to_odoo(invoice_list, self, company_id=self.company_id.id,
                                                             no_product=self.no_product, options=self.options,
                                                             customer_journal_id=self.sale_journal_id,
                                                             vendor_journal_id=self.purchase_journal_id)
            else:
                break

        if self.options == 'create':
            self.date_create_import_history_invoice = fields.Datetime.now()
        elif self.options == 'update':
            self.date_update_import_history_invoice = fields.Datetime.now()
        else:
            self.date_create_import_history_invoice = fields.Datetime.now()
            self.date_update_import_history_invoice = fields.Datetime.now()

    def xero_get_refund_invoices(self):
        if not self.access_token or not self.xero_referral_id:
            raise Warning(_('Authentication Failed !\nPlease authenticate again.'))
        page = 0
        while True:
            page += 1
            credit_notes_list = []
            if self.date_create_import_history_refund and self.options == 'create':
                res = self.get_import_data_xeroapi('CreditNotes?page=%s' % str(page), {
                    'If-Modified-Since': self.date_create_import_history_refund.strftime('%a, %d %b %Y %H:%M:%S GMT')})
                credit_notes_list = res.get('CreditNotes')
            elif self.date_update_import_history_refund and self.options == 'update':
                res = self.get_import_data_xeroapi('CreditNotes?page=%s' % str(page), {
                    'If-Modified-Since': self.date_update_import_history_refund.strftime('%a, %d %b %Y %H:%M:%S GMT')})
                credit_notes_list = res.get('CreditNotes')
            elif self.options == 'both' and self.date_create_import_history_refund and self.date_update_import_history_refund:
                min_date = min(self.date_create_import_history_refund, self.date_update_import_history_refund)

                res = self.get_import_data_xeroapi('CreditNotes?page=%s' % str(page), {
                    'If-Modified-Since': min_date.strftime('%a, %d %b %Y %H:%M:%S GMT')})

                credit_notes_list = res.get('CreditNotes')
            else:

                res = self.get_import_data_xeroapi('CreditNotes?page=%s' % str(page))

                credit_notes_list = res.get('CreditNotes')

            if credit_notes_list:
                self.env['account.move'].set_refund_invoice_to_odoo(credit_notes_list, self,
                                                                    company_id=self.company_id.id,
                                                                    no_product=self.no_product, options=self.options,
                                                                    customer_journal_id=self.sale_journal_id,
                                                                    vendor_journal_id=self.purchase_journal_id)
            else:
                break

        if self.options == 'create':
            self.date_create_import_history_refund = fields.Datetime.now()
        elif self.options == 'update':
            self.date_update_import_history_refund = fields.Datetime.now()
        else:
            self.date_create_import_history_refund = fields.Datetime.now()
            self.date_update_import_history_refund = fields.Datetime.now()

    def xero_get_journal(self):
        if not self.access_token or not self.xero_referral_id:
            raise Warning(_('Authentication Failed !\nPlease authenticate again.'))
        page = 0
        while True:
            page += 1
            journal_list = self.get_import_data_xeroapi('ManualJournals?page=%s' % str(page))
            if journal_list.get('ManualJournals'):
                self.env['account.move'].set_journal_to_odoo(journal_list['ManualJournals'], self,
                                                             company_id=self.company_id.id, options=self.options)
            else:
                break

        if self.options == 'create':
            self.date_create_import_history_journal = fields.Datetime.now()
        elif self.options == 'update':
            self.date_update_import_history_journal = fields.Datetime.now()
        else:
            self.date_create_import_history_journal = fields.Datetime.now()
            self.date_update_import_history_journal = fields.Datetime.now()

    def xero_post_currency(self):
        return True

    def xero_post_contact(self):
        return True

    def xero_post_product(self):
        return True

    def xero_post_account(self):
        return True

    def xero_post_journal(self):
        return True

    def xero_post_invoice(self):
        return True

    def xero_post_bank_account(self):
        return True

    def xero_post_tax(self):
        return True

    def xero_post_refund_invoices(self):
        return True
