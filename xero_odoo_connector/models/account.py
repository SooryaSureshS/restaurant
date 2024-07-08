# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from datetime import datetime
import math
import time
from odoo.tools.float_utils import float_round as round

USER_ACCOUNT_TYPE = [
            ### Map Xero Account User Type with Odoo Account User Type
            ('current', 'CURRENT ACCOUNT'),
            ('bank', 'BANK ACCOUNT'),
            ('fixed', 'FIXED ACCOUNT'),
            ('superannuationexpense', 'SUPERANNUATIONEXPENSE ACCOUNT'),
            ('inventory', 'INVENTORY ACCOUNT'),
            ('revenue', 'REVENUE ACCOUNT'),
            ('noncurrent', 'NONCURRENT ACCOUNT'),
            ('currliab', 'CURRLIAB ACCOUNT'),
            ('termliab', 'TERMLIAB ACCOUNT'),
            ('equity', 'EQUITY ACCOUNT'),
            ('liability', 'LIABILITY ACCOUNT'),
            ('directcosts', 'DIRECTCOSTS ACCOUNT'),
            ('prepayment', 'PREPAYMENT ACCOUNT'),
            ('overheads', 'OVERHEADS ACCOUNT'),
            ('wagespayableliability', 'WAGESPAYABLELIABILITY ACCOUNT'),
            ('paygliability', 'PAYGLIABILITY ACCOUNT'),
            ('depreciatn', 'DEPRECIATN ACCOUNT'),
            ('superannuationliability', 'SUPERANNUATIONLIABILITY ACCOUNT'),
            ('sales', 'SALES ACCOUNT'),
            ('expense', 'EXPENSE ACCOUNT'),
            ('otherincome', 'OTHERINCOME ACCOUNT'),
            ('wagesexpense', 'WAGESEXPENSE ACCOUNT'),
        ]


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    xero_linked_payment_account_id = fields.Many2one('account.account', string='Linked Xero Journal Account')


class XeroTaxHandler(models.Model):
    _name = 'xero.tax.handler'
    _description = 'Xero Tax Handler'

    name = fields.Char(string='Tax Name')
    rate = fields.Float(string='Tax Amount')
    tax_id = fields.Many2one('account.tax', string='Tax')

    _sql_constraints = [
        ('check_rate', 'CHECK(rate >= 0 AND rate <= 100)', 'Tax rate value should not be above 100 and below 0!'),
    ]


class AccountTax(models.Model):
    _inherit = 'account.tax'
    _description = 'Tax'

    name = fields.Char(string='Tax Name', required=True, size=48, translate=True)
    xero_type_tax_use = fields.Char(string='Xero Tax Scope', copy=False)
    xero_tax_handler_ids = fields.One2many('xero.tax.handler', 'tax_id', string='Handle Xero Taxes')

    @api.model
    def create(self, values):
        if values.get('xero_tax_handler_ids'):
            if values.get('xero_tax_handler_ids')[0][0] != 6:
                amount = 0.0
                for handler in values.get('xero_tax_handler_ids'):
                    amount += handler[2].get('rate')
                values.update({'amount': amount})
        return super(AccountTax, self).create(values)

    def write(self, values):
        if values.get('xero_tax_handler_ids'):
            if values.get('xero_tax_handler_ids')[0][0] != 6:
                amount = self.amount
                for handler in values.get('xero_tax_handler_ids'):
                    if handler[2] and handler[2].get('rate'):
                        amount += handler[2].get('rate')
                values.update({'amount': amount})
        return super(AccountTax, self).write(values)

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None, xero_tax_line_type=False):
        """ Returns the amount of a single tax. base_amount is the actual amount on which the tax is applied, which is
            price_unit * quantity eventually affected by previous taxes (if tax is include_base_amount XOR price_include)
        """
        self.ensure_one()

        if self.amount_type == 'fixed':
            # Use copysign to take into account the sign of the base amount which includes the sign
            # of the quantity and the sign of the price_unit
            # Amount is the fixed price for the tax, it can be negative
            # Base amount included the sign of the quantity and the sign of the unit price and when
            # a product is returned, it can be done either by changing the sign of quantity or by changing the
            # sign of the price unit.
            # When the price unit is equal to 0, the sign of the quantity is absorbed in base_amount then
            # a "else" case is needed.
            if base_amount:
                return math.copysign(quantity, base_amount) * self.amount
            else:
                return quantity * self.amount

        price_include = self._context.get('force_price_include', self.price_include)

        # base * (1 + tax_amount) = new_base
        if self.amount_type == 'percent' and not price_include:
            return base_amount * self.amount / 100
        # <=> new_base = base / (1 + tax_amount)
        if self.amount_type == 'percent' and (price_include or xero_tax_line_type == "Inclusive"):
            return base_amount - (base_amount / (1 + self.amount / 100))
        # base / (1 - tax_amount) = new_base
        if self.amount_type == 'division' and not price_include:
            return base_amount / (1 - self.amount / 100) - base_amount if (1 - self.amount / 100) else 0.0
        # <=> new_base * (1 - tax_amount) = base
        if self.amount_type == 'division' and (price_include or xero_tax_line_type == "Inclusive"):
            return base_amount - (base_amount * (self.amount / 100))

        # Setup for xero tax type
        if self.amount_type == "code":
            xerotaxdict = {
                "base_amount": base_amount,
                "price_unit": price_unit,
                "quantity": quantity,
                "product": product,
                "partner": partner,
                "company": self.env.company,
            }
            safe_eval(self.python_compute, xerotaxdict, mode="exec", nocopy=True)
            return xerotaxdict["result"]

    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None, is_refund=False, handle_price_include=True, xero_tax_line_type=False):
        if not self:
            company = self.env.company
        else:
            company = self[0].company_id

        ### Xero code
        if not xero_tax_line_type:
            xero_tax_line_type = self._context.get("xero_tax_line_type")
        ### End

        # 1) Flatten the taxes.
        taxes, groups_map = self.flatten_taxes_hierarchy(create_map=True)

        # 2) Avoid mixing taxes having price_include=False && include_base_amount=True
        # with taxes having price_include=True. This use case is not supported as the
        # computation of the total_excluded would be impossible.
        base_excluded_flag = False  # price_include=False && include_base_amount=True
        included_flag = False  # price_include=True
        for tax in taxes:
            if tax.price_include or xero_tax_line_type == "Inclusive":
                included_flag = True
            elif tax.include_base_amount:
                base_excluded_flag = True
            if base_excluded_flag and included_flag:
                raise UserError(_('Unable to mix any taxes being price included with taxes affecting the base amount but not included in price.'))

        # 3) Deal with the rounding methods
        if not currency:
            currency = company.currency_id

        prec = currency.rounding

        round_tax = False if company.tax_calculation_rounding_method == 'round_globally' else True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])

        if not round_tax:
            prec *= 1e-5

        def recompute_base(base_amount, fixed_amount, percent_amount, division_amount):
            return (base_amount - fixed_amount) / (1.0 + percent_amount / 100.0) * (100 - division_amount) / 100

        base = currency.round(price_unit * quantity)

        # For the computation of move lines, we could have a negative base value.
        # In this case, compute all with positive values and negate them at the end.
        sign = 1
        if currency.is_zero(base):
            sign = self._context.get('force_sign', 1)
        elif base < 0:
            sign = -1
        if base < 0:
            base = -base

        # Store the totals to reach when using price_include taxes (only the last price included in row)
        total_included_checkpoints = {}
        i = len(taxes) - 1
        store_included_tax_total = True
        # Keep track of the accumulated included fixed/percent amount.
        incl_fixed_amount = incl_percent_amount = incl_division_amount = 0
        # Store the tax amounts we compute while searching for the total_excluded
        cached_tax_amounts = {}
        if handle_price_include:
            for tax in reversed(taxes):
                tax_repartition_lines = (
                    is_refund
                    and tax.refund_repartition_line_ids
                    or tax.invoice_repartition_line_ids
                ).filtered(lambda x: x.repartition_type == "tax")
                sum_repartition_factor = sum(tax_repartition_lines.mapped("factor"))

                if tax.include_base_amount:
                    base = recompute_base(base, incl_fixed_amount, incl_percent_amount, incl_division_amount)
                    incl_fixed_amount = incl_percent_amount = incl_division_amount = 0
                    store_included_tax_total = True
                if tax.price_include or self._context.get('force_price_include') or xero_tax_line_type == "Inclusive":
                    if tax.amount_type == 'percent':
                        incl_percent_amount += tax.amount * sum_repartition_factor
                    elif tax.amount_type == 'division':
                        incl_division_amount += tax.amount * sum_repartition_factor
                    elif tax.amount_type == 'fixed':
                        incl_fixed_amount += quantity * tax.amount * sum_repartition_factor
                    else:
                        # tax.amount_type == other (python)
                        tax_amount = tax._compute_amount(base, sign * price_unit, quantity, product, partner, xero_tax_line_type=xero_tax_line_type) * sum_repartition_factor
                        incl_fixed_amount += tax_amount
                        # Avoid unecessary re-computation
                        cached_tax_amounts[i] = tax_amount
                    if store_included_tax_total and (
                        tax.amount or tax.amount_type not in ("percent", "division", "fixed")
                    ):
                        total_included_checkpoints[i] = base
                        store_included_tax_total = False
                i -= 1

        total_excluded = currency.round(recompute_base(base, incl_fixed_amount, incl_percent_amount, incl_division_amount))

        # 5) Iterate the taxes in the sequence order to compute missing tax amounts.
        # Start the computation of accumulated amounts at the total_excluded value.
        base = total_included = total_void = total_excluded

        taxes_vals = []
        i = 0
        cumulated_tax_included_amount = 0
        for tax in taxes:
            tax_repartition_lines = (is_refund and tax.refund_repartition_line_ids or tax.invoice_repartition_line_ids).filtered(lambda x: x.repartition_type == 'tax')
            sum_repartition_factor = sum(tax_repartition_lines.mapped('factor'))

            price_include = self._context.get('force_price_include', tax.price_include)

            #compute the tax_amount
            if (xero_tax_line_type == "Inclusive" or price_include) and total_included_checkpoints.get(i):
                # We know the total to reach for that tax, so we make a substraction to avoid any rounding issues
                tax_amount = total_included_checkpoints[i] - (base + cumulated_tax_included_amount)
                cumulated_tax_included_amount = 0
            else:
                tax_amount = tax.with_context(force_price_include=False)._compute_amount(
                    base, sign * price_unit, quantity, product, partner, xero_tax_line_type=xero_tax_line_type)

            # Round the tax_amount multiplied by the computed repartition lines factor.
            tax_amount = round(tax_amount, precision_rounding=prec)
            factorized_tax_amount = round(tax_amount * sum_repartition_factor, precision_rounding=prec)

            # Check xero tax type
            if (price_include or xero_tax_line_type == "Inclusive") and not total_included_checkpoints.get(i):
                cumulated_tax_included_amount += factorized_tax_amount

            # If the tax affects the base of subsequent taxes, its tax move lines must
            # receive the base tags and tag_ids of these taxes, so that the tax report computes
            # the right total
            subsequent_taxes = self.env['account.tax']
            subsequent_tags = self.env['account.account.tag']
            if tax.include_base_amount:
                subsequent_taxes = taxes[i+1:]
                subsequent_tags = subsequent_taxes.get_tax_tags(is_refund, 'base')

            # Compute the tax line amounts by multiplying each factor with the tax amount.
            # Then, spread the tax rounding to ensure the consistency of each line independently with the factorized
            # amount. E.g:
            #
            # Suppose a tax having 4 x 50% repartition line applied on a tax amount of 0.03 with 2 decimal places.
            # The factorized_tax_amount will be 0.06 (200% x 0.03). However, each line taken independently will compute
            # 50% * 0.03 = 0.01 with rounding. It means there is 0.06 - 0.04 = 0.02 as total_rounding_error to dispatch
            # in lines as 2 x 0.01.
            repartition_line_amounts = [round(tax_amount * line.factor, precision_rounding=prec) for line in tax_repartition_lines]
            total_rounding_error = round(factorized_tax_amount - sum(repartition_line_amounts), precision_rounding=prec)
            nber_rounding_steps = int(abs(total_rounding_error / currency.rounding))
            rounding_error = round(nber_rounding_steps and total_rounding_error / nber_rounding_steps or 0.0, precision_rounding=prec)

            for repartition_line, line_amount in zip(tax_repartition_lines, repartition_line_amounts):

                if nber_rounding_steps:
                    line_amount += rounding_error
                    nber_rounding_steps -= 1

                taxes_vals.append({
                    'id': tax.id,
                    'name': partner and tax.with_context(lang=partner.lang).name or tax.name,
                    'amount': sign * line_amount,
                    'base': round(sign * base, precision_rounding=prec),
                    'sequence': tax.sequence,
                    'account_id': tax.cash_basis_transition_account_id.id if tax.tax_exigibility == 'on_payment' else repartition_line.account_id.id,
                    'analytic': tax.analytic,
                    'price_include': price_include,
                    'tax_exigibility': tax.tax_exigibility,
                    'tax_repartition_line_id': repartition_line.id,
                    'group': groups_map.get(tax),
                    'tag_ids': (repartition_line.tag_ids + subsequent_tags).ids,
                    'tax_ids': subsequent_taxes.ids,
                })

                if not repartition_line.account_id:
                    total_void += line_amount

            # Affect subsequent taxes
            if tax.include_base_amount:
                base += factorized_tax_amount

            total_included += factorized_tax_amount
            i += 1

        return {
            'base_tags': taxes.mapped(is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids').filtered(lambda x: x.repartition_type == 'base').mapped('tag_ids').ids,
            'taxes': taxes_vals,
            'total_excluded': sign * total_excluded,
            'total_included': sign * currency.round(total_included),
            'total_void': sign * currency.round(total_void),
        }

    # Import Tax from xero to odoo
    def set_tax_to_odoo(self, taxes, xero, company_id=False, options=None):
        for tax_id in taxes:
            xero_tax_dict = xero.json_load_object_hook(tax_id)
            if xero_tax_dict.get('Status') == 'ACTIVE':
                
                if xero_tax_dict.get('ReportTaxType') == 'INPUT':
                    tax_type = 'purchase'
                elif xero_tax_dict.get('ReportTaxType') == 'OUTPUT':
                    tax_type = 'sale'
                else:
                    tax_type = 'none'
                
                amount = 0.0
                tax_child = []
                for tax_handle in xero_tax_dict.get('TaxComponents'):
                    tax_child.append(self.env['xero.tax.handler'].create({
                        'name': tax_handle.get('Name'),
                        'rate': tax_handle.get('Rate')}).id)
                    amount += tax_handle.get('Rate')
                exist_tax_id  = self.search([('xero_type_tax_use', '=', xero_tax_dict.get('TaxType')), ('company_id', '=', company_id)], limit=1)
                avilable_tax_ids = self.search([('company_id', '=', company_id), ('name', '=', xero_tax_dict.get('Name'))])
                if avilable_tax_ids:
                    avilable_tax_ids.write({'xero_type_tax_use': xero_tax_dict.get('TaxType')})
                if exist_tax_id and options in ['update', 'both']:
                    exist_tax_id.write({
                        'amount': amount,
                        'xero_type_tax_use': xero_tax_dict.get('TaxType'),
                        'xero_tax_handler_ids': [(6, 0, tax_child)],
                        'type_tax_use': tax_type,
                        'company_id': company_id,
                    })
                    self._cr.commit()
                elif not exist_tax_id and not avilable_tax_ids and options in ['create', 'both']:
                    self.create({'name': xero_tax_dict.get('Name'),
                                 'amount': amount,
                                 'xero_type_tax_use': xero_tax_dict.get('TaxType'),
                                 'xero_tax_handler_ids': [(6, 0, tax_child)],
                                 'type_tax_use': tax_type,
                                 'company_id': company_id,
                                 })
                    self._cr.commit()


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    linked_bank_account_id = fields.Char(string='Xero Bank Account', readonly=True)

    # Import Bank account from xero to odoo
    def set_bank_account_to_odoo(self, bank_accounts, xero, options=None, company_id=False):
        ResPartner = self.env['res.partner']
        ResCurrency = self.env['res.currency']
        for account in bank_accounts:
            account = xero.json_load_object_hook(account)
            if account.get('Status') == 'ACTIVE':
                partner_id = ResPartner.search([('name', '=', account.get('Name'))], limit=1)
                if not partner_id:
                    partner_id = ResPartner.create({'name': account.get('Name'), 'company_id': company_id})

                currency_id = ResCurrency.search([('name', '=', account.get('CurrencyCode'))], limit=1)
                bank_account_id = self.search([('linked_bank_account_id', '=', account.get('AccountID'))], limit=1)
                exist_bank_account_ids = self.search([('acc_number', '=', account.get('BankAccountNumber'))])
                if bank_account_id and options in ['update', 'both']:
                    bank_account_id.write({
                                        'partner_id': partner_id.id,
                                        'currency_id': currency_id.id if currency_id else False,
                                        'acc_number': account.get('BankAccountNumber')})
                    self._cr.commit()
                elif not bank_account_id and not exist_bank_account_ids and options in ['create', 'both']:
                    self.create({
                                'linked_bank_account_id': account.get('AccountID'),
                                'partner_id': partner_id.id,
                                'currency_id': currency_id.id if currency_id else False,
                                'acc_number': account.get('BankAccountNumber'),
                                'company_id': company_id})
                    self._cr.commit()


class AccountAccount(models.Model):
    _inherit = 'account.account'

    linked_xero_account_id = fields.Char(string='Xero Account', readonly=True, copy=False)
    xero_user_type = fields.Selection(USER_ACCOUNT_TYPE, string='Xero Tax Scope', default='sales')
    is_xero_stock_manage = fields.Boolean(string='Xero Stock Manage')

    def set_coa_to_odoo(self, accounts, xero, company_id=False, options=None):
        current_liabilities_account_id = self.env.ref('account.data_account_type_current_liabilities')
        current_assets_account_id = self.env.ref('account.data_account_type_current_assets')
        expense_account_id = self.env.ref('account.data_account_type_expenses')
        sales_account_id = self.env.ref('account.data_account_type_revenue')
        non_current_liabilities_account_id = self.env.ref('account.data_account_type_non_current_liabilities')
        liquidity_account_id = self.env.ref('account.data_account_type_liquidity')
        equity_account_id = self.env.ref('account.data_account_type_equity')
        depreciation_account_id = self.env.ref('account.data_account_type_depreciation')
        fixed_account_id = self.env.ref('account.data_account_type_fixed_assets')
        other_income_account_id = self.env.ref('account.data_account_type_other_income')
        current_assets_account_id = self.env.ref('account.data_account_type_non_current_assets')
        prepayment_account_id = self.env.ref('account.data_account_type_prepayments')
        get_user_account = {
                           'currliab': current_liabilities_account_id,
                           'liability': current_liabilities_account_id,
                           'paygliability': current_liabilities_account_id,
                           'current': current_assets_account_id,
                           'inventory': current_assets_account_id,
                           'expense': expense_account_id,
                           'directcosts': expense_account_id,
                           'overheads': expense_account_id,
                           'wagesexpense': expense_account_id,
                           'superannuationexpense': expense_account_id,
                           'revenue': sales_account_id,
                           'sales': sales_account_id,
                           'termliab': non_current_liabilities_account_id,
                           'superannuationliability': non_current_liabilities_account_id,
                           'bank': liquidity_account_id,
                           'equity': equity_account_id,
                           'depreciatn': depreciation_account_id,
                           'fixed': fixed_account_id,
                           'otherincome': other_income_account_id,
                           'noncurrent': current_assets_account_id,
                           'prepayment': prepayment_account_id,
                            }

        AccountTax = self.env['account.tax']
        for account in accounts:
            xero_account_dict = xero.json_load_object_hook(account)
            if xero_account_dict.get('Status') == 'ACTIVE' and xero_account_dict.get('Type'):
                user_account_type = str(xero_account_dict['Type'].lower())
                if get_user_account.get(user_account_type):
                    user_type = get_user_account[user_account_type]
                    
                    exist_account_id = self.search([('linked_xero_account_id', '=', xero_account_dict.get('AccountID')), ('company_id', '=', company_id)],limit=1)
                    if xero_account_dict.get('Type') == 'BANK' and not xero_account_dict.get('Code'):
                        raise UserError(_('Code must be unique for account \'%s\' in Xero.')% (xero_account_dict.get('Name')))
                    
                    exist_account_ids = self.search([('code', '=', xero_account_dict.get('Code')), ('company_id', '=', company_id)], limit=1)
                    if exist_account_ids and not exist_account_ids.linked_xero_account_id and exist_account_ids.name == xero_account_dict.get('Name'):
                        exist_account_ids.linked_xero_account_id = xero_account_dict.get('AccountID')
                    
                    tax_id = AccountTax.search([('xero_type_tax_use', '=', xero_account_dict.get('TaxType')), ('company_id', '=', company_id)])
                    if not exist_account_id and not exist_account_ids and options in ['create', 'both']:
                        self.create({'name': xero_account_dict.get('Name') or '',
                                     'code': xero_account_dict.get('Code') or '',
                                     'linked_xero_account_id': xero_account_dict.get('AccountID') or '',
                                     'company_id': company_id,
                                     'tax_ids': [(6, 0, [tax_id[0].id])] if tax_id else [],
                                     'is_xero_stock_manage': True if user_account_type in ['inventory'] else False,
                                     'user_type_id': user_type and user_type.id or False,
                                     'xero_user_type': user_account_type})
                        self._cr.commit()


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    symbol = fields.Char(string='Symbol', required=False, help='Currency sign, to be used when printing amounts.')

    def set_currency_to_odoo(self, currencies, xero):
        for currency in currencies:
            # xero_currency_dict = xero.json_load_object_hook(currency)
            xero_currency_dict = currency
            archived_currency_id = self.search([('name', '=', xero_currency_dict.get('Code')), ('active', '=', False)], limit=1)
            currency_id = self.search([('name', '=', xero_currency_dict.get('Code')), ('active', '=', True)])
            if archived_currency_id:
                archived_currency_id.write({'active': True})
                self._cr.commit()
            elif not archived_currency_id and not currency_id:
                self.create({'name': xero_currency_dict.get('Code'), 'active': True})
                self._cr.commit()

    @api.model
    def _compute_convert_currency(self, from_currency, to_currency):
        to_currency = to_currency.with_env(self.env)
        return to_currency.rate / from_currency

    def compute(self, from_amount, to_currency, round=True):
        _logger.warning('The `compute` method is deprecated. Use `_convert` instead')
        date = self._context.get('date') or fields.Date.today()
        company_id = self.env['res.company'].browse(self._context.get('company_id')) or self.env['res.users']._get_company()
        
        self, to_currency = self or to_currency, to_currency or self
        assert self, "compute from unknown resource(currency)"
        assert to_currency, "compute to unknown resource(currency)"
        
        if self == to_currency:
            to_amount = from_amount
        else:
            if self._context.get('CurrencyRate'):
                to_amount = from_amount * self._compute_convert_currency(self._context.get('CurrencyRate'), to_currency)
            else:
                to_amount = from_amount * self._get_conversion_rate(self, to_currency, company_id, date)
        
        return to_currency.round(to_amount) if round else to_amount
        