from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shipping_weight = fields.Float("Shipping weight in grams")
