# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    optional_product_type = fields.Selection(
        [('variant', 'Variant'), ('addon', 'Addon')],
        string='Optional Product Type')

