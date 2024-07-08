# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    bulk_attribute = fields.Selection([('size', 'Size'), ('color', 'Color')], string="Bulk Attribute Type")
