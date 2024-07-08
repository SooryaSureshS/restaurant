# -*- coding: utf-8 -*-
import json
import re
import requests
from odoo import api, fields, models, _
from odoo.exceptions import Warning


class ResPartnerInherited(models.Model):
    _inherit = 'res.partner'

    xero_employee_ref = fields.Char()


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    xero_employee_id = fields.Char()
    xero_partner_ref = fields.Char(string='Xero Conatct Name')
    xero_skype_name = fields.Char(string='Skype')
    xero_attention = fields.Char(string='Attention To')
    xero_firstname = fields.Char(string='First Name')
    xero_lastname = fields.Char(string='Last Name')
    xero_vat = fields.Char(string='Tax Number')
    xero_concate_phone_number = fields.Char(string='Direct dial')
    xero_related_companies = fields.One2many('xero.company', 'partner_id', string='Related Xero Company')

    @api.onchange('company_id')
    def _onchange_company(self):
        if self.company_id:
            xero_company_id = self.xero_related_companies.filtered(lambda c: c.company_id.id == self.company_id.id)
            if not xero_company_id:
                self.xero_related_companies = [(6, 0, {'company_id': self.company_id.id})]

    def set_employees_to_odoo(self, employees, xero, company_id=False, options=None):
        employee_ids = self.search(['|', ('company_id', '=', company_id), ('company_id', '=', False)])
        ResPartnerBank = self.env['res.partner.bank']
        ResCountryState = self.env['res.country.state']
        ResCountry = self.env['res.country']
        xero = self.env['xero.xero']
        ResCurrency = self.env['res.currency']
        AccountAccount = self.env['account.account']
        default_sale_account_id = AccountAccount.search(
            [('user_type_id', '=', self.env.ref('account.data_account_type_receivable').id),
             ('company_id', '=', company_id)], limit=1)
        default_purchase_account_id = AccountAccount.search(
            [('user_type_id', '=', self.env.ref('account.data_account_type_payable').id),
             ('company_id', '=', company_id)], limit=1)

        for xero_employee in employees:
            xero_employee = xero.json_load_object_hook(xero_employee)
            xero_active = True
            xero_concate_phone_number = xero_country_id = xero_state_id = xero_source_country_id = xero_source_state_id = xero_bank_id = xero_currency_id = invoice_address = False

            exist_partner_id = self.env['res.partner'].search(
                [('xero_employee_ref', '=', xero_employee.get('EmployeeID'))])
            exist_partner_id = exist_partner_id[0] if exist_partner_id else False
            partner_groups = []
            if xero_employee.get('HomeAddress'):
                for xero_partner_dict in xero_employee.get('HomeAddress'):
                    street1 = street2 = ''
                    partner_dict = {}
                    if xero_employee.get('HomeAddress').get('AddressLine1', False):
                        street1 += xero_employee.get('HomeAddress').get('AddressLine1', False)
                    if xero_employee.get('HomeAddress').get('AddressLine2', False):
                        street1 += ' ' + xero_employee.get('HomeAddress').get('AddressLine2', False)
                    if xero_employee.get('HomeAddress').get('City', False):
                        street2 += xero_employee.get('HomeAddress').get('City', False)
                    if xero_employee.get('HomeAddress').get('Region'):
                        xero_state_id = ResCountryState.search(
                            ['|', ('name', '=', xero_employee.get('HomeAddress').get('Region')),
                             ('code', '=', xero_employee.get('HomeAddress').get('Region'))], limit=1)
                        if not xero_state_id and xero_country_id:
                            xero_state_id = ResCountryState.create(
                                {'name': xero_employee.get('HomeAddress').get('Region'),
                                 'code': xero_employee.get('HomeAddress').get('Region'),
                                 'country_id': xero_country_id.id})

                if exist_partner_id and options in ['update', 'both']:
                    exist_partner_id.write({
                        'active': xero_active,
                        'name': (xero_employee.get('FirstName') or u'') + ' ' + (
                                xero_employee.get('LastName') or u''),
                        'phone': xero_employee.get('Phone'),
                        'mobile': xero_employee.get('Mobile'),
                        'xero_firstname': xero_employee.get('FirstName') or u'',
                        'xero_lastname': xero_employee.get('LastName') or u'',
                        'email': xero_employee.get('Email') or u'',
                        'city': street2,
                        'state_id': xero_state_id.id if xero_state_id else False,
                        'street': street1,
                        'street2': street2,
                        'zip': xero_employee.get('HomeAddress').get('PostalCode', False),
                        'country_id': xero_country_id.id if xero_country_id else False,
                        'property_account_receivable_id': default_sale_account_id.id if default_sale_account_id else False,
                        'property_account_payable_id': default_purchase_account_id.id if default_purchase_account_id else False,
                        'xero_bank_id': xero_bank_id.id if xero_bank_id else False,
                        'currency_id': xero_currency_id.id if xero_currency_id else False})
                    if xero_employee.get('BankAccounts'):
                        xero_bank_id = ResPartnerBank.search([('acc_number', '=' , xero_employee.get('BankAccountDetails'))], limit=1)
                        if not xero_bank_id:
                            ResPartnerBank.create({'acc_number': xero_employee.get('BankAccounts'),
                                                   'partner_id': exist_partner_id.id})
                        else:
                            xero_bank_id.partner_id = exist_partner_id.id

                    existing_emp = self.search([('xero_employee_id', '=', xero_employee.get('EmployeeID'))])
                    existing_emp.write({
                        'name': (xero_employee.get('FirstName') or u'') + ' ' + (
                                xero_employee.get('LastName') or u''),
                        'work_email': xero_employee.get('Email'),
                        'work_phone': xero_employee.get('Phone'),
                        'company_id': company_id,
                        'address_id': company_id,
                        'address_home_id': exist_partner_id.id,
                        'country_id': xero_country_id.id if xero_country_id else False,
                    })
                elif not exist_partner_id and options in ['create', 'both']:
                    partner_id = self.env['res.partner'].create({
                        'active': xero_active,
                        'xero_employee_ref': xero_employee.get('EmployeeID'),
                        'name': (xero_employee.get('FirstName') or u'') + ' ' + (
                                xero_employee.get('LastName') or u''),
                        'phone': xero_employee.get('Phone'),
                        'mobile': xero_employee.get('Mobile'),
                        'xero_firstname': xero_employee.get('FirstName') or u'',
                        'xero_lastname': xero_employee.get('LastName') or u'',
                        'email': xero_employee.get('EmailAddress') or u'',
                        'company_id': company_id,
                        'street': street1,
                        'street2': street2,
                        'city': street2,
                        'state_id': xero_state_id.id if xero_state_id else False,
                        'country_id': xero_country_id.id if xero_country_id else False,
                        'zip': xero_employee.get('HomeAddress').get('PostalCode', False),
                        'xero_bank_id': xero_bank_id.id if xero_bank_id else False,
                        'property_account_receivable_id': default_sale_account_id.id if default_sale_account_id else False,
                        'property_account_payable_id': default_purchase_account_id.id if default_purchase_account_id else False,
                        'currency_id': xero_currency_id.id if xero_currency_id else False})

                    if xero_employee.get('BankAccounts'):
                        xero_bank_id = ResPartnerBank.search([('acc_number', '=', xero_employee.get('BankAccountDetails'))], limit=1)
                        if not xero_bank_id:
                            ResPartnerBank.create({'acc_number': xero_employee.get('BankAccounts'),
                                                   'partner_id': partner_id.id})
                        else:
                            xero_bank_id.partner_id = partner_id.id

                    self.create({
                        'xero_employee_id': xero_employee.get('EmployeeID'),
                        'name': (xero_employee.get('FirstName') or u'') + ' ' + (
                                xero_employee.get('LastName') or u''),
                        'work_email': xero_employee.get('Email'),
                        'work_phone': xero_employee.get('Phone'),
                        'company_id': company_id,
                        'address_id': company_id,
                        'address_home_id': partner_id.id,
                        'country_id': xero_country_id.id if xero_country_id else False,

                    })


class XeroCompany(models.Model):
    _name = 'xero.company'
    _description = 'Related Xero Company'

    xero_ref_id = fields.Char('Xero ContctID')
    company_id = fields.Many2one('res.company', string='Related Company', required=True)
    partner_id = fields.Many2one('res.partner', string='Related Partner')
