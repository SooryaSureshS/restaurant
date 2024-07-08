# Company: giordano.ch AG
# Copyright by: giordano.ch AG
# https://giordano.ch/

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "blog.post"

    product_template_ids = fields.Many2many('product.template', string='Products')
    public_categ_ids = fields.Many2many('product.public.category', string='Categories')
