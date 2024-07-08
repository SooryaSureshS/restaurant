# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
import datetime
import logging
import time

_logger = logging.getLogger(__name__)


class XeroAccountInvoiceLineLog(models.Model):
    _name = 'xero.account.invoice.line.log'
    _description = 'Account Invoice Line Logs'

    name = fields.Char('Name of Payment Line')
    xero_payment_id_log = fields.Char(string='Xero Payment Log', copy=False)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    xero_payment_ref_id = fields.Char('Xero Payment Reference', copy=False)


class AccountMove(models.Model):
    _inherit = 'account.move'

    xero_invoice_ref_id = fields.Char(string='Xero Invoice Ref', readonly=True, copy=False)
    xero_invoice_ref_no = fields.Char(string='Xero Invoice Number', readonly=True, copy=False)
    xero_tax_line_type = fields.Selection([
        ('Exclusive', 'Tax Exclusive'),
        ('Inclusive', 'Tax Inclusive'),
        ('NoTax', 'NoTax'),
        ], string='Xero Tax Type', default='Exclusive')
    xero_assign_creditnote = fields.Boolean(string='Xero Assign CreditNote')
    xero_journal = fields.Char(string='Xero Journal', readonly=True, copy=False)
    individual_journal = fields.Boolean(string='Individual Journal ?')

    ### Don't delete this method & action which is related to to this method
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(AccountMove, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if self._context.get('default_type') in ['out_receipt', 'in_receipt', 'entry'] and view_type == 'tree':
    #         for action in res.get('toolbar').get('action'):
    #             if action.get('name') == 'Export In Xero':
    #                 res.get('toolbar').get('action').remove(action)
    #     return res

    @api.model
    def default_get(self, default_fields):
        res = super(AccountMove, self).default_get(default_fields)
        tax_type = self.env['ir.config_parameter'].get_param('account.show_line_subtotals_tax_selection')
        if tax_type == 'tax_included':
            res['xero_tax_line_type'] = 'Inclusive'
        elif tax_type == 'tax_excluded':
            res['xero_tax_line_type'] = 'Exclusive'
        return res

    # Xero reconcile Creditnotes Payments
    def xero_reconcile_creditnote(self, partner, xero_invoice, invoice, type, company_id=False):
        ResPartner = self.env['res.partner']
        AccountMoveLine = self.env['account.move.line']
        for payment in xero_invoice.get('Allocations'):
            domain = [('move_id.xero_invoice_ref_id', '=', payment.get('Invoice').get('InvoiceID')),
                      ('partner_id', '=', ResPartner._find_accounting_partner(partner).id),
                      ('reconciled', '=', False),
                      '|',
                      '&', ('amount_residual_currency', '!=', 0.0), ('currency_id', '!=', None),
                      '&', ('amount_residual_currency', '=', 0.0), '&', ('currency_id', '=', None), ('amount_residual', '!=', 0.0)]
            if invoice.move_type in ('out_invoice', 'in_refund'):
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
            lines = AccountMoveLine.search(domain)
            if len(lines) != 0:
                invoice.with_context({'allocation_amount': payment['Amount']}).js_assign_outstanding_line(lines.id)
 
    # Import Payment and Reconcile from xero to odoo
    def set_payment_to_invoice_xero_to_odoo(self, xero, partner, xero_invoice_id, odoo_invoice_id, type, company_id=False):
        XeroXero = self.env['xero.xero']
        ResCompany = self.env['res.company']
        ResPartner = self.env['res.partner']
        ResCurrency = self.env['res.currency']
        AccountAccount = self.env['account.account']
        AccountInvoiceLineLog = self.env['xero.account.invoice.line.log']
        if partner and xero_invoice_id and odoo_invoice_id:
            invoice = odoo_invoice_id
            partner_id = ResPartner._find_accounting_partner(partner).id
            if xero_invoice_id.get('Payments'):
                for payment_id in xero_invoice_id.get('Payments'):
                    payment = xero.json_load_object_hook(payment_id)
                    payment_line = AccountInvoiceLineLog.search([('xero_payment_id_log', '=', payment.get('PaymentID'))])
                    currency_id = ResCurrency.search([('name', '=', xero_invoice_id.get('CurrencyCode'))], limit=1)
                    if not currency_id:
                        currencies = xero.xero_get_currency()
                        ResCurrency.set_currency_to_odoo(currencies, xero)
                        currency_id = ResCurrency.search([('name', '=', xero_invoice_id.get('CurrencyCode'))], limit=1)

                    if payment.get('PaymentID'):
                        if not xero.access_token or not xero.xero_referral_id:
                            raise Warning(_('Authentication Failed !\nPlease try again !'))
                        res = xero.get_import_data_xeroapi('Payments/%s' % payment.get('PaymentID'))
                        if not res:
                            return True
                        xero_payment_id = res.get('Payments')
                        payment_coa_id = xero.json_load_object_hook(xero_payment_id[0].get('Account'))
                        account_id = AccountAccount.search([('code', '=', payment_coa_id.get('Code')), ('linked_xero_account_id', '=', payment_coa_id.get('AccountID'))],limit=1)
                        if not account_id:
                            account_list = xero.xero_get_account()
                            AccountAccount.set_coa_to_odoo(account_list, xero, company_id=company_id, options='create')
                            account_id = AccountAccount.search([('code', '=', payment_coa_id.get('Code')), ('linked_xero_account_id', '=', payment_coa_id.get('AccountID'))],limit=1)

                        xero_account_id = XeroXero.search([('company_id', '=', company_id)], limit=1)
                        payment_journal_id = False
                        for journal in xero_account_id.journal_ids:
                            if journal.payment_debit_account_id.id == account_id.id or journal.payment_credit_account_id.id == account_id.id:
                                payment_journal_id = journal
                                break
                            elif journal.xero_linked_payment_account_id and journal.xero_linked_payment_account_id.id == account_id.id:
                                payment_journal_id = journal
                                break
                        if not payment_journal_id:
                            company_id = ResCompany.browse(company_id)
                            raise UserError(_("Please Add 'Payment Journal' for account \'%s %s\' of company \'%s\'.")% (account_id.code, account_id.name, company_id.name))

                    if not payment_line:
                        payment_vals = {
                                            # 'reconciled_invoice_ids': [(6, 0, invoice.ids)],
                                            'amount': payment.get('Amount'),
                                            'currency_id': currency_id and currency_id.id or False,
                                            'partner_id': partner_id,
                                            'company_id': company_id,
                                            'journal_id': payment_journal_id and payment_journal_id.id or False,
                                            'date': payment.get('Date') or fields.Date.today(),
                                            'partner_type': invoice[0].move_type in ('out_invoice', 'out_refund') and 'customer' or 'supplier',
                                            'xero_payment_ref_id': payment.get('PaymentID') or False,
                                            }
                        if type in ['out_invoice', 'in_refund']:
                            payment_vals.update({'payment_type':invoice.move_type in ('out_invoice', 'in_refund') and 'inbound' or 'outbound',
                                        'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id})
                        elif type in ['in_invoice', 'out_refund']:
                            payment_vals.update({'payment_type':invoice.move_type in ('in_invoice', 'out_refund') and 'outbound' or 'inbound',
                                        'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id})
                        account_payment_id = self.env['account.payment'].create([payment_vals])
                        account_payment_id.reconciled_invoice_ids = [(6, 0, invoice.ids)]
                        AccountInvoiceLineLog.create({'name': partner.name, 'xero_payment_id_log': payment.get('PaymentID')})
                        account_payment_id.reconciled_invoice_ids.state = 'posted'
                        if account_payment_id.reconciled_invoice_ids.state == 'posted':
                            if xero_invoice_id.get('CurrencyRate'):
                                account_payment_id.with_context({'CurrencyRate': payment.get('CurrencyRate')}).action_post()
                                liquidity_lines, counterpart_lines, writeoff_lines = account_payment_id._seek_for_lines()
                                if invoice.move_type in ('out_invoice', 'in_refund'):
                                    (counterpart_lines + invoice.line_ids.filtered(lambda line: line.account_internal_type == 'receivable')).reconcile()
                                elif invoice.move_type in ('in_invoice', 'out_refund'):
                                    (counterpart_lines + invoice.line_ids.filtered(lambda line: line.account_internal_type == 'payable')).reconcile()
                            else:
                                account_payment_id.action_post()
                                liquidity_lines, counterpart_lines, writeoff_lines = account_payment_id._seek_for_lines()
                                if invoice.move_type in ('out_invoice', 'in_refund'):
                                    (counterpart_lines + invoice.line_ids.filtered(lambda line: line.account_internal_type == 'receivable')).reconcile()
                                elif invoice.move_type in ('in_invoice', 'out_refund'):
                                    (counterpart_lines + invoice.line_ids.filtered(lambda line: line.account_internal_type == 'payable')).reconcile()
                            self._cr.commit()

    # Import Invoice from xero to odoo
    def set_invoice_to_odoo(self, invoices, xero, company_id=False, no_product=False, options=None, customer_journal_id=False, vendor_journal_id=False):
        AccountMoveLine = self.env['account.move.line']
        AccountMove = self.env['account.move']
        AccountTax = self.env['account.tax']
        AccountAccount = self.env['account.account']
        ProductProduct = self.env['product.product']
        ResPartner = self.env['res.partner']
        ResCurrency = self.env['res.currency']
        xero_id = self.env['xero.xero'].search([('company_id', '=', company_id)], limit=1)
        for invoice in invoices:
            invoice = xero.json_load_object_hook(invoice)
            if invoice.get('Total') != 0.0:
                invoice_id = self.search([('xero_invoice_ref_id', '=', invoice.get('InvoiceID'))], limit=1)
                if invoice_id and options in ['update', 'both']:
                    if invoice.get('Status') == 'VOIDED' and invoice_id.state == 'posted':
                        invoice_id.button_draft()
                    if invoice.get('Status') in ['DELETED', 'VOIDED'] and invoice_id.state == 'draft':
                        invoice_id.button_cancel()
                    if invoice_id.state != 'cancel' and invoice_id.payment_state != 'paid':
                        if invoice_id.state == 'draft':
                            exist_line_ids = []
                            flag = 0
                            if invoice:
                                child_tax = invoice.get('SubTotal') + invoice.get('TotalTax')
                                if float("%.2f"%child_tax) != invoice.get('Total'):
                                    flag = 1

                                move_lines = []
                                for lines in invoice.get('LineItems'):
                                    exist_line_ids.append(lines.get('LineItemID'))
                                    line_id = AccountMoveLine.search([('xero_move_line_id', '=', lines.get('LineItemID')),('company_id', '=', company_id)])
                                    if flag == 1:
                                        line_amount = lines.get('LineAmount') - lines.get('TaxAmount')
                                        unit_amount = line_amount / lines.get('Quantity')
                                    else:
                                        line_amount = lines.get('LineAmount')
                                        unit_amount = lines.get('UnitAmount')

                                    tax_id = False
                                    if lines.get('TaxType'):
                                        tax_id = AccountTax.search([('xero_type_tax_use', '=', lines.get('TaxType')),('company_id', '=', company_id)])

                                    account_id = AccountAccount.search([('code', '=', lines.get('AccountCode')),('company_id', '=', company_id)], limit=1)
                                    if not account_id and invoice.get('Type') == 'ACCREC':
                                        account_id = self.env['ir.property'].with_company(company_id)._get('property_account_income_categ_id', 'product.category')
                                    elif not account_id and invoice.get('Type') == 'ACCPAY':
                                        account_id = self.env['ir.property'].with_company(company_id)._get('property_account_expense_categ_id', 'product.category')
                                    if line_id:
                                        if lines.get('ItemCode'):
                                            if no_product:
                                                aml_vals = {'name': lines.get('Description') or 'Didn\'t specify',
                                                        'price_unit': unit_amount or 0.0,
                                                        'company_id': company_id,
                                                        'tax_ids': [(6, 0, [tax_id.id])] if tax_id else [],
                                                        'quantity': lines.get('Quantity') or 1,
                                                        'discount': lines.get('DiscountRate') or 0.0,
                                                        'xero_move_line_id': lines.get('LineItemID'),
                                                        'move_id': invoice_id.id,
                                                        }
                                                if account_id:
                                                    aml_vals.update({'account_id': account_id and account_id.id})
                                                    line_id.with_context({'check_move_validity': False, 'xero_tax_line_type': invoice.get('LineAmountTypes')}).write(aml_vals)
                                                    line_id.with_context({'check_move_validity': False, 'xero_tax_line_type': invoice.get('LineAmountTypes')})._onchange_mark_recompute_taxes()

                                            elif not no_product:
                                                product_ids = ProductProduct.search([('default_code', '=', lines.get('ItemCode'))])
                                                if not product_ids:
                                                    raise Warning("Please First Import Product.")
                                                for product_id in product_ids:
                                                    inv_line_rec = {'name': lines.get('Description') or product_id.description or 'Didn\'t specify',
                                                                    'price_unit': unit_amount or product_id.lst_price,
                                                                    'tax_base_amount': unit_amount or product_id.lst_price,
                                                                    'quantity': lines.get('Quantity') or 1,
                                                                    'company_id': company_id,
                                                                    'product_id': product_id and product_id.id or False,
                                                                    'tax_ids': [(6, 0, [tax_id.id])] if tax_id else [],
                                                                    'discount': lines.get('DiscountRate') or 0.0,
                                                                    'xero_move_line_id': lines.get('LineItemID'),
                                                                    'move_id': invoice_id.id,
                                                                    }
                                                    if account_id:
                                                        inv_line_rec.update({'account_id': account_id and account_id.id})
                                                        line_id.with_context({'check_move_validity': False, 'xero_tax_line_type': invoice.get('LineAmountTypes')}).write(inv_line_rec)
                                                        line_id.with_context({'check_move_validity': False, 'xero_tax_line_type': invoice.get('LineAmountTypes')})._onchange_mark_recompute_taxes()

                                        else:
                                            aml_vals = {'name': lines.get('Description') or 'Didn\'t specify',
                                                    'price_unit': unit_amount or 0.0,
                                                    'company_id': company_id,
                                                    'tax_ids': [(6, 0, [tax_id.id])] if tax_id else [],
                                                    'quantity': lines.get('Quantity') or 1,
                                                    'discount': lines.get('DiscountRate') or 0.0,
                                                    'xero_move_line_id': lines.get('LineItemID'),
                                                    'move_id': invoice_id.id,
                                                    }
                                            if account_id:
                                                aml_vals.update({'account_id': account_id and account_id.id})
                                                line_id.with_context({'check_move_validity': False, 'xero_tax_line_type': invoice.get('LineAmountTypes')}).write(aml_vals)
                                                line_id.with_context({'check_move_validity': False, 'xero_tax_line_type': invoice.get('LineAmountTypes')})._onchange_mark_recompute_taxes()

                                    else:
                                        if lines.get('ItemCode'):
                                            if no_product:
                                                aml_vals = {'name': lines.get('Description') or 'Didn\'t specify',
                                                        'price_unit': unit_amount or 0.0,
                                                        'company_id': company_id,
                                                        'tax_ids': [(6, 0, [tax_id.id])] if tax_id else [],
                                                        'quantity': lines.get('Quantity') or 1,
                                                        'discount': lines.get('DiscountRate') or 0.0,
                                                        'xero_move_line_id': lines.get('LineItemID'),
                                                        'move_id': invoice_id.id,
                                                        }
                                                if account_id:
                                                    aml_vals.update({'account_id': account_id and account_id.id})
                                                    move_lines.append(aml_vals)
                                            elif not no_product:
                                                product_ids = ProductProduct.search([('default_code', '=', lines.get('ItemCode'))])
                                                if not product_ids:
                                                    raise Warning("Please First Import Product.")
                                                for product_id in product_ids:
                                                    inv_line_rec = {'name': lines.get('Description') or product_id.description or 'Didn\'t specify',
                                                                    'price_unit': unit_amount or product_id.lst_price,
                                                                    'quantity': lines.get('Quantity') or 1,
                                                                    'company_id': company_id,
                                                                    'product_id': product_id and product_id.id or False,
                                                                    'tax_ids': [(6, 0, [tax_id.id])] if tax_id else [],
                                                                    'discount': lines.get('DiscountRate') or 0.0,
                                                                    'xero_move_line_id': lines.get('LineItemID'),
                                                                    'move_id': invoice_id.id,
                                                                    }
                                                    if account_id:
                                                        inv_line_rec.update({'account_id': account_id and account_id.id})
                                                        move_lines.append(inv_line_rec)
                                        else:
                                            aml_vals = {'name': lines.get('Description') or 'Didn\'t specify',
                                                    'price_unit': unit_amount or 0.0,
                                                    'company_id': company_id,
                                                    'tax_ids': [(6, 0, [tax_id.id])] if tax_id else [],
                                                    'quantity': lines.get('Quantity') or 1,
                                                    'discount': lines.get('DiscountRate') or 0.0,
                                                    'xero_move_line_id': lines.get('LineItemID'),
                                                    'move_id': invoice_id.id,
                                                    }
                                            if account_id:
                                                aml_vals.update({'account_id': account_id and account_id.id})
                                                move_lines.append(aml_vals)

                                if move_lines:
                                    line_ids = AccountMoveLine.with_context({'check_move_validity': False, 'xero_tax_line_type': invoice.get('LineAmountTypes')}).create(move_lines)

                                if invoice['Type'] == 'ACCREC':
                                    xero_type = 'out_invoice'
                                else:
                                    xero_type = 'in_invoice'

                                partner = ResPartner.search(['|', ('company_id', '=', company_id), ('company_id', '=', False)]).filtered(lambda partner: partner.xero_related_companies.filtered(lambda contact: contact.xero_ref_id == invoice.get('Contact').get('ContactID') and contact.company_id.id == company_id))
                                if not partner:
                                    xero_id.xero_get_contact()
                                    partner = ResPartner.search(['|', ('company_id', '=', company_id), ('company_id', '=', False)]).filtered(lambda partner: partner.xero_related_companies.filtered(lambda contact: contact.xero_ref_id == invoice.get('Contact').get('ContactID') and contact.company_id.id == company_id))

                                currency_id = ResCurrency.search([('name', '=', invoice.get('CurrencyCode'))])

                                aml_vals = {
                                    'partner_id': partner and partner[0].id or False,
                                    'currency_id': currency_id and currency_id.id or False,
                                    'invoice_date': invoice.get('DateString'),
                                    'invoice_date_due': invoice.get('DueDateString'),
                                    'xero_invoice_ref_id': invoice.get('InvoiceID'),
                                    'xero_invoice_ref_no': invoice.get('InvoiceNumber'),
                                    'amount_tax': invoice.get('TotalTax'),
                                    'move_type': xero_type,
                                    'company_id': company_id,
                                    'xero_tax_line_type': invoice.get('LineAmountTypes'),
                                }
                                context = dict(self.env.context)
                                context.update({'check_move_validity': False, 'xero_tax_line_type': invoice.get('LineAmountTypes')})
                                self.env.context = context
                                invoice_id.write(aml_vals)
                                if context.get('check_move_validity'):
                                    del context['check_move_validity']
                                    self.env.context = context
                                invoice_id._compute_amount()
                                for invoice_lines in invoice_id.invoice_line_ids:
                                    if invoice_lines.xero_move_line_id not in exist_line_ids:
                                        invoice_lines.unlink()
                                invoice_id._onchange_invoice_line_ids()
                                invoice_id._compute_invoice_taxes_by_group()

                        if invoice.get('Status') == 'AUTHORISED' and invoice_id.state in ['draft', 'posted'] and invoice_id.invoice_line_ids:
                            if invoice_id.state == 'draft':
                                invoice_id.with_context({'CurrencyRate': invoice.get('CurrencyRate')}).action_post()
                            if invoice.get('AmountPaid') != 0.0 or invoice.get('Total') !=  invoice.get('AmountDue'):
                                if invoice_id.move_type in ('out_invoice', 'out_refund') and invoice.get('Type') == 'ACCREC':
                                    self.set_payment_to_invoice_xero_to_odoo(xero, invoice_id.partner_id, invoice, invoice_id, type='out_invoice', company_id=company_id)
                                else:
                                    self.set_payment_to_invoice_xero_to_odoo(xero, invoice_id.partner_id, invoice, invoice_id, type='out_invoice', company_id=company_id)
                        if invoice.get('Status') == 'PAID' and invoice_id.state in ['draft', 'posted'] and invoice_id.invoice_line_ids:
                            if invoice_id.state == 'draft':
                                invoice_id.with_context({'CurrencyRate': invoice.get('CurrencyRate')}).action_post()
                            if invoice_id.move_type in ('out_invoice', 'out_refund') and invoice.get('Type') == 'ACCREC':
                                self.set_payment_to_invoice_xero_to_odoo(xero, invoice_id.partner_id, invoice, invoice_id, type='out_invoice', company_id=company_id)
                            else:
                                self.set_payment_to_invoice_xero_to_odoo(xero, invoice_id.partner_id, invoice, invoice_id, type='out_invoice', company_id=company_id)

                elif not invoice_id and options in ['create', 'both']:
                    flag = 0
                    if invoice and invoice.get('Status') not in ['DELETED', 'VOIDED']:
                        partner = ResPartner.search(['|', ('company_id', '=', company_id), ('company_id', '=', False)]).filtered(lambda partner: partner.xero_related_companies.filtered(lambda contact: contact.xero_ref_id == invoice.get('Contact').get('ContactID') and contact.company_id.id == company_id))
                        if not partner:
                            xero_id.xero_get_contact()
                            partner = ResPartner.search(['|', ('company_id', '=', company_id), ('company_id', '=', False)]).filtered(lambda partner: partner.xero_related_companies.filtered(lambda contact: contact.xero_ref_id == invoice.get('Contact').get('ContactID') and contact.company_id.id == company_id))

                        invoice_lines = []
                        child_tax = invoice.get('SubTotal') + invoice.get('TotalTax')
                        if float("%.2f"%child_tax) != invoice.get('Total'):
                            flag = 1

                        for lines in invoice.get('LineItems'):
                            account_id = AccountAccount.search([('code', '=', lines.get('AccountCode')),('company_id', '=', company_id)])
                            if not account_id and invoice.get('Type') == 'ACCREC':
                                account_id = self.env['ir.property'].with_company(company_id)._get('property_account_income_categ_id', 'product.category')
                            elif not account_id and invoice.get('Type') == 'ACCPAY':
                                account_id = self.env['ir.property'].with_company(company_id)._get('property_account_expense_categ_id', 'product.category')

                            if flag == 1:
                                line_amount = lines.get('LineAmount', 0.0) - lines.get('TaxAmount', 0.0)
                                unit_amount = (line_amount / lines.get('Quantity')) if line_amount else 0.0
                            else:
                                line_amount = lines.get('LineAmount', 0.0)
                                unit_amount = lines.get('UnitAmount', 0.0)

                            tax_id = False
                            if lines.get('TaxType'):
                                tax_id = AccountTax.search([('xero_type_tax_use', '=', lines.get('TaxType')),('company_id', '=', company_id)])

                            if lines.get('ItemCode'):
                                if no_product:
                                    aml_vals = {'name': lines.get('Description') or 'Didn\'t specify',
                                            'price_unit': unit_amount or 0.0,
                                            'company_id': company_id,
                                            'tax_ids': [(6, 0, tax_id.ids)] if tax_id else [],
                                            'account_id': account_id and account_id.id or False,
                                            'quantity': lines.get('Quantity') or 1,
                                            'discount': lines.get('DiscountRate') or 0.0,
                                            'xero_move_line_id': lines.get('LineItemID'),
                                            }
                                    if account_id:
                                        aml_vals.update({'account_id': account_id and account_id.id})
                                        invoice_lines.append((0, 0, aml_vals))

                                elif not no_product:
                                    product_ids = ProductProduct.search([('default_code', '=', lines.get('ItemCode'))])
                                    if not product_ids:
                                        raise Warning("Please First Import Product.")
                                    for product_id in product_ids:
                                        inv_line_rec = {'name': lines.get('Description') or product_id.description or 'Didn\'t specify',
                                                        'price_unit': unit_amount,
                                                        'company_id': company_id,
                                                        'quantity': lines.get('Quantity') or 1,
                                                        'product_id': product_id and product_id.id or False,
                                                        'tax_ids': [(6, 0, tax_id.ids)] if tax_id else [],
                                                        'discount': lines.get('DiscountRate') or 0.0,
                                                        'xero_move_line_id': lines.get('LineItemID'),
                                                        }
                                        if account_id:
                                            inv_line_rec.update({'account_id': account_id.id})
                                            invoice_lines.append((0, 0, inv_line_rec))
                            else:
                                aml_vals = {'name': lines.get('Description') or 'Didn\'t specify',
                                        'price_unit': unit_amount or 0.0,
                                        'company_id': company_id,
                                        'tax_ids': [(6, 0, tax_id.ids)] if tax_id else [],
                                        'account_id': account_id and account_id.id or False,
                                        'quantity': lines.get('Quantity') or 1,
                                        'discount': lines.get('DiscountRate') or 0.0,
                                        'xero_move_line_id': lines.get('LineItemID'),
                                        }
                                if account_id:
                                    aml_vals.update({'account_id': account_id and account_id.id})
                                    invoice_lines.append((0, 0, aml_vals))

                        if invoice['Type'] == 'ACCREC':
                            xero_type = 'out_invoice'
                        else:
                            xero_type = 'in_invoice'

                        currency_id = ResCurrency.search([('name', '=', invoice.get('CurrencyCode'))], limit=1)
                        if invoice.get('Type') == 'ACCREC':
                            journal_id = customer_journal_id
                        elif invoice.get('Type') == 'ACCPAY':
                            journal_id = vendor_journal_id
                        invoice_vals = {'partner_id': partner and partner.id or False,
                                       'currency_id': currency_id and currency_id.id or False,
                                       'company_id': company_id,
                                       'journal_id': journal_id and journal_id.id or False,
                                       'invoice_date': invoice.get('DateString'),
                                       'invoice_date_due': invoice.get('DueDateString'),
                                       'xero_invoice_ref_id': invoice.get('InvoiceID'),
                                       'xero_invoice_ref_no': invoice.get('InvoiceNumber'),
                                       'amount_tax': invoice.get('TotalTax'),
                                       'move_type': xero_type,
                                       'xero_tax_line_type':invoice.get('LineAmountTypes'),
                                       }
                        invoice_type = self.env.context.copy()
                        invoice_type.update({'type': xero_type, 'xero_tax_line_type': invoice.get('LineAmountTypes')})
                        if invoice_lines:
                            invoice_vals.update({'invoice_line_ids': invoice_lines})

                        move_id = AccountMove.with_context(invoice_type).create(invoice_vals)
                        move_id._compute_amount()
                        move_id._onchange_invoice_line_ids()
                        self._cr.commit()
                        
                        if move_id and invoice.get('Status') in ['AUTHORISED', 'PAID'] and move_id.invoice_line_ids:
                            if move_id.state == 'draft':
                                move_id.with_context({'CurrencyRate': invoice.get('CurrencyRate')}).action_post()

                            if move_id and invoice.get('Status') == 'AUTHORISED':
                                if invoice.get('AmountPaid') != 0.0 or invoice.get('Total') !=  invoice.get('AmountDue'):
                                    if move_id.move_type in ['out_invoice', 'out_refund']:
                                        self.set_payment_to_invoice_xero_to_odoo(xero, move_id.partner_id, invoice, move_id, type='out_invoice', company_id=company_id)
                                    else:
                                        self.set_payment_to_invoice_xero_to_odoo(xero, move_id.partner_id, invoice, move_id, type='out_invoice', company_id=company_id)
                            if move_id and invoice.get('Status') == 'PAID':
                                if move_id.move_type in ['out_invoice', 'out_refund']:
                                    self.set_payment_to_invoice_xero_to_odoo(xero, move_id.partner_id, invoice, move_id, type='out_invoice', company_id=company_id)
                                else:
                                    self.set_payment_to_invoice_xero_to_odoo(xero, move_id.partner_id, invoice, move_id, type='out_invoice', company_id=company_id)

    # Import Refund Invoice from xero to odoo
    def set_refund_invoice_to_odoo(self, refund_invoices, xero, company_id=False, no_product=False, options=None, customer_journal_id=False, vendor_journal_id=False):
        ResPartner = self.env['res.partner']
        ResCurrency = self.env['res.currency']
        AccountAccount = self.env['account.account']
        ProductProduct = self.env['product.product']
        IrProperty = self.env['ir.property']
        AccountTax = self.env['account.tax']
        xero_id = self.env['xero.xero'].search([('company_id', '=', company_id)], limit=1)
        for refund_invoice in refund_invoices:
            refund_invoice = xero.json_load_object_hook(refund_invoice)
            invoice_vals = {}
            if refund_invoice.get('Total') != 0.0:
                exist_refund_invoice = self.search([('xero_invoice_ref_id', '=', refund_invoice.get('CreditNoteID')), ('xero_invoice_ref_no','=', refund_invoice.get('CreditNoteNumber')), ('company_id', '=', company_id)], limit=1)

                if exist_refund_invoice and exist_refund_invoice.state == 'draft' and options in ['update', 'both']:
                    exist_refund_invoice.invoice_line_ids.unlink()

                invoice_type = 'out_refund' if refund_invoice['Type'] == 'ACCRECCREDIT' else 'in_refund'
                if exist_refund_invoice.state == 'draft' or not exist_refund_invoice:
                    partner_id = ResPartner.search(['|', ('company_id', '=', company_id), ('company_id', '=', False)]).filtered(lambda partner: partner.xero_related_companies.filtered(lambda contact: contact.xero_ref_id == refund_invoice.get('Contact').get('ContactID') and contact.company_id.id == company_id))
                    if not partner_id:
                        xero_id.xero_get_contact()
                        partner_id = ResPartner.search(['|', ('company_id', '=', company_id), ('company_id', '=', False)]).filtered(lambda partner: partner.xero_related_companies.filtered(lambda contact: contact.xero_ref_id == refund_invoice.get('Contact').get('ContactID') and contact.company_id.id == company_id))

                    if refund_invoice.get('Type') == 'ACCRECCREDIT':
                        journal_id = customer_journal_id
                    elif refund_invoice.get('Type') == 'ACCPAYCREDIT':
                        journal_id = vendor_journal_id
                    
                    currency_id = ResCurrency.search([('name', '=', refund_invoice.get('CurrencyCode'))], limit=1)
                    invoice_vals.update({'partner_id': partner_id.id or False,
                                        'currency_id': currency_id and currency_id.id or False,
                                        'invoice_date': refund_invoice.get('DateString'),
                                        'invoice_date_due': refund_invoice.get('DueDateString'),
                                        'xero_invoice_ref_no': refund_invoice.get('CreditNoteNumber'),
                                        'xero_invoice_ref_id': refund_invoice.get('CreditNoteID'),
                                        'amount_tax': refund_invoice.get('TotalTax'),
                                        'move_type': invoice_type,
                                        'journal_id': journal_id and journal_id.id or False,
                                        'company_id': company_id,
                                        'invoice_line_ids': [],
                                        'xero_tax_line_type': refund_invoice.get('LineAmountTypes')})

                    invoice_lines = []
                    for line in refund_invoice.get('LineItems'):
                        product_id = False
                        account_id = AccountAccount.search([('code', '=', line.get('AccountCode')), ('company_id', '=', company_id)], limit=1)
                        if line.get('ItemCode'):
                            product_id = ProductProduct.search([('default_code', '=', line.get('ItemCode'))], limit=1)
                        if product_id:
                            if refund_invoice['Type'] == 'ACCRECCREDIT':
                                account_id = product_id.property_account_income_id or product_id.categ_id.property_account_income_categ_id
                            else:
                                account_id = product_id.property_account_expense_id or product_id.categ_id.property_account_expense_categ_id
                        if not account_id and refund_invoice['Type'] == 'ACCRECCREDIT':
                            account_id = IrProperty.with_company(company_id)._get('property_account_income_categ_id', 'product.category')
                        elif not account_id and refund_invoice['Type'] == 'ACCPAYCREDIT':
                            account_id = IrProperty.with_company(company_id)._get('property_account_expense_categ_id', 'product.category')

                        tax_id = False
                        if line.get('TaxType'):
                            tax_id = AccountTax.search([('xero_type_tax_use', '=', line.get('TaxType')), ('company_id', '=', company_id)])

                        if line.get('ItemCode'):
                            if no_product:
                                inv_line_data = {
                                        'name': line.get('Description') or 'Didn\'t specify',
                                        'price_unit': line.get('UnitAmount') or 0.0,
                                        'company_id': company_id,
                                        'tax_ids': [(6, 0, tax_id.ids)] if tax_id else [],
                                        'account_id': account_id.id,
                                        'quantity': line.get('Quantity') or 1}
                                invoice_lines.append((0, 0, inv_line_data))
                            elif not no_product:
                                if not product_id:
                                    raise Warning("Please First Import Product.")
                                inv_line_data = {
                                        'product_id': product_id.id,
                                        'name': (line.get('Description') or product_id.description or product_id.name),
                                        'price_unit': line.get('UnitAmount') or 0.0,
                                        'company_id': company_id,
                                        'tax_ids': [(6, 0, tax_id.ids)] if tax_id else [],
                                        'account_id': account_id.id,
                                        'quantity': line.get('Quantity') or 1}
                                invoice_lines.append((0, 0, inv_line_data))
                        else:
                            inv_line_data = {
                                        'name': line.get('Description') or 'Didn\'t specify',
                                        'price_unit': line.get('UnitAmount') or 0.0,
                                        'company_id': company_id,
                                        'tax_ids': [(6, 0, tax_id.ids)] if tax_id else [],
                                        'account_id': account_id.id,
                                        'quantity': line.get('Quantity') or 1}
                            invoice_lines.append((0, 0, inv_line_data))

                    invoice_vals.update({'invoice_line_ids': invoice_lines})
                if exist_refund_invoice and options in ['update', 'both']:
                    if exist_refund_invoice.state == 'posted' and refund_invoice.get('Status') == 'VOIDED':
                        exist_refund_invoice.button_draft()
                    if exist_refund_invoice.state == 'draft' and refund_invoice.get('Status') in ['DELETED', 'VOIDED']:
                        exist_refund_invoice.button_cancel()
                    if exist_refund_invoice.state != 'cancel' and exist_refund_invoice.payment_state != 'paid':
                        context = self.env.context.copy()
                        context.update({'move_type': invoice_type, 'check_move_validity': False, 'xero_tax_line_type': refund_invoice.get('LineAmountTypes')})
                        exist_refund_invoice.with_context(context).write(invoice_vals)
                        exist_refund_invoice._compute_amount()
                        exist_refund_invoice._onchange_invoice_line_ids()
                        self._cr.commit()
                elif not exist_refund_invoice and options in ['create', 'both']:
                    if refund_invoice.get('Status') not in ['VOIDED', 'DELETED']:
                        context = self.env.context.copy()
                        context.update({'move_type': invoice_type, 'check_move_validity': False, 'xero_tax_line_type': refund_invoice.get('LineAmountTypes')})
                        exist_refund_invoice = self.with_context(context).create(invoice_vals)
                        exist_refund_invoice._compute_amount()
                        exist_refund_invoice._onchange_invoice_line_ids()
                        self._cr.commit()

                if exist_refund_invoice.state != 'cancel' and exist_refund_invoice.payment_state != 'paid':
                    if refund_invoice.get('Status') in ['AUTHORISED', 'PAID'] and exist_refund_invoice.invoice_line_ids:
                        if exist_refund_invoice.state == 'draft':
                            exist_refund_invoice.with_context({'CurrencyRate': refund_invoice.get('CurrencyRate')}).action_post()
                        if refund_invoice.get('Payments'):
                            self.set_payment_to_invoice_xero_to_odoo(xero, exist_refund_invoice.partner_id, refund_invoice, exist_refund_invoice, type=exist_refund_invoice.move_type, company_id=company_id)
                        if refund_invoice.get('Allocations') and refund_invoice.get('Status') == 'PAID':
                            self.xero_reconcile_creditnote(exist_refund_invoice.partner_id, refund_invoice, exist_refund_invoice, type=exist_refund_invoice.move_type, company_id=company_id)

    # Import Journals from xero to odoo
    def set_journal_to_odoo(self, journals, xero, company_id=False, options=None):
        AccountTax = self.env['account.tax']
        for journal in journals:
            journal = xero.json_load_object_hook(journal)
            journal_id = self.search([('xero_journal', '=', journal.get('ManualJournalID'))], limit=1)

            if journal_id and journal_id.state == 'draft' and options in ['update', 'both'] and journal.get('Status') in ['DRAFT', 'POSTED']:
                journal_id.write({
                    'date': journal.get('Date'),
                    'ref': journal.get('Narration'),
                    'xero_tax_line_type': journal.get('LineAmountTypes'),
                    })
                
                journal_id.line_ids.unlink()
                journal_lines = []
                for line in journal.get('JournalLines'):
                    account_id = self.env['account.account'].search([('code', '=', line.get('AccountCode')), ('company_id', '=', company_id)], limit=1)
                    if not account_id:
                        _logger.info("Account Code '%s' is not available. Please First Import Chart of Account.", line.get('AccountCode'))
                        raise Warning(("Account Code '%s' is not available. Please First Import Chart of Account.") % line.get('AccountCode'))

                    credit = debit = 0
                    if journal.get('LineAmountTypes') == 'Exclusive':
                        if '-' in str(line.get('LineAmount')):
                            credit = abs(line.get('LineAmount'))
                        else:
                            debit = line.get('LineAmount')

                        credit_tax = debit_tax = 0
                        journal_line_vals = {}
                        if line.get('TaxType') and line.get('TaxAmount') != 0:
                            tax_id = AccountTax.search([('xero_type_tax_use', '=', line.get('TaxType')), ('company_id', '=', company_id)], limit=1)
                            
                            journal_line_vals = {'tax_ids': [(6, 0, tax_id.ids)]}
                            if '-' in str(line.get('TaxAmount')):
                                credit_tax = abs(line.get('TaxAmount'))
                            else:
                                debit_tax = line.get('TaxAmount')

                            for tax in tax_id.invoice_repartition_line_ids:
                                if tax.repartition_type == 'tax':
                                    journal_lines.append((0, 0, {
                                      'account_id': tax.account_id.id if tax.account_id else account_id.id,
                                      'name': tax_id.name,
                                      'debit': debit_tax,
                                      'credit': credit_tax,
                                      'move_id': journal_id.id,
                                      }))

                    elif journal.get('LineAmountTypes') == 'Inclusive':
                        credit_tax = debit_tax = 0
                        journal_line_vals = {}
                        if line.get('TaxType') and line.get('TaxAmount') != 0:
                            tax_id = AccountTax.search([('xero_type_tax_use', '=', line.get('TaxType')), ('company_id', '=', company_id)], limit=1)
                            journal_line_vals = {'tax_ids': [(6, 0, tax_id.ids)]}
                            if '-' in str(line.get('TaxAmount')):
                                credit_tax = abs(line.get('TaxAmount'))
                            else:
                                debit_tax = line.get('TaxAmount')

                            for tax in tax_id.invoice_repartition_line_ids:
                                if tax.repartition_type == 'tax':
                                    journal_lines.append((0, 0, {
                                      'account_id': tax.account_id.id if tax.account_id else account_id.id,
                                      'name': tax_id.name,
                                      'debit': debit_tax,
                                      'credit': credit_tax,
                                      'move_id': journal_id.id,
                                      }))
                        if '-' in str(line.get('LineAmount')):
                            credit = abs(line.get('LineAmount')) - credit_tax
                        else:
                            debit = line.get('LineAmount') - debit_tax

                    elif journal.get('LineAmountTypes') == 'NoTax':
                        journal_line_vals = {}
                        credit = debit = 0
                        if '-' in str(line.get('LineAmount')):
                            credit = abs(line.get('LineAmount'))
                        else:
                            debit = line.get('LineAmount')

                    journal_line_vals.update({
                          'account_id': account_id.id,
                          'name': line.get('Description'),
                          'debit': debit,
                          'credit': credit,
                          'move_id': journal_id.id,
                          })

                    journal_lines.append((0, 0, journal_line_vals))
                journal_id.write({'line_ids': journal_lines})
                journal_id._onchange_recompute_dynamic_lines()

                if journal.get('Status').lower() == 'posted':
                    journal_id.post()
                self._cr.commit()

            elif not journal_id and options in ['create', 'both'] and journal.get('Status') in ['DRAFT','POSTED']:
                xero_account_id = self.env['xero.xero'].search([('company_id', '=', company_id)], limit=1)
                journal_id = self.create({
                    'date': journal.get('Date'),
                    'ref': journal.get('Narration'),
                    'xero_tax_line_type': journal.get('LineAmountTypes'),
                    'journal_id': xero_account_id.misc_journal_id.id,
                    'xero_journal': journal.get('ManualJournalID'),
                    'individual_journal': True,
                    })

                journal_lines = []
                for line in journal.get('JournalLines'):
                    account_id = self.env['account.account'].search([('code', '=', line.get('AccountCode')),('company_id', '=', company_id)], limit=1)

                    if not account_id:
                        _logger.info("Account Code '%s' is not available. Please First Import Chart of Account.",line.get('AccountCode'))
                        raise Warning(("Account Code '%s' is not available. Please First Import Chart of Account.") % line.get('AccountCode'))

                    credit = debit = 0

                    if journal.get('LineAmountTypes') == 'Exclusive':
                        if '-' in str(line.get('LineAmount')):
                            credit = abs(line.get('LineAmount'))
                        else:
                            debit = line.get('LineAmount')

                        credit_tax = debit_tax = 0
                        journal_line_vals = {}
                        if line.get('TaxType') and line.get('TaxAmount') != 0:
                            tax_id = AccountTax.search([('xero_type_tax_use', '=', line.get('TaxType')),('company_id', '=', company_id)], limit=1)
                            journal_line_vals = {'tax_ids': [(6, 0, tax_id.ids)]}
                            if '-' in str(line.get('TaxAmount')):
                                credit_tax = abs(line.get('TaxAmount'))
                            else:
                                debit_tax = line.get('TaxAmount')

                            for tax in tax_id.invoice_repartition_line_ids:
                                if tax.repartition_type == 'tax':
                                    journal_lines.append((0, 0, {
                                      'account_id': tax.account_id.id if tax.account_id else account_id.id,
                                      'name': tax_id.name,
                                      'debit': debit_tax,
                                      'credit': credit_tax,
                                      'move_id': journal_id.id,
                                      }))

                    elif journal.get('LineAmountTypes') == 'Inclusive':
                        credit_tax = debit_tax = 0
                        journal_line_vals = {}
                        if line.get('TaxType') and line.get('TaxAmount') != 0:
                            tax_id = AccountTax.search([('xero_type_tax_use', '=', line.get('TaxType')),('company_id', '=', company_id)], limit=1)
                            journal_line_vals = {'tax_ids': [(6, 0, tax_id.ids)]}

                            if '-' in str(line.get('TaxAmount')):
                                credit_tax = abs(line.get('TaxAmount'))
                            else:
                                debit_tax = line.get('TaxAmount')

                            for tax in tax_id.invoice_repartition_line_ids:
                                if tax.repartition_type == 'tax':
                                    journal_lines.append((0, 0, {
                                      'account_id': tax.account_id.id if tax.account_id else account_id.id,
                                      'name': tax_id.name,
                                      'debit': debit_tax,
                                      'credit': credit_tax,
                                      'move_id': journal_id.id,
                                      }))
                        if '-' in str(line.get('LineAmount')):
                            credit = abs(line.get('LineAmount')) - credit_tax
                        else:
                            debit = line.get('LineAmount') - debit_tax

                    elif journal.get('LineAmountTypes') == 'NoTax':
                        credit = debit = 0
                        journal_line_vals = {}
                        if '-' in str(line.get('LineAmount')):
                            credit = abs(line.get('LineAmount'))
                        else:
                            debit = line.get('LineAmount')

                    journal_line_vals.update({'account_id': account_id.id,
                                         'name': line.get('Description'),
                                         'debit': debit,
                                         'credit': credit,
                                         'move_id': journal_id.id,
                                         })
                    journal_lines.append((0, 0, journal_line_vals))

                journal_id.write({'line_ids': journal_lines})
                journal_id._onchange_recompute_dynamic_lines()
                if journal.get('Status').lower() == 'posted':
                    journal_id.post()
                self._cr.commit()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    xero_move_line_id = fields.Char('Xero Move Line Ref', readonly=True, copy=False)
    xero_move_payment_id = fields.Char('Xero Move Releted Payment ID', readonly=True, copy=False)

    def _reconcile_lines(self, debit_moves, credit_moves, field):
        """ This function loops on the 2 recordsets given as parameter as long as it
            can find a debit and a credit to reconcile together. It returns the recordset of the
            account move lines that were not reconciled during the process.
        """
        if self._context.get('allocation_amount'):
            (debit_moves + credit_moves).read([field])
            to_create = []
            cash_basis = debit_moves and debit_moves[0].account_id.internal_type in ('receivable', 'payable') or False
            cash_basis_percentage_before_rec = {}
            dc_vals ={}
            while (debit_moves and credit_moves):
                debit_move = debit_moves[0]
                credit_move = credit_moves[0]
                company_currency = debit_move.company_id.currency_id
                # We need those temporary value otherwise the computation might be wrong below
                temp_amount_residual = min(debit_move.amount_residual, -credit_move.amount_residual)
                temp_amount_residual_currency = min(debit_move.amount_residual_currency, -credit_move.amount_residual_currency)
                dc_vals[(debit_move.id, credit_move.id)] = (debit_move, credit_move, temp_amount_residual_currency)
                amount_reconcile = min(debit_move[field], -credit_move[field])

                #Remove from recordset the one(s) that will be totally reconciled
                # For optimization purpose, the creation of the partial_reconcile are done at the end,
                # therefore during the process of reconciling several move lines, there are actually no recompute performed by the orm
                # and thus the amount_residual are not recomputed, hence we have to do it manually.
                if amount_reconcile == debit_move[field]:
                    debit_moves -= debit_move
                else:
                    debit_moves[0].amount_residual -= temp_amount_residual
                    debit_moves[0].amount_residual_currency -= temp_amount_residual_currency

                if amount_reconcile == -credit_move[field]:
                    credit_moves -= credit_move
                else:
                    credit_moves[0].amount_residual += temp_amount_residual
                    credit_moves[0].amount_residual_currency += temp_amount_residual_currency
                #Check for the currency and amount_currency we can set
                currency = False
                amount_reconcile_currency = 0
                if field == 'amount_residual_currency':
                    currency = credit_move.currency_id.id
                    amount_reconcile_currency = temp_amount_residual_currency
                    amount_reconcile = temp_amount_residual

                if cash_basis:
                    tmp_set = debit_move | credit_move
                    cash_basis_percentage_before_rec.update(tmp_set._get_matched_percentage())

                to_create.append({
                    'debit_move_id': debit_move.id,
                    'credit_move_id': credit_move.id,
                    'amount': self._context.get('allocation_amount'),
                    'amount_currency': amount_reconcile_currency,
                    'currency_id': currency,
                })

            cash_basis_subjected = []
            part_rec = self.env['account.partial.reconcile']
            for partial_rec_dict in to_create:
                debit_move, credit_move, amount_residual_currency = dc_vals[partial_rec_dict['debit_move_id'], partial_rec_dict['credit_move_id']]
                # /!\ NOTE: Exchange rate differences shouldn't create cash basis entries
                # i. e: we don't really receive/give money in a customer/provider fashion
                # Since those are not subjected to cash basis computation we process them first
                if not amount_residual_currency and debit_move.currency_id and credit_move.currency_id:
                    part_rec.create(partial_rec_dict)
                else:
                    cash_basis_subjected.append(partial_rec_dict)

            for after_rec_dict in cash_basis_subjected:
                new_rec = part_rec.create(after_rec_dict)
                # if the pair belongs to move being reverted, do not create CABA entry
                if cash_basis and not (
                        new_rec.debit_move_id.move_id == new_rec.credit_move_id.move_id.reversed_entry_id
                        or
                        new_rec.credit_move_id.move_id == new_rec.debit_move_id.move_id.reversed_entry_id
                ):
                    new_rec.create_tax_cash_basis_entry(cash_basis_percentage_before_rec)
            return debit_moves+credit_moves
        else:
            return super(AccountMoveLine, self)._reconcile_lines(debit_moves, credit_moves, field)
