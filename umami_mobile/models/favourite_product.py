from odoo import models, fields


class FavouriteProduct(models.Model):
    _name = 'favourite.product'

    product_id = fields.Many2one('product.template')
    partner_id = fields.Many2one('res.partner')