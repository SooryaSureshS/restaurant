import werkzeug

from odoo import _, exceptions, http
from odoo.http import request
from odoo.tools import consteq
from odoo.addons.theme_wineshop.controllers.main import WineWebsiteSale
# from odoo.addons.theme_clarico.controllers.track_item import Website
import qrcode
import base64
import io

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

# commented payments
import base64
import json
import pytz
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_sale.controllers.main import WebsiteSale
import geopy.distance
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from datetime import datetime
from operator import itemgetter
from timeit import itertools
from itertools import groupby
from datetime import date
from odoo import http, api, fields, models, _
import datetime
from datetime import date
from odoo.addons.website_qr_code.controllers.main import WineWebsiteSaleQrcode


class WineWebsiteSaleQrcodeInherited(WineWebsiteSaleQrcode):

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>''',
        '''/shop/brands''',
        '''/qr/shop/<string:qr>'''
    ], type='http', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, brands=None, qr=None, **post):
        if request.env['website'].sudo().get_current_website().theme_id.name == 'theme_wineshop':
            sale_order_new = request.website.sale_get_order(force_create=True)
            if sale_order_new and qr == 'scan':
                sale_order_new.sudo().write({
                    'qrcode_order': True
                })
            add_qty = int(post.get('add_qty', 1))
            Category = request.env['product.public.category']
            if category:
                category = Category.search(
                    [('id', '=', int(category))], limit=1)
                if category.child_id:
                    category = category.child_id[0]
                if not category or not category.can_access_from_current_website():
                    raise NotFound()
            else:
                category = Category.search([], limit=1, order='sequence asc')
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
                        if cate_for_price and request.session.get('curr_category') and request.session.get(
                                'curr_category') != float(cate_for_price):
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
                                if prod_id.price >= float(request.session['min1']) and prod_id.price <= float(
                                        request.session['max1']):
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
            return super(WineWebsiteSaleQrcodeInherited, self).shop(page=page, category=category, search=search, ppg=ppg, **post)



    @http.route(['/shop/merge/check'], type='json', auth="public", methods=['POST'], website=True)
    def shop_cart_merge(self, name=None, phone=None, email=None, table=None, **kw):
        """This route is called when adding a product to cart (no options)."""

        sale_order = request.website.sale_get_order(force_create=True)
        # print("KKKKKKKKKKKKKKKKKK", table)
        print("pre table",table,sale_order)
        invalid_product = False
        enable_qr_code_merge = request.env['ir.config_parameter'].sudo().get_param('website_qr_order_merge.enable_qr_code_merge')
        qr_code_merge_time = request.env['ir.config_parameter'].sudo().get_param('website_qr_order_merge.qr_code_merge_time')
        if sale_order and enable_qr_code_merge and qr_code_merge_time and table:
            from datetime import timedelta
            pre_order_for_merge = request.env['sale.order'].sudo().search([('dine_in_table','=', int(table)),('parent_id','=',False)],order='id DESC', limit=1)
            if pre_order_for_merge:
                tz = pytz.timezone(sale_order.company_id.tz or 'UTC')
                sale_order_time_zone = pre_order_for_merge.date_order.astimezone(tz)
                now = fields.Datetime.now().astimezone(tz)
                print("time",qr_code_merge_time)
                print("found",pre_order_for_merge)
                # estimation = sale_order.date_order.astimezone(tz) + timedelta(hours=0, minutes=pos_min_kitchen_display_time)
                user_tz = pytz.timezone( request.env.user.tz or request.env.context.get('tz') or 'UTC')
                # today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
                # date_start = today.astimezone(pytz.timezone('UTC'))
                print("pre ggggggggggggggggggggg", tz,sale_order_time_zone,qr_code_merge_time)
                print("pre rrrrrrrrrrrrr", now)
                from datetime import date
                today = date.today()
                print("Today's date:", today)
                if today ==  pre_order_for_merge.date_order.date():
                    print("Today's date:", pre_order_for_merge.date_order.date())
                    difference = str(now - sale_order_time_zone)
                    print("pre diidddddd", difference)
                    delta = timedelta(hours=int(difference.split(':')[0]), minutes=int(difference.split(':')[1]), seconds=int(difference.split(':')[2]))
                    minutes = delta.total_seconds() / 60
                    print(minutes)
                    print(qr_code_merge_time)
                    # pos_order_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(difference) * 60, 60))
                    # pos_kitchen_pre_order_time = datetime.strptime(pos_order_time, '%H:%M').time()
                    # pos_tot_secs = (pos_kitchen_pre_order_time.hour * 60 + pos_kitchen_pre_order_time.minute) * 60 + pos_kitchen_pre_order_time.second
                    # pos_min_kitchen_display_time = pos_tot_secs / 60
                    if float(minutes) <= float(qr_code_merge_time):
                        print("sucesss   ssss")
                        print("pre wwwwwwwwwwwwww", difference)
                        # print("pre qqqqqqqqqqqqqqq", pos_min_kitchen_display_time)
                        print("pre qqq", user_tz,request.env.user.tz,request.env.context.get('tz'))
                        return {'status': 'merge','merge_order': pre_order_for_merge.name, 'partner': pre_order_for_merge.partner_id.name, 'table': pre_order_for_merge.dine_in_table.name,'parent_id': pre_order_for_merge.id}
                    else:
                        return {'status': 'ok'}
                return {'status': 'ok'}
            else:
                return {'status': 'ok'}
        else:
            return {'status': 'ok'}



    @http.route(['/shop/cart/address/merge'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_merge(self, name=None, phone=None, email=None, table=None, parent_id=None, **kw):
        """This route is called when adding a product to cart (no options)."""
        # S21469
        sale_order = request.website.sale_get_order(force_create=True)
        print("KKKKKKKKKKKKKKKKKK", table,parent_id)
        print("KKKKKKKKKKKKKKKKKK", sale_order)
        parent_order = request.env['sale.order'].sudo().search([('id','=',parent_id)],limit=1)
        parent_order.write({
            'merge_order': True
        })
        sale_order.write({
            'parent_id': parent_order.id,
        })

        invalid_product = False
        if sale_order:
            order_data = request.env['sale.order'].sudo().search([('id', '=', int(sale_order.id))])
            if sale_order.website_delivery_type == 'pickup':
                if order_data.order_line:
                    for pro in order_data.order_line:
                        if pro.product_id.not_available_for_pickup:
                            invalid_product = True
            if invalid_product:
                val = {"status": "invalid_products"}
                return val


        old_user = request.env['res.users'].sudo().search([('login', '=', str(email))])
        if old_user:
            new_partner1 = request.env['res.partner'].sudo().search([('id', '=', old_user.partner_id.id)])
            new_partner1.sudo().write({'phone': phone, 'email': str(email)})
            country = request.env['res.country'].sudo().search([('code', '=', 'AU')], limit=1).id
            company = request.env['res.company'].sudo().browse(request.website.company_id.id)
            state_id = request.env['res.country.state'].sudo().search([('code', '=', 'QLD')], limit=1).id

            val = {
                'company_type': 'person',
                'parent_id': new_partner1.id,
                'type': 'delivery',
                'name': str(name),
                'phone': int(phone),
                'email': str(email),
            }

            child = request.env['res.partner'].sudo().create(val)
            request.env.cr.commit()
            child.sudo().write({
                'country_id': company.country_id,
                'state_id': company.state_id,
                'zip': company.zip,
                'street': company.street,
                'street2': company.street2,
                'city': company.city
            })

            sale_order.onchange_partner_shipping_id()
            sale_order.order_line._compute_tax_id()
            request.session['sale_last_order_id'] = sale_order.id
            request.website.sale_get_order(update_pricelist=True)

            sale_order.sudo().write({'partner_id': child.id})
            sale_order.sudo().write({'carrier_id': 1})
            sale_order.sudo().write({
                'partner_shipping_id': child.id,
                'partner_invoice_id': child.id,
                'public_partner': child.id,
                'carrier_id': 1,
                'dine_in_table': table if table else False
            })
            if sale_order.sudo().partner_id:
                return True
            else:
                return False
        else:
            val = {
                'name': str(name),
                'login': str(email),
                'groups_id': [(4, request.env.ref('base.group_portal').id)]
            }
            user = request.env['res.users']
            new_user = user.sudo().create(val)
            new_partner = request.env['res.partner'].sudo().search([('id', '=', new_user.partner_id.id)])
            company = request.env['res.company'].sudo().browse(request.website.company_id.id)
            country = request.env['res.country'].sudo().search([('code', '=', 'AU')], limit=1).id
            # state_id = request.env['res.country.state'].sudo().search([('code', '=', 'QLD')], limit=1).id
            new_partner.write({
                'country_id': company.country_id,
                'state_id': company.state_id,
                'zip': company.zip,
                'street': company.street,
                'street2': company.street2,
                'city': company.city
            })
            # order.sudo().write({
            #     'partner_shipping_id': users.partner_id.id,
            #     'partner_invoice_id': users.partner_id.id,
            #     'public_partner': users.partner_id.id,
            #     'carrier_id': 3
            # })
            new_partner.sudo().write({'phone': phone, 'email': str(email)})
            sale_order.sudo().write({'partner_id': new_partner.id})
            sale_order.sudo().write({'carrier_id': 1})
            sale_order.sudo().write({
                'partner_shipping_id': new_partner.id,
                'partner_invoice_id': new_partner.id,
                'public_partner': new_partner.id,
                'dine_in_table': table if table else False
            })
            if sale_order.sudo().partner_id:
                return True
            else:
                return False
