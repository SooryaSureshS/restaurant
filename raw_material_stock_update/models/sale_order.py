# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #     for order_line in self.order_line:
    #         if order_line.product_template_id.raw_material_ids:
    #             for recipe in order_line.product_template_id.raw_material_ids:
    #                 for product in recipe.product_id:
    #                     quant_line = {
    #                         "product_id": product.product_variant_id.id,
    #                         "quantity": -(order_line.product_uom_qty*recipe.product_qty),
    #                         "location_id": product.inventory_location_id.id,
    #                     }
    #                     self.env["stock.quant"].sudo().create(quant_line)
    #     return res


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # def action_pos_order_paid(self):
    #     res = super(PosOrder, self).action_pos_order_paid()
    #     for order_line in self.lines:
    #         if order_line.product_id.raw_material_ids:
    #             for recipe in order_line.product_id.raw_material_ids:
    #                 for product in recipe.product_id:
    #                     quant_line = {
    #                         "product_id": product.product_variant_id.id,
    #                         "quantity": -(order_line.qty*recipe.product_qty),
    #                         "location_id": product.inventory_location_id.id,
    #                     }
    #                     self.env["stock.quant"].sudo().create(quant_line)
    #     return res
