# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    split_order_ids = fields.One2many('sale.order', 'split_id')
    split_id = fields.Many2one('sale.order')
    brand_id = fields.Many2one('product.brand', 'Brand')

    def split_order(self):
        for rec in self:
            for line in rec.order_line:
                brand = line.product_id.product_brand_id
                # Already has one or more order lines of one brand
                if rec.brand_id and brand and brand.id != rec.brand_id.id:
                    split_line = rec.split_order_ids.filtered(
                        lambda l: l.brand_id.id == rec.brand_id.id)
                    if split_line:
                        line.order_id = split_line[0].id
                    else:
                        split_line = request.website.sale_get_order(
                            force_create=True)
                        split_line.sudo().write({
                            'brand_id': brand.id,
                            'split_id': rec.id,
                        })
                        line.order_id = split_line.id
                        split_line.action_confirm()
                # First line with a brand
                elif brand:
                    rec.brand_id = brand.id
