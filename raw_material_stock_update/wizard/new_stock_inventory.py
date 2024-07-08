# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import models, fields, _
from odoo.exceptions import UserError


class NewStockInventory(models.TransientModel):
    _name = 'new.stock.inventory'
    _description = "New Stock Inventory"

    product_ids = fields.Many2many("product.template", string="Product Template")

    def conform(self):
        product_list = self.product_ids.mapped("product_variant_ids")
        product_ids = product_list.filtered(lambda x: not x.inventory_location_id)
        if product_ids:
            raise UserError(_('Select location for below products \n%s' % ('\n'.join(p.name for p in product_ids.mapped('product_tmpl_id')))))
        try:
            inventory = self.env['stock.inventory'].sudo().create({
                'name': 'Inventory adjustment ' + str(fields.Datetime.now()),
                'product_ids': product_list.ids,
            })
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', inventory.company_id.id)], limit=1)
            for product in product_list:
                self.env['stock.inventory.line'].sudo().create({
                    'product_id': product.id,
                    'inventory_id': inventory.id,
                    'product_qty': product.new_quantity,
                    'location_id': product.inventory_location_id and product.inventory_location_id.id or False,
                })
            inventory._action_start()
            inventory.action_validate()
            for product in product_list:
                product.new_quantity = 0
                if product.stock_update_type == 'daily':
                    product.inventory_adjust_date = datetime.today() + timedelta(days=1)
                if product.stock_update_type == 'weekly':
                    product.inventory_adjust_date = datetime.today() + timedelta(weeks=1)
                if product.stock_update_type == 'monthly':
                    product.inventory_adjust_date = datetime.today() + timedelta(days=30)
        except Exception as e:
            raise UserError(e)
