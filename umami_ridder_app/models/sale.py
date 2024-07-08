from odoo import models, fields


class SaleOrderInheritedRider(models.Model):
    _inherit = 'sale.order'

    latitude = fields.Char(string='latitude')
    longitude = fields.Char(string='longitude')
    delivery_boy = fields.Many2one('res.partner',string='Delivery Boy')
    # reject = fields.Boolean(string='Rejected')
    # reject_reason = fields.Char(string='Rejected Reason')
    cancel_reason = fields.Char(string='Cancel Reason')
    rejected_order_ids = fields.One2many('sale.reject', 'rejected_order_id', string="Rejected List Information")
    payment_method = fields.Selection([('cod', 'COD'), ('stripe', 'Stripe')])

class RejectedOrderLine(models.Model):
    _name = 'sale.reject'
    _description = "SaleOrderReject"

    rejected_order_id = fields.Many2one('sale.order', string="Rejected ID")
    delivery_boy = fields.Many2one('res.partner', string='Delivery Boy')
    reject_reason = fields.Char(string='Rejected Reason')





class POSOrders(models.Model):
    _inherit = 'product.template'

    returnable_product = fields.Boolean('Not Returnable')


class RespartnerView(models.Model):
    _inherit = 'res.partner'

    is_rider = fields.Boolean('Rider')
