from odoo import models, fields


class PosConfigKitchenPOsOrdersChange(models.Model):
    _name = 'change.order'

    product_id = fields.Many2one('product.product', string="Products")
    qty = fields.Integer(string='Qty', default=0)
    change_id = fields.Many2one('pos.order',string='Change Id', default=0)


class PosConfigKitchenSaleOrdersLine(models.Model):
    _inherit = 'sale.order.line'

    order_printed = fields.Boolean(string='Order Printed')


class PosConfigKitchePosOrdersLine(models.Model):
    _inherit = 'pos.order.line'

    order_printed = fields.Boolean(string='Order Printed')


class RestaurantPrinter(models.Model):
    _inherit = 'restaurant.printer'

    is_pass_printer = fields.Boolean('Is pass')


class PosConfigKitchenSaleOrders(models.Model):
    _inherit = 'sale.order'

    order_printed = fields.Boolean(string='Order Printed')


class PosConfigKitchenPOsOrders(models.Model):
    _inherit = 'pos.order'

    order_printed = fields.Boolean(string='Order Printed')
    updated_order = fields.Boolean(string='Updated Order', readonly=True, copy=False)
    change_ids = fields.One2many('change.order', 'change_id', string='Tables', help='The list of Change orders')


class PosConfig(models.Model):
    _inherit = 'pos.config'

    trigger_screen = fields.Selection([('kvs', 'KVS'), ('product', 'Product')], string='Print From',  default='kvs')
