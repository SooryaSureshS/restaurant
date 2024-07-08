# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import datetime


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    initial_inventory = fields.Boolean(string='Base Stock Set')
    taxes_id = fields.Many2many('account.tax', 'product_taxes_rel', 'prod_id', 'tax_id', string='Customer Taxes', domain=[('type_tax_use', '!=', 'purchase')])
    supplier_taxes_id = fields.Many2many('account.tax', 'product_supplier_taxes_rel', 'prod_id', 'tax_id', string='Vendor Taxes', domain=[('type_tax_use', '!=', 'sale')])


class XeroProduct(models.Model):
    _name = 'xero.product'
    _description = 'Xero Product'

    xero_product_id = fields.Char(string='Xero Product Ref/ID')
    product_id = fields.Many2one('product.product', string='Product')
    company_id = fields.Many2one('res.company', string='Company', required=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    xero_product_related_companies = fields.One2many('xero.product', 'product_id', string='Linked Xero Company')

    _sql_constraints = [
        ('default_code_uniq', 'unique(default_code)', 'Internal Reference must be unique!'),
    ]

    @api.onchange('company_id')
    def _onchange_company(self):
        if self.company_id:
            xero_company_id = self.xero_product_related_companies.filtered(lambda l: l.company_id.id == self.company_id.id)
            if not xero_company_id:
                self.xero_product_related_companies = [(6, 0, {'company_id': self.company_id.id})]

    def set_product_to_odoo(self, products, xero, mapped_categ_id, unmapped_categ_id, company_id=False, options=None):
        AccountAccount = self.env['account.account']
        AccountTax = self.env['account.tax']
        ProductChangeQuantity = self.env['stock.change.product.qty']
        for product in products:
            product_dict = xero.json_load_object_hook(product)
            property_account_income_id = property_account_expense_id = sale_taxes_ids = purchase_taxes_ids = False
            
            if product_dict.get('SalesDetails').get('AccountCode'):
                property_account_income_id = AccountAccount.search([('code', '=', product_dict.get('SalesDetails').get('AccountCode')), ('company_id', '=', company_id)], limit=1)
            
            if product_dict.get('PurchaseDetails').get('AccountCode'):
                property_account_expense_id = AccountAccount.search([('code', '=', product_dict.get('PurchaseDetails').get('AccountCode')), ('company_id', '=', company_id)], limit=1)
            if product_dict.get('PurchaseDetails').get('COGSAccountCode'):
                property_account_expense_id = AccountAccount.search([('code', '=', product_dict.get('PurchaseDetails').get('COGSAccountCode')), ('company_id', '=', company_id)], limit=1)
            
            if product_dict.get('SalesDetails').get('TaxType'):
                sale_taxes_ids = AccountTax.search([('xero_type_tax_use', '=', product_dict.get('SalesDetails').get('TaxType')), ('company_id', '=', company_id)])
            if product_dict.get('PurchaseDetails').get('TaxType'):
                purchase_taxes_ids = AccountTax.search([('xero_type_tax_use', '=', product_dict.get('PurchaseDetails').get('TaxType')), ('company_id', '=', company_id)])
            
            exist_product_id = self.search([('default_code', '=', product_dict.get('Code'))], limit=1)
            xero_product_company_id = exist_product_id.xero_product_related_companies.filtered(lambda c: c.company_id.id == company_id)
            if exist_product_id and xero_product_company_id and not xero_product_company_id.xero_product_id:
                xero_product_company_id.xero_product_id = product_dict.get('ItemID')
            elif exist_product_id and not xero_product_company_id:
                exist_product_id.xero_product_related_companies = [(0, 0, {'company_id': company_id,
                                                                           'xero_product_id': product_dict.get('ItemID')})]

            product_ids = self.search([]).filtered(lambda product_id: product_id.xero_product_related_companies.filtered(lambda l: l.company_id.id == company_id and l.xero_product_id == product_dict.get('ItemID')))

            product_type = 'consu'
            product_category = unmapped_categ_id
            if product_dict.get('IsTrackedAsInventory'):
                product_type = 'product'
                product_category = mapped_categ_id
            
            if not mapped_categ_id and not unmapped_categ_id:
                print (">>>>>>>>>>>>>>>>>>>..", mapped_categ_id, unmapped_categ_id)
                product_category = self.env.ref('product.product_category_all')
                
            if product_ids and options in ['update', 'both']:
                product_ids[0].write({
                    'type': product_type,
                    'name': product_dict.get('Name', product_dict.get('Code')) or u'',
                    'default_code': product_dict.get('Code') or u'',
                    'description': product_dict.get('Description') or u'',
                    'list_price': product_dict.get('SalesDetails').get('UnitPrice') or 0.0,
                    'standard_price': product_dict.get('PurchaseDetails').get('UnitPrice') or 0.0,
                    'property_account_income_id': property_account_income_id,
                    'property_account_expense_id': property_account_expense_id,
                    'taxes_id': [(6, 0, sale_taxes_ids.ids)] if sale_taxes_ids else [],
                    'supplier_taxes_id': [(6, 0, purchase_taxes_ids.ids)] if purchase_taxes_ids else [],
                    'categ_id': product_category.id if product_category else False,
                    })
                self._cr.commit()
            
            elif not product_ids and options in ['create', 'both']:
                product_id = self.create({
                    'type': product_type,
                    'name': product_dict.get('Name', product_dict.get('Code')) or u'',
                    'default_code': product_dict.get('Code') or u'',
                    'description': product_dict.get('Description') or u'',
                    'list_price': product_dict.get('SalesDetails').get('UnitPrice') or 0.0,
                    'standard_price': product_dict.get('PurchaseDetails').get('UnitPrice') or 0.0,
                    'property_account_income_id': property_account_income_id,
                    'property_account_expense_id': property_account_expense_id,
                    'taxes_id': [(6, 0, sale_taxes_ids.ids)] if sale_taxes_ids else [],
                    'supplier_taxes_id': [(6, 0, purchase_taxes_ids.ids)] if purchase_taxes_ids else [],
                    'categ_id': product_category.id if product_category else False,
                    'company_id': company_id,
                    'xero_product_related_companies': [(0, 0, {'company_id': company_id, 'xero_product_id': product_dict.get('ItemID')})],
                    })

                if product_dict.get('IsTrackedAsInventory'):
                    InventoryWizard = ProductChangeQuantity.with_context({'xero_opening_stock': True}).create({
                            'product_id': product_id.id,
                            'product_tmpl_id': product_id.product_tmpl_id.id,
                            'new_quantity': product_dict.get('QuantityOnHand'),
                        })
                    InventoryWizard.change_product_qty()
                self._cr.commit()


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    xero_opening_stock = fields.Boolean(string='Xero Opening Stock')
    xero_invoice_ref_id = fields.Char(string='Xero Invoice Reference ID', readonly=True, copy=False)
    xero_invoice_ref_no = fields.Char(string='Xero Invoice Reference No', readonly=True, copy=False)

    @api.model
    def create(self, values):
        if self._context.get('xero_opening_stock'):
            values.update({'xero_opening_stock': True})
        return super(StockMoveLine, self).create(values)

    def adjust_inventories(self, xero, company_id=False, inventory_account_id=False):
        stock_move_lines = self.search([('product_id.categ_id.property_valuation', '=', 'real_time'),
                                      '|',
                                    ('location_id.usage', 'in', ['inventory', 'production']),
                                    ('location_dest_id.usage', 'in', ['inventory','production']),
                                    ('state', '=', 'done'),
                                    ('xero_invoice_ref_id', '=', False),
                                    ('xero_invoice_ref_no', '=', False),
                                    ('move_id.company_id', '=', company_id),
                                    ('xero_opening_stock', '=', False)])

        for move_line in stock_move_lines:
            product_default_code = move_line.product_id.default_code[:30] if move_line.product_id.default_code else move_line.product_id.name[:30]
            if move_line.location_id.usage in ['production', 'inventory']:
                description = (str(move_line.move_id.reference) + '-' + 'Inventory Adjustment') if move_line.location_id.usage == 'inventory' else (str(move_line.move_id.reference) + '-' + 'Inventory Adjustment (Manufacturing)')
                invoice_vals = {
                        u'Type': u'ACCPAY',
                        u'Contact': {u'Name': u'Stock Journal (Odoo)'},
                        u'InvoiceNumber': description,
                        u'Date': move_line.date and datetime.datetime.strftime(move_line.date, "%Y-%m-%d"),
                        u'DueDate': move_line.date and datetime.datetime.strftime(move_line.date, "%Y-%m-%d"),
                        u'LineAmountTypes': u'NoTax',
                        u'Status': u'AUTHORISED',
                        u'LineItems': [{u'ItemCode': product_default_code,
                                      u'Description': move_line.product_id.description or move_line.product_id.name,
                                      u'Quantity': move_line.qty_done,
                                      u'UnitAmount': move_line.product_id.standard_price,
                                      u'AccountCode': (move_line.product_id.categ_id.property_stock_account_input_categ_id and move_line.product_id.categ_id.property_stock_account_input_categ_id.code) or 630,
                                      },
                                      {
                                      u'Description': 'Stock Movement',
                                      u'Quantity': move_line.qty_done,
                                      u'UnitAmount': -(move_line.product_id.standard_price),
                                      u'AccountCode': (inventory_account_id and inventory_account_id.code or 401),
                                      }]}
                xero_invoice_id = xero.invoices.put(invoice_vals)
                move_line.write({'xero_invoice_ref_id': xero_invoice_id[0]['InvoiceID'], 'xero_invoice_ref_no': xero_invoice_id[0]['InvoiceNumber']})
                self._cr.commit()
            elif move_line.location_dest_id.usage in ['production', 'inventory']:
                description = (str(move_line.move_id.reference) + '-' + 'Inventory Adjustment') if move_line.location_dest_id.usage == 'inventory' else (str(move_line.move_id.reference) + '-' + 'Inventory Adjustment (Manufacturing)')
                refund_invoice_vals = {u'Type': u'ACCPAYCREDIT',
                          u'Contact': {u'Name': u'Stock Journal (Odoo)'},
                          u'CreditNoteNumber': description,
                          u'Date': move_line.date and datetime.datetime.strftime(move_line.date, "%Y-%m-%d"),
                          u'DueDate': move_line.date and datetime.datetime.strftime(move_line.date, "%Y-%m-%d"),
                          u'LineAmountTypes': u'NoTax',
                          u'Status': u'AUTHORISED',
                          u'LineItems': [{u'ItemCode': product_default_code,
                                          u'Description': move_line.product_id.description or move_line.product_id.name,
                                          u'Quantity': move_line.qty_done,
                                          u'UnitAmount': move_line.product_id.standard_price,
                                          u'AccountCode': (move_line.product_id.categ_id.property_stock_account_input_categ_id and move_line.product_id.categ_id.property_stock_account_input_categ_id.code) or 630,
                                          },
                                          {
                                          u'Description': 'Stock Movement',
                                          u'Quantity': move_line.qty_done,
                                          u'UnitAmount': -(move_line.product_id.standard_price),
                                          u'AccountCode': (inventory_account_id and inventory_account_id.code or 401),
                                          }]}
                xero_refund_invoice_id = xero.creditnotes.put(refund_invoice_vals)
                move_line.write({'xero_invoice_ref_id': xero_refund_invoice_id[0]['CreditNoteID'], 'xero_invoice_ref_no': xero_refund_invoice_id[0]['CreditNoteID']})
                self._cr.commit()
        return True
