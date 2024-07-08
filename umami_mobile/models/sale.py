from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_status = fields.Selection([
        ('new', 'Order confirmed'),
        ('active', 'Delivering'),
        ('history', 'Delivered'),
        ('cancel','Cancel')
    ], string='Delivery status',default='new')

    payment_method = fields.Selection([('cod','COD'),('stripe','Stripe')])


