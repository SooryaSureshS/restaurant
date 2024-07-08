# -*- coding: utf-8 -*-
from odoo import models,fields


class ProductTemplate(models.Model):
    _inherit = ['product.template']

    features_sale = fields.Text(strings="Features")
    additional_info = fields.Text(string="Additional Information")
    is_fragrance = fields.Boolean()


class ProductPackagingInherit(models.Model):
    _inherit = 'product.packaging'

    pack_image = fields.Binary("Pack Image")
