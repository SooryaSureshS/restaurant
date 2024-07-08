# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _order = 'website_sequence_product'

    website_sequence_product = fields.Integer(
        string='Product sequence')
    tab_ids = fields.Many2many('product.tab','product_tab_table','tab_ids','product_ids',string="Tab")
    sku_id =fields.Char(string="SKU")
    year =fields.Date(string="Year")
    tag_ids = fields.Many2many("product.tag",string="Tag")
    product_label_id = fields.Many2one('product.label.bizople',string="Product Label")

class ProductTag(models.Model):
    _name = "product.tag"
    _description = "Product Tag"


    name = fields.Char("Name")
    sequence = fields.Integer("Sequence")

class ProductTab(models.Model):
    _name = 'product.tab'
    _description = 'Product Tab'

    name = fields.Char(string="Name",translate=True)
    sequence = fields.Integer(string="Sequence", default=1)
    content = fields.Html(string="Content",translate=True)
    product_ids = fields.Many2many('product.template','product_tab_table','product_ids','tab_ids', string="product")

class Website(models.Model):
    _inherit = 'website'

    @api.model
    def get_categories(self):
        category_ids = self.env['product.public.category'].search(
            [('parent_id', '=', False)])
        res = {
            'categories': category_ids,
        }
        return res

class ProductLabelBizople (models.Model):
     _name = 'product.label.bizople'
     _description = 'Product Label'
     
     _SELECTION_STYLE = [
        ('rounded', 'Rounded'),
        ('outlinesquare', 'Outline Square'),
        ('outlineround', 'Outline Rounded'),
        ('flat', 'Flat'),
    ]
     
     name = fields.Char(string="Name", translate=True, required=True)
     label_bg_color = fields.Char(string="Label Background Color", required=True,default="#f6513b")
     label_font_color = fields.Char(string="Label Font Color", required=True, default="#ffffff")
     label_style = fields.Selection(
        string='Label Style', selection=_SELECTION_STYLE, default='rounded')
