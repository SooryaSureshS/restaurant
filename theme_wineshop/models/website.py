# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo.http import request

class Website(models.Model):
    _inherit = "website"

    @api.model
    def get_brand_data(self):
        brand_ids = self.env['product.brand'].sudo().search([('visible_snippet', '=', True)])
        return brand_ids

    @api.model
    def get_product_category_data(self):
        category_ids = self.env['product.public.category'].sudo().search([('visible_snippet', '=', True)])
        return category_ids
    
    def get_product_brands(self, category, **post):
        domain = []
        if category:
            cat_id = []
            if category != None:
                for ids in category:
                    cat_id.append(ids.id)
                domain += ['|', ('public_categ_ids.id', 'in', cat_id),
                           ('public_categ_ids.parent_id', 'in', cat_id)]
        else:
            domain = []
        product_ids = self.env["product.template"].sudo().search(domain)
        domain_brand = [
            ('product_ids', 'in', product_ids.ids or []), ('product_ids', '!=', False)]
        brands = self.env['product.brand'].sudo().search(domain_brand)
        return brands

    def get_blog_data(self):
        biz_blog = request.env['blog.post'].search([])
        print(biz_blog);
        return biz_blog;

    def get_blog_tag(self):
        biz_blog_tag = request.env['blog.tag'].search([])
        print(biz_blog_tag);
        return biz_blog_tag;