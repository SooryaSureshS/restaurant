from odoo import models, api, fields


class ProductAttributeValueInherit(models.Model):
    _inherit = 'product.attribute.value'

    code = fields.Char('Code')

