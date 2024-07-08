# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = "product.product"
    
    
    pos_size_categ_id = fields.Many2one(
        'pos.size.category', 'POS Size Category',
        help="Select POS size category for the current product")