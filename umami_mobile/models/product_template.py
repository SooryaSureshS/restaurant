from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    is_menu = fields.Boolean('Include in menu')
    rating = fields.Selection([
        ('1', '1 Star'),
        ('2', '2 Star'),
        ('3', '3 Star'),
        ('4', '4 Star'),
        ('5', '5 Star'),
    ], string='Rating',help="Rating",default='3')


