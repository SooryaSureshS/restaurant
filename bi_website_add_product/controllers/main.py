# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound
_logger = logging.getLogger(__name__)



from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.osv import expression

class website_add_product(http.Controller):

    @http.route(['/shop/cart/update_with_values'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update(self, product_id, add_qty=1, checkout_note=None, set_qty=0, **kw):
        print("cart update values")
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

        line = sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )

        if line['line_id']:
            order_line = request.env['sale.order.line'].sudo().search([('id', '=', line['line_id'])])
            if order_line:
                    order_line.sudo().write({'checkout_note': checkout_note})
        if kw.get('express'):
            return request.redirect("/shop/checkout?express=1")

        name = request.env['product.product'].sudo().search(
            [('id', '=', product_id)]).website_url
        if kw.get('shop'):
            return request.redirect("/shop")
        qty = 0

        if sale_order.order_line:
            sorted_product = sorted(sale_order.order_line, key=lambda x: x.product_id.pos_categ_id.sequence)
            print(sorted_product)
            seq = 0
            for k in sorted_product:
                print(k.product_id.name)
                k.sudo().write({'sequence': seq})
                for i in sale_order.order_line:
                    if i.linked_line_id:
                        i.sudo().write({'sequence': i.linked_line_id.sequence})
                seq += 1

        if sale_order:
            order_main = sale_order.order_line.filtered(lambda line: line.product_template_id.is_optional_product != True and len(line.linked_line_id) == 0)
            qty = int(sum(order_main.mapped('product_uom_qty')))
            return qty
        return False

    @http.route(['/shop/cart/update_qty_data'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_qty_data(self, **kw):
        print("cart update values e")
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        qty = 0;
        if sale_order.order_line:
            sorted_product = sorted(sale_order.order_line, key=lambda x: x.product_id.pos_categ_id.sequence)
            print(sorted_product)
            seq = 0
            for k in sorted_product:
                print(k.product_id.name)
                k.sudo().write({'sequence': seq})
                for i in sale_order.order_line:
                    if i.linked_line_id:
                        i.sudo().write({'sequence': i.linked_line_id.sequence})
                seq += 1

        if sale_order:
            order_main = sale_order.order_line.filtered(lambda line: line.product_template_id.is_optional_product != True and len(line.linked_line_id) == 0)
            sale_order.cart_quantity = int(sum(order_main.mapped('product_uom_qty')))
            return sale_order.cart_quantity
        return False

    @http.route(['/shop/get_bundle_data'], type='json', auth="public", methods=['POST'], website=True)
    def getBundleValues(self, product_id, **kw):

        total_count = 0
        if product_id:
            product_data = []
            qty_item = []
            product = request.env['product.product'].sudo().search([('id', '=', int(product_id))])
            if product and product.is_bundle_product:
                if product.bundle_product_ids:
                    for pro in product.bundle_product_ids:

                        bundle_prods = []
                        for pros in pro.product_id:
                            optional_product = []
                            groups = pros.optional_product_ids.mapped('product_option_group')
                            for grp in groups:
                                optional_grp = {'optional_product_id': grp.id, 'optional_product_name': grp.name}
                                optional = pros.optional_product_ids.filtered(
                                    lambda r: r.product_option_group.id == grp.id)
                                opt_pro = []
                                for opt in optional:
                                    opt_pro.append({'product_id': opt.id,
                                                    'product_name': opt.name,
                                                    'price': opt.list_price,
                                                    })

                                optional_grp['products'] = opt_pro
                                optional_product.append(optional_grp)
                            bundle_image_url = '/web/image/product.product/' + str(pro.id) + '/image_128'

                            bundle_prods.append({
                                'choice_product_id': pros.id,
                                'choice_product_name': pros.name,
                                'bundle_extra_price': pros.bundle_extra_price,
                                'optional_product_length': len(optional_product),
                                'optional_product': optional_product,
                                'choice_image_url': bundle_image_url,
                            })
                        total_count = total_count + int(pro.qty)
                        product_data.append({
                            'bundle_product_name': pro.bundle_name,
                            'bundle_product_id': pro.id,
                            'bundle_product_qty': pro.qty,
                            'choice_products': bundle_prods,
                        })
                        qty_item.append(pro.qty)
                    image_url = '/web/image/product.product/' + str(product.id) + '/image_128'
                    vals = {
                        'product': product.id,
                        'image_url': image_url,
                        'add_qty': 1,
                        'bundle_qty': qty_item,
                        'price': product.lst_price,
                        'description': product.description_sale,
                        'parent_name': product.name,
                        'variant_values': product_data,
                        'total_count': total_count
                    }

                    print("OPPO", vals)
                    return vals

                else:
                    return False
            else:
                return False
        else:
            return False

    @http.route(['/get/novariable/popup/details'], type='json', auth="public", methods=['POST'], website=True)
    def no_variable(self, product_id, **kw):
        product_obj = request.env['product.product'].sudo().browse([int(product_id)])
        if product_obj:
            data = {'name':product_obj.name,'description':product_obj.description_sale if product_obj.description_sale else '','product_id':product_id,
                    'image_url':'/web/image/product.product/'+product_id+'/image_128','price':product_obj.list_price}
            print("DDdd",data)
            return data
        else:
            return False


# class WebsiteSale(WebsiteSale):
#
#     @http.route(['/shop/checkoutrrr/fgggf'], type='http', auth="public", website=True, sitemap=False)
#     def checkoute(self, **post):
#         order = request.website.sale_get_order()
#         if order:
#             holiday_surcharge = request.env['ir.config_parameter'].sudo().get_param('bi_website_add_product.holiday_surcharge')
#             start_date = request.env['ir.config_parameter'].sudo().get_param('bi_website_add_product.start_date')
#             end_date = request.env['ir.config_parameter'].sudo().get_param('bi_website_add_product.end_date')
#             start_date_date_time_obj = datetime.strptime(start_date, '%Y-%m-%d')
#             end_date_date_time_obj = datetime.strptime(end_date, '%Y-%m-%d')
#
#             if holiday_surcharge == "True":
#                 now = fields.Datetime.now()
#                 if now >= start_date_date_time_obj and now <= end_date_date_time_obj:
#                     check_holiday = order.order_line.mapped('name')
#                     if "Holiday surcharge" not in check_holiday:
#                         choose_price = request.env['ir.config_parameter'].sudo().get_param('bi_website_add_product.choose_price')
#                         if choose_price == 'percentage':
#                             percentage_amount = float(request.env['ir.config_parameter'].sudo().get_param('bi_website_add_product.percentage'))
#                             if percentage_amount != 0:
#                                 amount_percentage = (percentage_amount/100) * order.amount_total
#                                 surcharge_product = request.env['product.template'].sudo().search([('name', '=', "Holiday surcharge")])
#                                 if not surcharge_product:
#                                     surcharge_product_id = request.env['product.template'].sudo().create({'name': "Holiday surcharge",
#                                                                         'list_price': amount_percentage,
#                                                                         'standard_price': amount_percentage,
#                                                                         'type': 'service',
#                                                                         'supplier_taxes_id': None})
#                                     request.env['sale.order.line'].sudo().create({
#                                         'order_id': order.id,
#                                         'customer_lead': 1,
#                                         'product_id': surcharge_product_id.product_variant_id.id,
#                                         'product_uom_qty': 1.0,
#                                         'price_unit': surcharge_product_id.list_price
#                                     })
#                                 if surcharge_product:
#                                     surcharge_product.sudo().write({'list_price': amount_percentage})
#                                     request.env['sale.order.line'].sudo().create({
#                                         'order_id': order.id,
#                                         'customer_lead': 1,
#                                         'product_id': surcharge_product.product_variant_id.id,
#                                         'product_uom_qty': 1.0,
#                                         'price_unit': surcharge_product.list_price
#                                     })
#                                 else:
#                                     pass
#
#                             else:
#                                 pass
#                         else:
#                             amount = float(request.env['ir.config_parameter'].sudo().get_param('bi_website_add_product.amount'))
#                             surcharge_product = request.env['product.product'].sudo().search([('name', '=', "Holiday surcharge")])
#                             if not surcharge_product:
#                                 surcharge_product_id = request.env['product.template'].sudo().create({'name': "Holiday surcharge",
#                                                                                                'list_price': amount,
#                                                                                                 'type': 'service',
#                                                                                                'standard_price': amount,
#                                                                                                'supplier_taxes_id': None})
#                                 product_created = request.env['sale.order.line'].sudo().create({
#                                         'order_id': order.id,
#                                         'customer_lead': 1,
#                                         'product_id': surcharge_product_id.product_variant_id.id,
#                                         'product_uom_qty': 1.0,
#                                         'price_unit': surcharge_product_id.list_price
#                                     })
#                             if surcharge_product:
#                                 surcharge_product.sudo().write({'list_price': amount})
#
#                                 product_created = request.env['sale.order.line'].sudo().create({
#                                         'order_id': order.id,
#                                         'customer_lead': 1,
#                                         'product_id': surcharge_product.product_variant_id.id,
#                                         'product_uom_qty': 1.0,
#                                         'price_unit': surcharge_product.list_price
#                                     })
#                             else:
#                                 pass
#
#                     if "Holiday surcharge" in check_holiday:
#                         surcharge = order.order_line.search([("name", '=', "Holiday surcharge")], limit=1)
#                         amount_order = order.amount_total - surcharge.price_unit
#                         surcharge_product = request.env['product.product'].sudo().search(
#                             [('name', '=', "Holiday surcharge")])
#                         if surcharge_product:
#                             choose_price = request.env['ir.config_parameter'].sudo().get_param(
#                                 'bi_website_add_product.choose_price')
#                             if choose_price == 'percentage':
#                                 percentage_amount = float(request.env['ir.config_parameter'].sudo().get_param(
#                                     'bi_website_add_product.percentage'))
#                                 amount_percentage = (percentage_amount / 100) * amount_order
#                                 surcharge.write({'price_unit': amount_percentage})
#                             if choose_price == 'amount':
#                                 amount = float(request.env['ir.config_parameter'].sudo().get_param(
#                                     'bi_website_add_product.amount'))
#                                 surcharge.write({'price_unit': amount})
#
#
#             else:
#                 pass
#
#         redirection = self.checkout_redirection(order)
#         if redirection:
#             return redirection
#
#         if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
#             return request.redirect('/shop/address')
#
#         # redirection = self.checkout_check_address(order)
#         # if redirection:
#         #     return redirection
#
#         values = self.checkout_values(**post)
#
#         if post.get('express'):
#             return request.redirect('/shop/confirm_order')
#
#         values.update({'website_sale_order': order})
#
#         # Avoid useless rendering if called in ajax
#         if post.get('xhr'):
#             return 'ok'
#         return request.render("website_sale.checkout", values)


    # @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    # def cart(self, access_token=None, revive='', **post):
    #     """
    #     Main cart management + abandoned cart revival
    #     access_token: Abandoned cart SO access token
    #     revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
    #     """
    #     order = request.website.sale_get_order()