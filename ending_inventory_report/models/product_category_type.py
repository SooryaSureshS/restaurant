from odoo import models, fields, api, _


class ProductCategoryType(models.Model):
    _name = 'product.category.types'
    _description = "Product category Type"

    name = fields.Char( string="Product Category Type")