from odoo import models, fields


class CustomMaskWebsiteSequence(models.Model):
    _name = 'custom.mask.website.sequence'

    sequence = fields.Integer()
    product_id = fields.Many2one('product.template', string="Product")
