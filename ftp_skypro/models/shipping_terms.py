from odoo import models, api, fields


class ShippingTerms(models.Model):
    _name = 'shipping.delivery.terms'
    _description = 'Shipping Terms'

    name = fields.Char()
    active = fields.Boolean(default=True)
    english_explanation = fields.Char()
    chinese_explanation = fields.Char()
    code = fields.Char()
    company_id = fields.Many2one('res.company', string='Company', related='product_id.company_id', store=True,
                                 readonly=False)
    product_id = fields.Many2one('product.product', string='Delivery Product', ondelete='restrict')
    zip_from = fields.Char('Zip From')
    zip_to = fields.Char('Zip To')
    margin = fields.Float(help='This percentage will be added to the shipping price.')
    free_over = fields.Boolean('Free if order amount is above',
                               help="If the order total amount (shipping excluded) is above or equal to this value, the customer benefits from a free shipping",
                               default=False)
    amount = fields.Float(string='Amount',
                          help="Amount of the order to benefit from a free shipping, expressed in the company currency")

    class SaleOrder(models.Model):
        _inherit = 'sale.order'

        shipping_term_id = fields.Many2one('shipping.delivery.terms', string="Shipping Terms",
                                           domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                           help="Fill this field if you plan to invoice the shipping based on picking.")

    class StockMoveLine(models.Model):
        _inherit = 'stock.move.line'

        shipping_term_id = fields.Many2one(related='picking_id.shipping_term_id')

    class StockPicking(models.Model):
        _inherit = 'stock.picking'

        shipping_term_id = fields.Many2one("shipping.delivery.terms", string="Shipping Terms", check_company=True)
