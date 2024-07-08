from odoo import models, fields, api, _




class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    category_type_id = fields.Many2one('product.category.types', string="Category")

