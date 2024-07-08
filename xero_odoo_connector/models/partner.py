# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class ResPartner(models.Model):
    _inherit = 'res.partner'

    xero_partner_ref = fields.Char(string='Xero Conatct Name')
    xero_skype_name = fields.Char(string='Skype')
    xero_attention = fields.Char(string='Attention To')
    xero_firstname = fields.Char(string='First Name')
    xero_lastname = fields.Char(string='Last Name')
    xero_bank_id = fields.Many2one('res.partner.bank', string='Bank Account')
    xero_vat = fields.Char(string='Tax Number')
    xero_concate_phone_number = fields.Char(string='Direct dial')
    xero_related_companies = fields.One2many('xero.company', 'partner_id', string='Related Xero Company')

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                if '@' not in record.email or '.' not in record.email:
                    raise Warning(_('Invalid Email!'))
        return True

    @api.onchange('company_id')
    def _onchange_company(self):
        if self.company_id:
            xero_company_id = self.xero_related_companies.filtered(lambda c: c.company_id.id == self.company_id.id)
            if not xero_company_id:
                self.xero_related_companies = [(6, 0, {'company_id': self.company_id.id})]

    @api.onchange('email')
    def onchange_email(self):
        if self.email:
            if '@' not in self.email or '.' not in self.email:
                raise Warning(_('Invalid Email!'))

    def set_partner_to_odoo(self, contacts, xero, company_id=False, options=None):
        contact_ids = self.search(['|', ('company_id', '=', company_id), ('company_id', '=', False)])
        print(contact_ids,"contact_ids")
        check_emails_list = []
        for partner_id in contact_ids:
            check_emails_list.append(partner_id.email)

        ResPartnerCategory = self.env['res.partner.category']
        ResPartnerBank = self.env['res.partner.bank']
        ResCountryState = self.env['res.country.state']
        ResCountry = self.env['res.country']
        ResCurrency = self.env['res.currency']
        AccountAccount = self.env['account.account']

        default_sale_account_id = AccountAccount.search([('user_type_id', '=', self.env.ref('account.data_account_type_receivable').id), ('company_id', '=', company_id)], limit=1)
        default_purchase_account_id = AccountAccount.search([('user_type_id', '=', self.env.ref('account.data_account_type_payable').id), ('company_id', '=', company_id)], limit=1)

        for xero_partner in contacts:
            print(xero_partner,"xero_partner")
            xero_partner = xero.json_load_object_hook(xero_partner)
            xero_active = True
            xero_concate_phone_number = xero_country_id = xero_state_id = xero_source_country_id = xero_source_state_id = xero_bank_id = xero_currency_id = invoice_address = False
            

            exist_partner_id = self.search([]).filtered(lambda p:p.xero_related_companies.filtered(lambda c: c.company_id.id == company_id and c.xero_ref_id == xero_partner.get('ContactID')))
            exist_partner_id = exist_partner_id[0] if exist_partner_id else False
            
            partner_groups = []
            if xero_partner.get('Addresses'):
                for xero_partner_dict in xero_partner.get('Addresses'):
                    street1 = street2 = ''
                    partner_dict = {}
                    if xero_partner_dict.get('AddressType') == 'STREET':
                        partner_dict = xero_partner_dict
                        
                        if partner_dict.get('AddressLine1', False):
                            street1 += partner_dict.get('AddressLine1', False)
                        if partner_dict.get('AddressLine2', False):
                            street1 += ' '+ partner_dict.get('AddressLine2', False)
                        if partner_dict.get('AddressLine3', False):
                            street2 += partner_dict.get('AddressLine3', False)
                        if partner_dict.get('AddressLine4', False):
                            street2 += ' ' + partner_dict.get('AddressLine4', False)

                        if partner_dict.get('Country'):
                            xero_country_id = ResCountry.search([('name', '=' , partner_dict.get('Country'))], limit=1)
                            if not xero_country_id:
                                xero_country_id = ResCountry.create({'name':  partner_dict.get('Country')})
                        
                        if partner_dict.get('Region'):
                            xero_state_id = ResCountryState.search(['|', ('name', '=' , partner_dict.get('Region')),
                                              ('code', '=' , partner_dict.get('Region'))], limit=1)
                            if not xero_state_id and xero_country_id:
                                xero_state_id = ResCountryState.create({'name':  partner_dict.get('Region'),
                                                          'code': partner_dict.get('Region'),
                                                          'country_id': xero_country_id.id})

                    if xero_partner_dict.get('AddressType') == 'POBOX':
                        xero_pobox_partner_dict = xero_partner_dict
                        
                        pobox_street1 = pobox_street2 = ''
                        if xero_pobox_partner_dict.get('AddressLine1', False):
                            invoice_address = True
                            pobox_street1 += xero_pobox_partner_dict.get('AddressLine1', False)
                        if xero_pobox_partner_dict.get('AddressLine2', False):
                            invoice_address = True
                            pobox_street1 += ' ' + xero_pobox_partner_dict.get('AddressLine2', False)
                        if xero_pobox_partner_dict.get('AddressLine3', False):
                            invoice_address = True
                            pobox_street2 += xero_pobox_partner_dict.get('AddressLine3', False)
                        if xero_pobox_partner_dict.get('AddressLine4', False):
                            invoice_address = True
                            pobox_street2 += ' ' + xero_pobox_partner_dict.get('AddressLine4', False)

                        if xero_pobox_partner_dict.get('Country'):
                            invoice_address = True
                            xero_source_country_id = ResCountry.search([('name', '=' , xero_pobox_partner_dict.get('Country'))], limit=1)
                            if not xero_source_country_id:
                                xero_source_country_id = ResCountry.create({'name':  xero_pobox_partner_dict.get('Country')})
                        
                        if xero_pobox_partner_dict.get('Region'):
                            invoice_address = True
                            xero_source_state_id = ResCountryState.search(['|',('name', '=' , xero_pobox_partner_dict.get('Region')),
                                ('code', '=' , xero_pobox_partner_dict.get('Region'))], limit=1)
                            if not xero_source_state_id and xero_source_country_id:
                                xero_source_state_id = ResCountryState.create({'name':  xero_pobox_partner_dict.get('Region'),
                                                                'code': xero_pobox_partner_dict.get('Region'),
                                                                'country_id': xero_source_country_id.id})

                
                xero_currency_id = ResCurrency.search([('name', '=', xero_partner.get('DefaultCurrency'))], limit=1)
                phone_no = mobile_no = ''
                for phone_dict in xero_partner.get('Phones'):
                    if phone_dict.get('PhoneType', False):
                        if phone_dict.get('PhoneType') == 'DEFAULT':
                            if phone_dict.get('PhoneCountryCode', False):
                                phone_no = '+' + phone_dict.get('PhoneCountryCode', False) + ' ' + phone_dict.get('PhoneNumber', False)
                            else:
                                phone_no = phone_dict.get('PhoneNumber', False)
                        if phone_dict.get('PhoneType') == 'MOBILE':
                            if phone_dict.get('PhoneCountryCode', False):
                                mobile_no = '+' + phone_dict.get('PhoneCountryCode', False) + ' ' + phone_dict.get('PhoneNumber', False)
                            else:
                                mobile_no = phone_dict.get('PhoneNumber', False)
                        if phone_dict.get('PhoneType') == 'DDI':
                            if phone_dict.get('PhoneCountryCode', False):
                                xero_concate_phone_number = '+' + phone_dict.get('PhoneCountryCode', False) + ' ' + phone_dict.get('PhoneNumber', False)
                            else:
                                xero_concate_phone_number = phone_dict.get('PhoneNumber', False)

                if xero_partner.get('ContactStatus') != 'ACTIVE':
                    xero_active = False
                
                if exist_partner_id and options in ['update', 'both']:
                    exist_partner_id.write({
                            'active': xero_active,
                            'name': xero_partner.get('Name') or u'',
                            'xero_concate_phone_number': xero_concate_phone_number,
                            'phone': phone_no,
                            'mobile': mobile_no,
                            'xero_firstname':xero_partner.get('FirstName') or u'',
                            'xero_lastname':xero_partner.get('LastName') or u'',
                            'xero_skype_name':xero_partner.get('SkypeUserName') or u'',
                            'email':xero_partner.get('EmailAddress') or u'',
                            'customer_rank': 1 if xero_partner.get('IsCustomer') else 0,
                            'supplier_rank': 1 if xero_partner.get('IsSupplier') else 0,
                            'xero_attention': partner_dict.get('AttentionTo') or u'',
                            'city': partner_dict.get('City') or u'',
                            'state_id': xero_state_id.id if xero_state_id else False,
                            'street': street1,
                            'street2': street2,
                            'zip': partner_dict.get('PostalCode') or u'',
                            'country_id': xero_country_id.id if xero_country_id else False,
                            'website': xero_partner.get('Website') or u'',
                            'property_account_receivable_id': default_sale_account_id.id if default_sale_account_id else False,
                            'property_account_payable_id': default_purchase_account_id.id if default_purchase_account_id else False,
                            'xero_vat': xero_partner.get('TaxNumber') or u'',
                            'xero_bank_id': xero_bank_id.id if xero_bank_id else False,
                            'currency_id': xero_currency_id.id if xero_currency_id else False})

                    if xero_partner.get('BankAccountDetails'):
                        xero_bank_id = ResPartnerBank.search([('acc_number', '=' , xero_partner.get('BankAccountDetails'))], limit=1)
                        if not xero_bank_id:
                            ResPartnerBank.create({'acc_number': xero_partner.get('BankAccountDetails'),
                                                   'partner_id': exist_partner_id.id})
                        else:
                            xero_bank_id.partner_id = exist_partner_id.id

                    partner_category_group_id = False
                    for contactgroups in xero_partner.get('ContactGroups'):
                        partner_category_group_id = ResPartnerCategory.search([('xero_partner_source_id', '=', contactgroups.get('ContactGroupID'))], limit=1)
                        if partner_category_group_id:
                            partner_groups.append(partner_category_group_id.id)

                    partner_groups = list(set(partner_groups))
                    exist_partner_id.category_id = [(6, 0, partner_groups)] if partner_groups else []
                    
                    if invoice_address:
                        invoice_address_id = exist_partner_id.child_ids.filtered(lambda x: x.type == 'invoice')
                        if invoice_address_id:
                            invoice_address_id[0].write({
                                'type': 'invoice',
                                'street': pobox_street1,
                                'street2': pobox_street2,
                                'city': xero_pobox_partner_dict.get('City') or u'',
                                'state_id': xero_source_state_id.id if xero_source_state_id else False,
                                'country_id': xero_source_country_id.id if xero_source_country_id else False,
                                'zip': xero_pobox_partner_dict.get('PostalCode') or u'',
                                'xero_attention': xero_pobox_partner_dict.get('AttentionTo') or u'',
                                'xero_related_companies': [(0, 0, {'company_id': company_id})],
                                'parent_id':  exist_partner_id.id if exist_partner_id else False})
                        else:
                            self.create({
                                'type': 'invoice',
                                'street': pobox_street1,
                                'street2': pobox_street2,
                                'city': xero_pobox_partner_dict.get('City') or u'',
                                'state_id': xero_source_state_id.id if xero_source_state_id else False,
                                'country_id': xero_source_country_id.id if xero_source_country_id else False,
                                'zip': xero_pobox_partner_dict.get('PostalCode') or u'',
                                'xero_attention': xero_pobox_partner_dict.get('AttentionTo') or u'',
                                'xero_related_companies': [(0, 0, {'company_id': company_id})],
                                'parent_id':  exist_partner_id.id if exist_partner_id else False})

                    child_partner_list = []
                    for record in exist_partner_id.child_ids.filtered(lambda x: x.type == 'contact'):
                        child_partner_list.append(record.email)
                    for child_partner_dict in xero_partner.get('ContactPersons'):
                        if child_partner_dict.get('EmailAddress') in child_partner_list:
                            exist_child_partner_id = self.search([('parent_id', '=', exist_partner_id.id), ('email', '=', child_partner_dict.get('EmailAddress'))], limit=1)
                            if exist_child_partner_id:
                                exist_child_partner_id.write({
                                    'type': 'contact',
                                    'name': (child_partner_dict.get('FirstName') or u'') + ' ' + (child_partner_dict.get('LastName') or u''),
                                    'xero_firstname': child_partner_dict.get('FirstName') or u'',
                                    'xero_lastname': child_partner_dict.get('LastName') or u'',
                                    'email': child_partner_dict.get('EmailAddress') or u'',
                                    'xero_related_companies': [(0, 0, {'company_id': company_id})],
                                    'parent_id': exist_partner_id.id if exist_partner_id else False,
                                    })
                        else:
                            self.create({
                                'type': 'contact',
                                'name': (child_partner_dict.get('FirstName') or u'') + ' ' + (child_partner_dict.get('LastName') or u''),
                                'xero_firstname': child_partner_dict.get('FirstName') or u'',
                                'xero_lastname': child_partner_dict.get('LastName') or u'',
                                'email': child_partner_dict.get('EmailAddress') or u'',
                                'xero_related_companies': [(0, 0, {'company_id': company_id})],
                                'parent_id': exist_partner_id.id if exist_partner_id else False,
                                })
                    self._cr.commit()

                elif not exist_partner_id and options in ['create', 'both']:
                    partner_id = self.create({
                            'active': xero_active,
                            'name':xero_partner.get('Name') or u'',
                            'phone': phone_no,
                            'mobile': mobile_no,
                            'xero_concate_phone_number': xero_concate_phone_number,
                            'xero_firstname':xero_partner.get('FirstName') or u'',
                            'xero_lastname':xero_partner.get('LastName') or u'',
                            'xero_skype_name':xero_partner.get('SkypeUserName') or u'',
                            'email':xero_partner.get('EmailAddress') or u'',
                            'website': xero_partner.get('Website') or u'',
                            'company_id': company_id,
                            'xero_related_companies': [(0, 0, {'company_id': company_id,
                                                               'xero_ref_id': xero_partner.get('ContactID') or u''})],
                            'customer_rank': 1 if xero_partner.get('IsCustomer') else 0,
                            'supplier_rank': 1 if xero_partner.get('IsSupplier') else 0,
                            'street': street1,
                            'street2': street2,
                            'city': partner_dict.get('City') or u'',
                            'state_id': xero_state_id.id if xero_state_id else False,
                            'country_id': xero_country_id.id if xero_country_id else False,
                            'zip': partner_dict.get('PostalCode') or u'',
                            'xero_vat': xero_partner.get('TaxNumber') or u'',
                            'xero_bank_id': xero_bank_id.id if xero_bank_id else False,
                            'xero_attention': partner_dict.get('AttentionTo') or u'',
                            'property_account_receivable_id': default_sale_account_id.id if default_sale_account_id else False,
                            'property_account_payable_id': default_purchase_account_id.id if default_purchase_account_id else False,
                            'currency_id': xero_currency_id.id if xero_currency_id else False})

                    if xero_partner.get('BankAccountDetails'):
                        xero_bank_id = ResPartnerBank.search([('acc_number', '=' , xero_partner.get('BankAccountDetails'))], limit=1)
                        if not xero_bank_id:
                            ResPartnerBank.create({'acc_number': xero_partner.get('BankAccountDetails') or u'',
                                                      'partner_id': partner_id.id})
                        else:
                            xero_bank_id.partner_id = partner_id.id

                    partner_category_group_id = False
                    for contactgroups in xero_partner.get('ContactGroups'):
                        partner_category_group_id = ResPartnerCategory.search([('xero_partner_source_id', '=', contactgroups.get('ContactGroupID'))], limit=1)
                        if partner_category_group_id:
                            partner_groups.append(partner_category_group_id.id)
                    partner_id.category_id = [(6, 0, partner_groups)] if partner_groups else []

                    if invoice_address:
                        self.create({
                            'type': 'invoice',
                            'street': pobox_street1,
                            'street2': pobox_street2,
                            'city': xero_pobox_partner_dict.get('City') or u'',
                            'state_id': xero_source_state_id.id if xero_source_state_id else False,
                            'country_id': xero_source_country_id.id if xero_source_country_id else False,
                            'zip': xero_pobox_partner_dict.get('PostalCode') or u'',
                            'xero_attention': xero_pobox_partner_dict.get('AttentionTo') or u'',
                            'xero_related_companies': [(0, 0, {'company_id': company_id})],
                            'parent_id': partner_id.id if partner_id else False})
                    for child_partner_dict in xero_partner.get('ContactPersons'):
                        self.create({
                            'type': 'contact',
                            'name': (child_partner_dict.get('FirstName') or u'') + ' ' + (child_partner_dict.get('LastName') or u''),
                            'xero_firstname': child_partner_dict.get('FirstName') or u'',
                            'xero_lastname': child_partner_dict.get('LastName') or u'',
                            'email': child_partner_dict.get('EmailAddress') or u'',
                            'xero_related_companies': [(0, 0, {'company_id': company_id})],
                            'parent_id': partner_id.id if partner_id else False,
                            })
                    self._cr.commit()


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    xero_partner_source_id = fields.Char(string='Xero Source Tag')

    def set_partner_group_to_odoo(self, partner_groups):
        for partner_source_dict in partner_groups:
            if partner_source_dict.get('Status') == 'ACTIVE':
                partner_source_id = self.search(['|', ('xero_partner_source_id', '=', partner_source_dict.get('ContactGroupID')),
                                            ('name', '=', partner_source_dict.get('Name'))], limit=1)
                if partner_source_id:
                    partner_source_id.write({'xero_partner_source_id': partner_source_dict.get('ContactGroupID'), 'active': True})
                else:
                    self.create({'name': partner_source_dict.get('Name'), 'xero_partner_source_id': partner_source_dict.get('ContactGroupID'), 'active': True})
                self._cr.commit()


class XeroCompany(models.Model):
    _name = 'xero.company'
    _description = 'Related Xero Company'

    xero_ref_id = fields.Char('Xero ContctID')
    company_id = fields.Many2one('res.company', string='Related Company', required=True)
    partner_id = fields.Many2one('res.partner', string='Related Partner')