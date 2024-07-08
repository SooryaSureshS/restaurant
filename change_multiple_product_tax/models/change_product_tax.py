# -*- coding: utf-8 -*-
# Email: shivoham.odoo@gmail.com

from odoo import models, fields, api, _


class ChangeProductTax(models.Model):
    _name = 'change.tax'
    _description = 'Change Product Tax'

    change_type = fields.Selection([('category', 'Product Category wise'), ('pos_category', 'POS Category wise'),
                                    ('product', 'Multiple Product wise')], default='category',
                                    string='Change Product tax')
    change_tax_type = fields.Selection([('customer', 'Customer Tax'), ('vendor', 'Vendor Tax'),  ('both', 'Both')],
                                       default='customer', string='Change which tax of product')
    taxes_id = fields.Many2many('account.tax', 'change_product_taxes', 'prod_id', 'tax_id',
                                help="Default taxes used when selling the product.", string='Customer Taxes',
                                domain=[('type_tax_use', '=', 'sale')],
                                default=lambda self: self.env.company.account_sale_tax_id)
    supplier_taxes_id = fields.Many2many('account.tax', 'change_product_supplier_taxes', 'prod_id', 'tax_id',
                                         string='Vendor Taxes', help='Default taxes used when buying the product.',
                                         domain=[('type_tax_use', '=', 'purchase')],
                                         default=lambda self: self.env.company.account_purchase_tax_id)
    categ_id = fields.Many2one('product.category', string='Product category')
    pos_categ_id = fields.Many2one('pos.category', string='POS category')
    product_id = fields.Many2many('product.product', string='Product')

    def change_product_tax(self):
        if self.change_type == 'category':
            products = self.env['product.product'].search([('categ_id', '=', self.categ_id.id)])
            if self.change_tax_type == 'customer':
                for rec in products:
                    rec.taxes_id = self.taxes_id
            elif self.change_type == 'vendor':
                for rec in products:
                    rec.supplier_taxes_id = self.supplier_taxes_id
            else:
                for rec in products:
                    rec.taxes_id = self.taxes_id
                    rec.supplier_taxes_id = self.supplier_taxes_id

        elif self.change_type == 'pos_category':
            products = self.env['product.product'].search([('pos_categ_id', '=', self.pos_categ_id.id)])
            if self.change_tax_type == 'customer':
                for rec in products:
                    rec.taxes_id = self.taxes_id
            elif self.change_type == 'vendor':
                for rec in products:
                    rec.supplier_taxes_id = self.supplier_taxes_id
            else:
                for rec in products:
                    rec.taxes_id = self.taxes_id
                    rec.supplier_taxes_id = self.supplier_taxes_id

        elif self.change_type == 'product':
            products = self.env['product.product'].search([('id', 'in', self.product_id.ids)])
            if self.change_tax_type == 'customer':
                for rec in products:
                    rec.taxes_id = self.taxes_id
            elif self.change_type == 'vendor':
                for rec in products:
                    rec.supplier_taxes_id = self.supplier_taxes_id
            else:
                for rec in products:
                    rec.taxes_id = self.taxes_id
                    rec.supplier_taxes_id = self.supplier_taxes_id
