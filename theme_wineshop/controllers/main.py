# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import re
import math
import json
import os
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo import http, SUPERUSER_ID, fields
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website_sale.controllers import main
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute

class WineWebsiteSale(WebsiteSale):

    @http.route(['/shop/pager_selection/<model("product.per.page.count.bizople"):pl_id>'], type='http', auth="public", website=True, sitemap=False)
    def product_page_change(self, pl_id, **post):
        request.session['default_paging_no'] = pl_id.name
        main.PPG = pl_id.name
        return request.redirect(request.httprequest.referrer or '/shop')

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>''',
        '''/shop/brands'''
    ], type='http', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, brands=None, **post):
        if request.env['website'].sudo().get_current_website().theme_id.name == 'theme_wineshop':
            add_qty = int(post.get('add_qty', 1))
            Category = request.env['product.public.category']
            if category:
                category = Category.search(
                    [('id', '=', int(category))], limit=1)
                if not category or not category.can_access_from_current_website():
                    raise NotFound()
            else:
                category = Category
            if brands:
                req_ctx = request.context.copy()
                req_ctx.setdefault('brand_id', int(brands))
                request.context = req_ctx
            result = super(WineWebsiteSale, self).shop(
                page=page, category=category, search=search, ppg=ppg, **post)
            page_no = request.env['product.per.page.count.bizople'].sudo().search(
                [('default_active_count', '=', True)])
            if page_no:
                ppg = int(page_no.name)
            else:
                ppg = result.qcontext['ppg']

            ppr = request.env['website'].get_current_website().shop_ppr or 4

            attrib_list = request.httprequest.args.getlist('attrib')
            attrib_values = [[int(x) for x in v.split("-")]
                             for v in attrib_list if v]
            attributes_ids = {v[0] for v in attrib_values}
            attrib_set = {v[1] for v in attrib_values}

            domain = self._get_search_domain(search, category, attrib_values)

            url = "/shop"
            if search:
                post["search"] = search
            if attrib_list:
                post['attrib'] = attrib_list
            if post:
                request.session.update(post)

            Product = request.env['product.template'].with_context(
                bin_size=True)
            session = request.session
            cate_for_price = None
            search_product = Product.search(domain)
            website_domain = request.website.website_domain()
            pricelist_context, pricelist = self._get_pricelist_context()
            categs_domain = [('parent_id', '=', False)] + website_domain
            if search:
                search_categories = Category.search(
                    [('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
                categs_domain.append(('id', 'in', search_categories.ids))
            else:
                search_categories = Category
            categs = Category.search(categs_domain)

            if category:
                url = "/shop/category/%s" % slug(category)
                cate_for_price = int(category)
            prevurl = request.httprequest.referrer
            if prevurl:
                if not re.search('/shop', prevurl, re.IGNORECASE):
                    request.session['pricerange'] = ""
                    request.session['min1'] = ""
                    request.session['max1'] = ""
                    request.session['curr_category'] = ""
            brand_list = request.httprequest.args.getlist('brand')
            brand_list = [unslug(x)[1] for x in brand_list]
            brand_set = set([int(v) for v in brand_list])
            if brand_list:
                brandlistdomain = list(map(int, brand_list))
                domain += [('brand_id', 'in', brandlistdomain)]
                bran = []
                brand_obj = request.env['product.brand'].sudo().search(
                    [('id', 'in', brandlistdomain)])
                if brand_obj:
                    for vals in brand_obj:
                        if vals.name not in bran:
                            bran.append((vals.name, vals.id))
                    if bran:
                        request.session["brand_name"] = bran
            if not brand_list:
                request.session["brand_name"] = ''
            product_count = len(search_product)
            is_price_slider = request.website.viewref(
                'theme_wineshop.avi_price_slider_layout').active
            if is_price_slider:
                # For Price slider
                is_discount_hide = True if request.website.get_current_pricelist(
                ).discount_policy == 'with_discount' or request.website.get_current_pricelist(
                ).discount_policy == 'without_discount' else False
                product_slider_ids = []
                if is_discount_hide:
                    price_list = Product.search(domain).mapped('price')
                    if price_list:
                        product_slider_ids.append(min(price_list))
                        product_slider_ids.append(max(price_list))

                else:
                    asc_product_slider_ids = Product.search(
                        domain, limit=1, order='list_price')
                    desc_product_slider_ids = Product.search(
                        domain, limit=1, order='list_price desc')
                    if asc_product_slider_ids:
                        product_slider_ids.append(
                            asc_product_slider_ids.price if is_discount_hide else asc_product_slider_ids.list_price)
                    if desc_product_slider_ids:
                        product_slider_ids.append(
                            desc_product_slider_ids.price if is_discount_hide else desc_product_slider_ids.list_price)
                if product_slider_ids:
                    if post.get("range1") or post.get("range2") or not post.get("range1") or not post.get("range2"):
                        range1 = min(product_slider_ids)
                        range2 = max(product_slider_ids)
                        result.qcontext['range1'] = math.floor(range1)
                        result.qcontext['range2'] = math.ceil(range2)
                    if request.session.get('pricerange'):
                        if cate_for_price and request.session.get('curr_category') and request.session.get('curr_category') != float(cate_for_price):
                            request.session["min1"] = math.floor(range1)
                            request.session["max1"] = math.ceil(range2)

                    if session.get("min1") and session["min1"]:
                        post["min1"] = session["min1"]
                    if session.get("max1") and session["max1"]:
                        post["max1"] = session["max1"]
                    if range1:
                        post["range1"] = range1
                    if range2:
                        post["range2"] = range2
                    if range1 == range2:
                        post['range1'] = 0.0

                    if request.session.get('min1') or request.session.get('max1'):
                        if is_discount_hide:
                            price_product_list = []
                            product_withprice = Product.search(domain)
                            for prod_id in product_withprice:
                                if prod_id.price >= float(request.session['min1']) and prod_id.price <= float(request.session['max1']):
                                    price_product_list.append(prod_id.id)

                            if price_product_list:
                                domain += [('id', 'in',
                                            price_product_list)]
                            else:
                                domain += [('id', 'in', [])]
                        else:
                            domain += [('list_price', '>=', float(request.session.get('min1'))),
                                       ('list_price', '<=', float(request.session.get('max1')))]
                        request.session["pricerange"] = str(
                            request.session['min1']) + "-To-" + str(request.session['max1'])

                    if session.get('min1') and session['min1']:
                        result.qcontext['min1'] = session["min1"]
                        result.qcontext['max1'] = session["max1"]
            if cate_for_price:
                request.session['curr_category'] = float(cate_for_price)
            if request.session.get('default_paging_no'):
                ppg = int(request.session.get('default_paging_no'))
            keep = QueryURL('/shop', category=category and int(category),
                            search=search, attrib=attrib_list, order=post.get('order'))
            product_count = Product.search_count(domain)
            pager = request.website.pager(
                url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            products = Product.search(
                domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

            ProductAttribute = request.env['product.attribute']
            if products:
                # get all products without limit
                attributes = ProductAttribute.search(
                    [('product_tmpl_ids', 'in', search_product.ids)])
            else:
                attributes = ProductAttribute.browse(attributes_ids)

            layout_mode = request.session.get('website_sale_shop_layout_mode')
            if not layout_mode:
                if request.website.viewref('website_sale.products_list_view').active:
                    layout_mode = 'list'
                else:
                    layout_mode = 'list'
            active_brand_list = list(set(brand_set))
            result.qcontext.update({
                'search': search,
                'category': category,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'pager': pager,
                'pricelist': pricelist,
                'add_qty': add_qty,
                'products': products,
                'search_count': product_count,  # common for all searchbox
                'bins': TableCompute().process(products, ppg, ppr),
                'ppg': ppg,
                'ppr': ppr,
                'categories': categs,
                'attributes': attributes,
                'keep': keep,
                'search_categories_ids': search_categories.ids,
                'layout_mode': layout_mode,
                'brand_set': brand_set,
                'active_brand_list': active_brand_list,
            })
            return result
        else:
            return super(WineWebsiteSale, self).shop(page=page, category=category, search=search, ppg=ppg, **post)




class bizcommonSliderSettings(http.Controller):

    def get_blog_data(self, slider_filter):
        slider_header = request.env['biz.blog.slider'].sudo().search(
            [('id', '=', int(slider_filter))])
        values = {
            'slider_header': slider_header,
            'blog_slider_details': slider_header.blog_post_ids,
        }
        return values

    def get_categories_data(self, slider_id):
        slider_header = request.env['biz.category.slider'].sudo().search(
            [('id', '=', int(slider_id))])
        values = {
            'slider_header': slider_header
        }
        values.update({
            'slider_details': slider_header.category_ids,
        })
        return values


    @http.route(['/theme_wineshop/blog_get_options'], type='json', auth="public", website=True,sitemap=False)
    def bizcommon_get_slider_options(self):
        slider_options = []
        option = request.env['biz.blog.slider'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options



    @http.route(['/theme_wineshop/second_blog_get_dynamic_slider'], type='http', auth='public', website=True, sitemap=False)
    def second_get_dynamic_slider(self, **post):
        if post.get('slider-type'):
            values = self.get_blog_data(post.get('slider-type'))
            return request.render("theme_wineshop.bizcommon_blog_slider_view", values)



    @http.route(['/theme_wineshop/blog_image_effect_config'], type='json', auth='public', website=True, sitemap=False)
    def bizcommon_product_image_dynamic_slider(self, **post):
        slider_data = request.env['biz.blog.slider'].search(
            [('id', '=', int(post.get('slider_filter')))])
        values = {
            's_id': str(slider_data.no_of_objects) + '-' + str(slider_data.id),
            'counts': slider_data.no_of_objects,
            'auto_slide': slider_data.auto_slide,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values


    @http.route(['/theme_wineshop/category_get_options'], type='json', auth="public", website=True, sitemap=False)
    def category_get_slider_options(self):
        slider_options = []
        option = request.env['biz.category.slider'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options


    @http.route(['/theme_wineshop/category_slider_3'], type='http', auth='public', website=True, sitemap=False)
    def category_slider_value(self, **post):
        if post.get('slider-id'):
            values = self.get_categories_data(post.get('slider-id'))
            return request.render("theme_wineshop.s_bizople_theme_category_slider_view", values)

    @http.route(['/theme_wineshop/bizcommon_image_effect_config'], type='json', auth='public', website=True, sitemap=False)
    def category_image_dynamic_slider(self, **post):
        slider_data = request.env['biz.category.slider'].search(
            [('id', '=', int(post.get('slider_id')))])
        values = {
            's_id': slider_data.name.lower().replace(' ', '-') + '-' + str(slider_data.id),
            'counts': slider_data.no_of_objects,
            'auto_slide': slider_data.auto_slide,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    @http.route(['/theme_wineshop/product_get_options'], type='json', auth="public", website=True, sitemap=False)
    def product_get_slider_options(self):
        slider_options = []
        option = request.env['biz.product.slider'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/theme_wineshop/product_get_dynamic_slider'], type='http', auth='public', website=True, sitemap=False)
    def product_get_dynamic_slider(self, **post):
        if post.get('slider-id'):
            slider_header = request.env['biz.product.slider'].sudo().search(
                [('id', '=', int(post.get('slider-id')))])
            values = {
                'slider_header': slider_header
            }
            values.update({
                'slider_details': slider_header.product_ids,
            })
            return request.render("theme_wineshop.bizople_theme_common_product_slider_view", values)

    @http.route(['/theme_wineshop/slider_product_call'], type='json', auth='public', website=True, sitemap=False)
    def product_image_dynamic_slider(self, **post):
        slider_data = request.env['biz.product.slider'].search(
            [('id', '=', int(post.get('slider_id')))])
        values = {
            's_id': slider_data.name.lower().replace(' ', '-') + '-' + str(slider_data.id),
            'counts': slider_data.no_of_objects,
            'auto_slide': slider_data.auto_slide,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    @http.route(['/theme_wineshop/product_multi_get_options'], type='json', auth="public", website=True, sitemap=False)
    def product_multi_get_slider_options(self):
        slider_options = []
        option = request.env['multi.tab.product.slider'].sudo().search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/tabpro/product_multi_get_dynamic_slider'], type='http', auth='public', website=True, sitemap=False)
    def ecomm_multi_get_dynamic_slider(self, **post):
        context, pool = dict(request.context), request.env
        if post.get('slider-type'):
            slider_header = request.env['multi.tab.product.slider'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])

            if not context.get('pricelist'):
                pricelist = request.website.get_current_pricelist()
                context = dict(request.context, pricelist=int(pricelist))
            else:
                pricelist = pool.get('product.pricelist').browse(
                    context['pricelist'])

            context.update({'pricelist': pricelist.id})
            from_currency = pool['res.users'].sudo().browse(
                SUPERUSER_ID).company_id.currency_id
            to_currency = pricelist.currency_id

            def compute_currency(price): return pool['res.currency']._convert(
                price, from_currency, to_currency, fields.Date.today())
            values = {
                'slider_details': slider_header,
                'slider_header': slider_header,
                'compute_currency': compute_currency,
            }
            return request.render("theme_wineshop.bizcommon_multi_cat_slider_view", values)


    @http.route(['/theme_wineshop/multi_tab_product_call'], type='json', auth='public', website=True, sitemap=False)
    def product_multi_product_image_dynamic_slider(self, **post):
        slider_data = request.env['multi.tab.product.slider'].sudo().search(
            [('id', '=', int(post.get('slider_filter')))])
        values = {
            's_id': slider_data.no_of_tabs + '-' + str(slider_data.id),
            'counts': slider_data.no_of_tabs,
            'auto_slide': slider_data.auto_slide,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

