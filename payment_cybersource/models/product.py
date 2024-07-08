from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_discount_product = fields.Boolean(default=False)
