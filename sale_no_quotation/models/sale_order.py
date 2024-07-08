from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection=[
            ('draft', "Add To Cart"),
            ('sent', "Checkout"),
            ('sale', "Sales Order"),
            ('done', "Locked"),
            ('cancel', "Cancelled"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
