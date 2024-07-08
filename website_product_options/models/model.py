# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _


class ProductBundles(models.Model):
    _name = 'product.bundles'
    _order = "sequence,id"

    sequence = fields.Integer('Sequence', default=1)
    product_id = fields.Many2many('product.template', string="Products")
    qty = fields.Integer(string='Qty', default=1)
    bundle_id = fields.Many2one('product.template')
    bundle_name = fields.Char("Name")
    extra_amount = fields.Float(default=0.0)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bundle_extra_price = fields.Float('Bundle Product Price')

    is_optional_product = fields.Boolean('Optional Product')
    accessory_product = fields.Boolean('Accessory Product')

    is_bundle_product = fields.Boolean('Bundle Product')
    bundle_product_ids = fields.One2many(
        'product.bundles', 'bundle_id',
        string='Bundle Products')

    product_option_group = fields.Many2one('options.group', string='Options Group')

    @api.onchange('is_optional_product', 'is_bundle_product')
    def _onchange_is_optional_product(self):
        for rec in self:
            if rec.is_optional_product:
                rec.is_published = True

    def make_product_and_optional_to_website(self):
        for res in self:
            res.is_published = True
            if res.optional_product_ids:
                filtered_product = res.optional_product_ids.filtered(lambda r: r.is_published == False)
                for opt in filtered_product:
                    opt.is_published = True

    def unpublish_product_and_optional(self):
        for res in self:
            res.is_published = False
            if res.optional_product_ids:
                filtered_product = res.optional_product_ids.filtered(lambda r: r.is_published == True)
                for opt in filtered_product:
                    opt.is_published = False


class OptionsGroup(models.Model):
    _name = 'options.group'
    _order = "sequence,id"

    name = fields.Char()
    sequence = fields.Integer('Sequence', default=1, help='Gives the sequence order when displaying a product option list')
    max_count = fields.Integer(string="Maximum Number")
    min_count = fields.Integer(string="Minimum Number")
    icon = fields.Char('Icon')

    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)

class SaleLine(models.Model):
    _inherit = 'sale.order.line'

    bundle_parent = fields.Boolean()
    bundle_child = fields.Boolean()
    bundle_option = fields.Boolean()
    bundle_parent_id = fields.Integer()

    def write(self, vals):
        res = super(SaleLine, self).write(vals)
        for i in self:
            if not i._context.get('bundle_option', False):
                if i.bundle_option:
                    bundle_price = i.product_id.bundle_extra_price
                    print(i.bundle_option, "hfdsasd", bundle_price)
                    i.with_context(bundle_option=True).price_unit = bundle_price
        return res
