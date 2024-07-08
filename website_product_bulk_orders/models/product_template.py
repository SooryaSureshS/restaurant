# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    hidden_color_attribute_value_ids = fields.Many2many('product.attribute.value', string="Hide Attribute Colors")
    product_bulk_order = fields.Boolean("Product Bulk Order.")
    bulk_order_config = fields.Boolean(compute="_compute_config_base")

    def _compute_config_base(self):
        self.bulk_order_config = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'website_product_bulk_orders.product_bulk_order')], limit=1).value

    def get_all_product_template_data(self):
        color_size_variant_mapping = {}
        for variant in self.product_variant_ids:
            variant_attribute_name = '-'
            for ptav in variant.product_template_attribute_value_ids:
                if ptav.attribute_id.bulk_attribute == 'color':
                    variant_attribute_name = str(ptav.product_attribute_value_id.id) + variant_attribute_name
                if ptav.attribute_id.bulk_attribute == 'size':
                    variant_attribute_name = variant_attribute_name + str(ptav.product_attribute_value_id.id)
            variant_price = self.env['product.pricelist'].price_get(variant.id, 1, self.env.user.partner_id.id).get(
                self.env.user.partner_id.property_product_pricelist.id, False)
            color_size_variant_mapping.update(
                {variant_attribute_name: [variant.id, variant_price and variant_price or variant.lst_price,
                                          variant.qty_available]})
        size_data = []
        size_value_ids = self.attribute_line_ids.filtered(
            lambda x: x.attribute_id.bulk_attribute == 'size') and self.attribute_line_ids.filtered(
            lambda x: x.attribute_id.bulk_attribute == 'size').value_ids.filtered(
            lambda y: y.id not in self.hidden_color_attribute_value_ids.ids) or []
        for x in size_value_ids:
            size_data.append([x.id, x.name])
        color_data = []
        color_value_ids = self.attribute_line_ids.filtered(
            lambda x: x.attribute_id.bulk_attribute == 'color') and self.attribute_line_ids.filtered(
            lambda x: x.attribute_id.bulk_attribute == 'color').value_ids.filtered(
            lambda y: y.id not in self.hidden_color_attribute_value_ids.ids) or []
        for x in color_value_ids:
            color_data.append([x.id, x.name])
        data = {
            'size': size_data,
            'color': color_data,
            'color_size_variant_mapping': color_size_variant_mapping,
            'currency_symbol': self.currency_id.symbol
        }
        return data
