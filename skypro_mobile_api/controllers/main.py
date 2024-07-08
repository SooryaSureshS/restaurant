from __future__ import absolute_import, division, print_function

import xml
from odoo.exceptions import AccessError, MissingError, ValidationError
from werkzeug.exceptions import Forbidden, NotFound
from odoo import fields, http, SUPERUSER_ID, tools, _
import passlib.context
import math, random
import json
import odoo
from odoo import http, _
from odoo.http import request
import logging
import threading
import xml.etree.ElementTree as ET
import base64
import requests
import werkzeug.urls
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import html_escape
from passlib.context import CryptContext
from hashlib import sha256
from werkzeug.urls import url_join

_logger = logging.getLogger(__name__)


# function for getting the current database
def get_db_name():
    db = odoo.tools.config['db_name']
    if not db and hasattr(threading.current_thread(), 'dbname'):
        return threading.current_thread().dbname
    return db


class Login(http.Controller):

    # function for generating OTP for verification
    def generateOTP(self):
        digits = "0123456789"
        OTP = ""
        for i in range(4):
            OTP += digits[math.floor(random.random() * 10)]

        return OTP

    # param: email, password
    @http.route('/user/login', type='json', auth="public", methods=['POST'])
    def authenticate(self):
        print('authenticate')
        try:
            data = request.httprequest.data
            data = json.loads(data)
            db = get_db_name()
            uid = request.session.authenticate(db, data.get('email', False),
                                               data.get('password', False))
            user_details = {'success': True,
                            'user_id': uid}
            return user_details
        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
            }

    # User registration api
    # param: name, phone number, email, password, confirm ,

    @http.route('/user/register', type='json', auth="public", methods=['POST', 'GET'], csrf=False)
    def user_register(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            if data.get('email'):
                if request.env['res.partner'].sudo().search([('email', '=', data.get('email'))]):
                    return {
                        'status': 0,
                        'message': "The given email is already registered"
                    }
                else:
                    partner = request.env['res.partner'].sudo().create(
                        {'name': data.get('first_name') + ' ' + data.get('last_name'),
                         'first_name': data.get('first_name'),
                         'last_name': data.get('last_name'),
                         'email': data.get('email'),
                         'mobile': data.get('mobile')
                         })
                    print('partner', partner)
                    group_portal_user = request.env.ref('base.group_portal')
                    user = request.env['res.users'].sudo().create({
                        'company_id': request.env.company.id,
                        'email': data.get('email'),
                        'name': data.get('first_name') + ' ' + data.get('last_name'),
                        'login': data.get('email'),
                        'partner_id': partner.id,
                        'new_password': data.get('password'),
                        'groups_id': [(6, 0, [group_portal_user.id])],
                        'totp_enabled': True
                    })
                    if user:
                        user.write({'password': data.get('password'), 'new_password': data.get('password')})

                        return {'success': True,
                                'user_id': user.id,
                                'name': data.get('first_name') + ' ' + data.get('last_name'),
                                'first_name': data.get('first_name'),
                                'last_name': data.get('last_name'),
                                'email': data.get('email'),
                                'mobile': data.get('mobile'),
                                'message': "User Is Created"
                                }

        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # forgot password api
    # param: email
    @http.route('/forgot/password', type='json', auth="public", methods=['POST', 'GET'], csrf=False)
    def forgot_password(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            email_id = data.get('email')
            if email_id:
                user_id = request.env['res.users'].sudo().search([('email', '=', email_id)])
                if user_id:
                    otp = self.generateOTP()
                    body_html = '''<div style="margin: 0px; padding: 0px;">
                                                    <p style="margin: 0px; padding: 0px; font-size: 13px;">
                                                        Hi ''' + user_id.name + ''',
                                                        <br/><br/>
                                                         <p>
                                                            Please find the OTP number ''' + otp + ''' for your password reset 
            
                                                            <br/>
                                                            <br/>
                                                        Thank you
                                                    </p>
                                                </div>'''
                    mail = request.env['ir.mail_server'].sudo().search([], limit=1)
                    mail_from = mail.smtp_user
                    template_obj = request.env['mail.mail'].sudo().search([], limit=1)
                    template_data = {
                        'subject': 'Password Reset OTP',
                        'body_html': body_html,
                        'email_from': mail_from,
                        'email_to': user_id.email
                    }
                    template_id = template_obj.create(template_data)
                    template_id.sudo().send()
                    user_id.write({
                        'user_otp': otp
                    })
                    _logger.info("-------otp-sended-------")
                    return {'success': True, 'otp': otp, 'mail_sent': "Password reset mail sent"}

                return {
                    'status': 0,
                    'message': "Email doesn't registered or exist"
                }
        except Exception as e:
            return {
                'status': 0,
                'message': "Email doesn't registered or exist"
            }

    # forgot password api for OTP verification
    # param : email,otp

    @http.route('/forgot/password/verify', type='json', auth="public", methods=['POST'], csrf=False)
    def forgot_password_verify(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            email_id = data.get('email')
            otp = data.get('otp')
            if email_id and otp:
                user_id = request.env['res.users'].sudo().search([('email', '=', email_id), ('user_otp', '=', otp)])
                if user_id:
                    return {'success': True, 'message': "OTP Verified"}
                else:
                    return {
                        'status': 0,
                        'message': "OTP/Email you have entered is incorrect"
                    }
            return {
                'status': 0,
                'message': "Email doesn't registered or exist"
            }
        except Exception as e:
            return {
                'status': 0,
                'message': "Email doesn't registered or exist"
            }

    # rest password api
    # param : password,confirmed ,password ,email

    def _set_encrypted_password(self, uid, pw):
        assert self._crypt_context().identify(pw) != 'plaintext'

        self.env.cr.execute(
            'UPDATE res_users SET password=%s WHERE id=%s',
            (pw, uid)
        )
        self.invalidate_cache(['password'], [uid])

    @http.route('/reset/password', type='json', auth="public", methods=['POST'], csrf=False)
    def reset_password(self):
        ctx = passlib.context.CryptContext(
            ['pbkdf2_sha512', 'plaintext'],
            deprecated=['plaintext'],
        )
        try:
            data = request.httprequest.data
            data = json.loads(data)
            email_id = data.get('email')
            password = data.get('password')
            confirmed_password = data.get('confirmed_password')
            if password == confirmed_password:
                user_id = request.env['res.users'].sudo().search([('email', '=', email_id)])
                if user_id:
                    hash_password = ctx.hash if hasattr(ctx, 'hash') else ctx.encrypt
                    user_id._set_encrypted_password(user_id.id, hash_password(confirmed_password))
                    user_id.user_otp = ""
                    return {'success': True, 'message': "New Password has been reset"}
                else:
                    return {
                        'status': 0,
                        'message': "Passwords are not match"
                    }
            return {
                'status': 0,
                'message': "Passwords are not match"
            }
        except Exception as e:
            return {
                'status': 0,
                'message': "Passwords are not match"
            }

    # api for  homepage, listing the products

    @http.route('/homepage', type="json", auth="public", methods=['GET', 'POST'], csrf=False)
    def homepage(self):
        try:
            url = request.httprequest.host_url
            products = request.env['product.template'].sudo().search(
                [('is_published', '=', True), ('is_mask_product', '=', True)], limit=3)
            published_products = []
            for product in products:
                if product.image_1920:
                    published_products.append({'product_id': product.id,
                                               'name': product.name,
                                               'description': product.description or product.name,
                                               'sale_price': product.list_price,
                                               'image': url + 'web/image/product.template/' + str(product.id) + '/image_1920'})
            return {'success': True, 'published_products': published_products}
        except Exception as e:
            return {
                'status': 0,
                'message': "There is no Products is published to the website"
            }

    # Homepage product Description
    # param {product ID}
    @http.route('/product/detail', type="json", auth="public", methods=['GET', 'POST'], csrf=False)
    def product_detail(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            product_id = data.get('product_id')
            url = request.httprequest.host_url
            product = request.env['product.template'].sudo().search([('is_mask_product', '=', True),
                                                                     ('id', '=', product_id)])
            products_details = {'product_id': product.id,
                                'name': product.name,
                                'min_qty': product.minimum_order_quantity,
                                'min_qty_step': product.minimum_quantity_step,
                                'product_features': product.features or '',
                                'product_description': product.discription or '',
                                'product_chinese_description': product.discription_chinese or '',
                                'product_additional_info': product.additional_information or "",
                                'sale_price': product.list_price,
                                # 'image': url + "product/image/" + str(product.id) + "/image",
                                'image': url + 'web/image/product.template/' + str(product_id) + '/image_1920',
                                'nose_pad_image': url + 'web/image/product.template/' + str(product_id) + '/nose_pad_image',
                                'logo_image': url + 'web/image/product.template/' + str(product_id) + '/logo_image',
                                'full_image': url + 'web/image/product.template/' + str(product_id) + '/full_image',
                                'blank_image': url + 'web/image/product.template/' + str(product_id) + '/blank_image',
                                'preview_full_image': url + 'web/image/product.template/' + str(product_id) + '/preview_full_area',
                                'preview_logo_image': url + 'web/image/product.template/' + str(product_id) + '/preview_logo_area'
                                }
            return {'success': True, 'products_details': products_details}
        except Exception as e:
            return {
                'status': 0,
                'message': "There is no Products With this ID",
                'error': e
            }

    def remove_tag(self, data):
        return ''.join(ET.fromstring(data).itertext())

    @http.route('/product/ptavs/detail', type="json", auth="public", methods=['GET', 'POST'], csrf=False)
    def product_ptav(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            pid = data.get('pid')
            ptavs = request.env['product.template.attribute.value'].sudo().search([('product_tmpl_id.id', '=', int(pid))])
            attributes = {
                'print_type': [],
                'nose_sponge': [],
                'cloth_color': [],
                'earloop_color': [],
                'mask_size': []
            }
            for ptav in ptavs:
                if ptav.attribute_id.name == 'Print type':
                    attributes['print_type'].append({
                        'id': ptav.id,
                        'attribute_name': ptav.attribute_id.name,
                        'value': ptav.name,
                        'code': ptav.product_attribute_value_id.code,
                        'extra_price': ptav.price_extra,
                        'color': ptav.product_attribute_value_id.html_color,
                    })
                elif ptav.attribute_id.name == 'Nose sponge':
                    attributes['nose_sponge'].append({
                        'id': ptav.id,
                        'attribute_name': ptav.attribute_id.name,
                        'value': ptav.name,
                        'code': ptav.product_attribute_value_id.code,
                        'extra_price': ptav.price_extra,
                        'color': ptav.product_attribute_value_id.html_color,
                    })
                elif ptav.attribute_id.name == 'Cloth color':
                    attributes['cloth_color'].append({
                        'id': ptav.id,
                        'attribute_name': ptav.attribute_id.name,
                        'value': ptav.name,
                        'code': ptav.product_attribute_value_id.code,
                        'extra_price': ptav.price_extra,
                        'color': ptav.product_attribute_value_id.html_color,
                    })
                elif ptav.attribute_id.name == 'Earloop color':
                    attributes['earloop_color'].append({
                        'id': ptav.id,
                        'attribute_name': ptav.attribute_id.name,
                        'value': ptav.name,
                        'code': ptav.product_attribute_value_id.code,
                        'extra_price': ptav.price_extra,
                        'color': ptav.product_attribute_value_id.html_color,
                    })
                elif ptav.attribute_id.name == 'Mask size':
                    attributes['mask_size'].append({
                        'id': ptav.id,
                        'attribute_name': ptav.attribute_id.name,
                        'value': ptav.name,
                        'code': ptav.product_attribute_value_id.code,
                        'extra_price': ptav.price_extra,
                        'color': ptav.product_attribute_value_id.html_color,
                    })
            return {
                'status': 1,
                'pid': pid,
                'mask_colors': [attribute['color'] for attribute in attributes['cloth_color']],
                'rope_colors': [attribute['color'] for attribute in attributes['earloop_color']],
                'ptavs': attributes
            }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    @http.route('/packing/images/get', type="json", auth="public", methods=['GET', 'POST'], csrf=False)
    def get_carton_package_images(self):
        try:
            url = request.httprequest.host_url
            data = request.httprequest.data
            data = json.loads(data)
            product_tmpl_id = data.get('product_tmpl_id')
            return {
                'status': 1,
                'message': 'Success',
                'package_image': url + 'web/image/product.template/' + product_tmpl_id + '/package_image',
                'carton_image': url + 'web/image/product.template/' + product_tmpl_id + '/carton_image',
            }
        except Exception as e:
            return {
               'status': 0,
               'message': e
            }

    """default product.product is passed if no ptav_ids are passed
    else product.product with corresponding ptav_ids is passed"""
    @http.route('/product/variant', type="json", auth="public", methods=['GET', 'POST'], csrf=False)
    def product_variant(self):
        try:
            url = request.httprequest.host_url
            data = request.httprequest.data
            data = json.loads(data)
            product_tmpl_id = data.get('product_tmpl_id')
            attributes = data.get('attributes')
            if not attributes:
                return {
                    'status': 0,
                    'message': 'Missing product attributes'
                }
            pt = request.env['product.template'].sudo().browse(int(product_tmpl_id))
            qty = data.get('qty') if data.get('qty') else pt.minimum_order_quantity
            print_type = int(attributes.get('print_type')) if attributes.get('print_type') else False
            nose_sponge = int(attributes.get('nose_sponge')) if attributes.get('nose_sponge') else pt.default_nose_attribute.id if pt.default_nose_attribute else False
            cloth_color = int(attributes.get('cloth_color')) if attributes.get('cloth_color') else pt.default_mask_attribute.id if pt.default_mask_attribute else False
            earloop_color = int(attributes.get('earloop_color')) if attributes.get('earloop_color') else pt.default_rope_attribute.id if pt.default_rope_attribute else False
            mask_size = int(attributes.get('mask_size')) if attributes.get('mask_size') else False
            # fragrance = attributes.get('fragrance')
            if print_type and nose_sponge and cloth_color and earloop_color and mask_size:
                products = request.env['product.product'].sudo().search([('product_tmpl_id.id', '=', product_tmpl_id)]).filtered(
                    lambda p: print_type in p.product_template_variant_value_ids.ids
                              and nose_sponge in p.product_template_variant_value_ids.ids
                              and cloth_color in p.product_template_variant_value_ids.ids
                              and earloop_color in p.product_template_variant_value_ids.ids
                              and mask_size in p.product_template_variant_value_ids.ids
                              # and fragrance in p.product_template_variant_value_ids.ids
                )
                if not products:
                    return {
                       'status': 0,
                       'message': 'No Product variant found'
                    }
                product_variant = products[0]
                website_pricelist = int(
                    request.env['ir.config_parameter'].sudo().get_param('mask_cutomization.website_price_list'))
                pricelist = request.env['product.pricelist'].search([('id', '=', int(website_pricelist))], limit=1)
                price = product_variant.lst_price
                if pricelist:
                    for item in pricelist.item_ids.search([('id', 'in', pricelist.item_ids.ids)], order="min_quantity"):
                        if item.product_id.id == product_variant.id:
                            if item.min_quantity <= float(qty):
                                price = item.fixed_price
                else:
                    price = product_variant.lst_price
                amount = float(price) * float(qty)
                return {
                    'status': 1,
                    'product': {
                        'id': product_variant.id,
                        'name': product_variant.name,
                        'amount': amount
                    }
                }
            else:
                return {
                    'status': 0,
                    'message': 'Missing product attribute %s' %('print_type' if not print_type else 'nose_sponge' if not nose_sponge else 'cloth_color' if not cloth_color else 'earloop_color' if not earloop_color else 'mask_size' if not mask_size else 'fragrance')
                }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # auth="user"
    @http.route('/customize/mask', type="json", auth="user", methods=['GET', 'POST'], csrf=False, website=True)
    def customize_mask(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user_obj = request.env['res.users'].sudo().search([('id', '=', request.uid)])
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            website = request.env['website'].browse(request.website_routing)
            sale_order = request.website.sale_get_order(force_create=True)
            # sale_order = request.env['sale.order'].sudo().search([('state', 'in', ['draft']),
            #                                                       ('website_id', '=', website.id),
            #                                                       ('user_id', '=', user_obj.id)], limit=1)
            print('saleeeeeee', sale_order)
            product_id = data.get('product_id')
            qty = data.get('qty')
            stock_quant = request.env['stock.quant'].sudo().search(
                [('product_id', '=', product_id), ('on_hand', '=', True)])
            available_qty = sum([int(stock.quantity) for stock in stock_quant])
            # if sale_order and available_qty < qty:
            if not sale_order:
                print("wwwwwwwwwweeweq")
                sale_order = self.create_sale_order(user_obj, website)
                product_obj = request.env['product.product'].sudo().search([('id', '=', data.get('product_id'))])
                vals = {n.display_name.split(":")[0]: n.name for n in product_obj.product_template_variant_value_ids if
                        n.display_name}
                sale_order.upload_your_image = data.get('mask_image') if data.get(
                    'mask_image') else None
                sale_order.mask_size = 'adult' if vals.get('Mask size') == "Adult" else "child" if vals.get(
                    'Mask size') == "Child" else ""
                sale_order.mask_area = 'logo' if vals.get('Print type') == "Logo" else "full" if vals.get(
                    'Print type') == "Full" else "blank" if vals.get('Print type') == "Blank" else ""
                return {'success': True,
                        'sale_order_line_id': sale_order.id,
                        'product_id': product_id,
                        'Iframe_fold_url': url_join(base_url,
                                                    f"/mask/design/load/{product_id}/{sale_order.id}/fold"),
                        'Iframe_3d_url': url_join(base_url,
                                                  f"/mask/design/load/{product_id}/{sale_order.id}/3d"),
                        'available_quantity': available_qty,
                        'message': f"We are not able to process your Order. You ask for {qty} products but only {stock_quant.quantity} is available."
                        }

            order_line = self.update_create_sale_order_line(data, sale_order)
            vals =  {'success': True,
                    'sale_order_id': sale_order.id,
                    'product_id': product_id,
                    'sale_order_line_id': order_line.id,
                    'available_quantity': available_qty,
                    # 'upload_your_image': data.get('mask_image') if data.get(
                    #         'mask_image') else None,
                    'Iframe_fold_url': url_join(base_url,
                                                f"/mask/design/load/{product_id}/{sale_order.id}/fold"),
                    'Iframe_3d_url': url_join(base_url,
                                              f"/mask/design/load/{product_id}/{sale_order.id}/3d"),
                    'message': "Customized Mask successfully"
                    }
            if available_qty < qty:
                # vals['available_quantity'] = available_qty,
                vals['message'] = f"We are not able to process your Order. You ask for {qty} products but only {stock_quant.quantity} is available."
            return vals
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    @staticmethod
    def create_sale_order(user_obj, website):
        sale_order_obj = request.env['sale.order']
        sale_order_val = {
            'partner_id': user_obj.partner_id.id,
            'partner_invoice_id': user_obj.partner_id.id,
            'partner_shipping_id': user_obj.partner_id.id,
            'date_order': datetime.now(),
            'pricelist_id': user_obj.partner_id.property_product_pricelist.id,
            'state': 'draft',
            'picking_policy': 'direct',
            'user_id': user_obj.id,
            'website_id': website.id,
        }
        return sale_order_obj.sudo().create(sale_order_val)

    @staticmethod
    def update_create_sale_order_line(data, sale_order):
        product_obj = request.env['product.product'].sudo().search([('id', '=', data.get('product_id'))])
        vals = {n.display_name.split(":")[0]: n.name for n in product_obj.product_template_variant_value_ids if n.display_name}
        sale_order.upload_your_image = data.get('mask_image') if data.get(
            'mask_image') else None
        sale_order.mask_size = 'adult' if vals.get('Mask size') == "Adult" else "child" if vals.get('Mask size') == "Child" else ""
        sale_order.mask_area = 'logo' if vals.get('Print type') == "Logo" else "full" if vals.get('Print type') == "Full" else "blank" if vals.get('Print type') == "Blank" else ""
        return sale_order.order_line.sudo().create({
            'order_id': sale_order.id,
            'product_id': product_obj.id,
            'product_template_id': product_obj.product_tmpl_id.id,
            'name': product_obj.description_sale or 'DES',
            'product_uom_qty': data.get('qty'),
            'product_uom': product_obj.uom_id.id,
            'price_unit': product_obj.lst_price,
            'customer_lead': 0,
            'price_subtotal': product_obj.lst_price * data.get('qty'),
            # 'mask_size': data.get('print_area'),
            'upload_your_image': data.get('mask_image') if data.get(
                'mask_image') else None
        })

    @http.route('/customize/packing', type="json", auth="user", methods=['POST'], csrf=False)
    def customize_packing(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            sale_order_id = data.get('sale_order_id')
            product_id = data.get('product_id')
            pack_image = data.get('pack_image')
            sale_order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
            packing_id = [order_line.product_packaging_id.id for order_line in
                          request.env['sale.order.line'].sudo().search([
                              ('order_id', '=', sale_order_id), ('product_id', '=', product_id)]) if
                          order_line.product_packaging_id]
            for rec in packing_id:
                product_packing = request.env['product.packaging'].sudo().search([('id', '=', rec)])
                product_packing.update({
                    'package_image': pack_image if pack_image else None
                })
            return {'success': True,
                    'sale_order_id': sale_order.id,
                    'message': "Packaging Image Added Successfully"
                    }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    @http.route('/customize/carton', type="json", auth="user", methods=['POST'], csrf=False)
    def customize_carton(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            sale_order_id = data.get('sale_order_id')
            product_id = data.get('product_id')
            carton_image = data.get('carton_image')
            sale_order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
            packing_id = [order_line.product_packaging_id.id for order_line in
                          request.env['sale.order.line'].sudo().search([
                              ('order_id', '=', sale_order_id), ('product_id', '=', product_id)]) if
                          order_line.product_packaging_id]
            for rec in packing_id:
                product_packing = request.env['product.packaging'].sudo().search([('id', '=', rec)])
                product_packing.update({
                    'carton_image': carton_image if carton_image else None,
                    'carton_package': True
                })
            return {'success': True,
                    'sale_order_id': sale_order.id,
                    'message': "Carton Image Added Successfully"
                    }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    @http.route('/customise/cart', type="json", auth="user", methods=['GET', 'POST'], csrf=False)
    def customize_cart(self):
        try:
            url = request.httprequest.host_url
            user_obj = request.env['res.users'].sudo().search([('id', '=', request.uid)])
            website = request.env['website'].browse(request.website_routing)
            sale_order = request.env['sale.order'].sudo().search([('state', 'in', ['draft', 'sent']),
                                                                  ('website_id', '=', website.id),
                                                                  ('partner_id.id', '=', user_obj.partner_id.id)], limit=1)

            order_lis = self.website_sale_order_get(url, sale_order)
            # nose_pad =
            # sale_order.with_nose_pad = nose_pad
            print("sale_ordcustomier",order_lis)
            # if not sale_order:
            #     sale_order = self.create_sale_order(user_obj, website)
            order_lis = self.website_sale_order_get(url, sale_order)
            print("order_list",order_lis)
            # for rec in order_lis:
            #     print(type(rec['qty']))
            #     ordered_qty = rec['qty']
            #     stock_quant = request.env['stock.quant'].sudo().search(
            #         [('product_id', '=', rec['product_id']), ('on_hand', '=', True)])
            #     available_qty = sum([int(stock.quantity) for stock in stock_quant])
                # if available_qty < ordered_qty:
                #     # order_lis = self.website_sale_order_get(url, sale_order)
                #     product_obj = request.env['product.product'].sudo().search([('id', '=',  rec['product_id'])])
                #
                #     print('oooooooo', ordered_qty)
                #     sale_order.order_line.sudo().create({
                #         'order_id': sale_order.id,
                #         'product_id': product_obj.id,
                #         'product_template_id': product_obj.product_tmpl_id.id,
                #         'name': product_obj.description_sale or 'DES',
                #         'product_uom_qty': rec['qty'],
                #         'product_uom': product_obj.uom_id.id,
                #         'price_unit': product_obj.lst_price,
                #         'customer_lead': 0,
                #         'price_subtotal': product_obj.lst_price * rec['qty'],
                #         # 'mask_size': data.get('print_area'),
                #         'upload_your_image': rec['mask_image'] if rec['mask_image'] else None
                #     })
            # min_qty_step= product.minimum_quantity_step
            print("lllllllll",order_lis)
            total_amount = 0
            for rec in sale_order.order_line:
                total_amount += rec.price_subtotal
            return {'success': True,
                    'sale_order': sale_order.id,
                    'order_data': order_lis,
                    'total_amount': total_amount,
                    'message': "Cart Product Details" if sale_order.id else "Your cart is empty!"
                    }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    @staticmethod
    def website_sale_order_get(url, sale_order):
        order_lis = []
        optional_products = [line for line in sale_order.order_line if line.linked_line_id]
        val = {}
        for rec in sale_order.order_line:
            if rec.product_template_id.sale_ok:
                val.update({rec.id: {'product_name': rec.product_template_id.name, 'qty': rec.product_uom_qty,
                               'order_line': rec.id, 'product_id': rec.product_id.id, 'area': rec.print_area,
                               'product_image': url + 'web/image/product.product/' + str(rec.product_id.id) + '/image1920',
                               'mask_image': url + 'web/image/sale.order.line/' + str(rec.id) + '/upload_your_image',
                               'package_image': url + 'web/image/product.packaging/' + str(
                                   rec.product_packaging_id.id) + '/pack_image',
                               'unit_price': rec.product_id.lst_price, 'price_subtotal': rec.price_subtotal,'with_nose_pad':bool(rec.with_nose_pad),'nose_pad_price':rec.price_nose_pad},})
        for options in optional_products:
            product_data = val[options.linked_line_id.id]
            list(map(lambda x: val[options.id].pop(x), ['mask_image', 'package_image', 'area']))
            if options.product_template_id.is_nose_pad:
                product_data['nose_pad'] = val[options.id]
            if options.product_template_id.is_fragrance:
                product_data['fragrance'] = val[options.id]
            order_lis.append(product_data) if product_data not in order_lis else None
        list(map(lambda n: val.pop(n), [pro.id for pro in optional_products]))
        list(map(lambda n: val.pop(n), list(set(pro.linked_line_id.id for pro in optional_products))))
        [order_lis.append(x) for x in [n for n in val.values()]]
        return order_lis

    @http.route('/cart/empty/item', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def remove_item(self):
        try:
            url = request.httprequest.host_url
            data = request.httprequest.data
            data = json.loads(data)
            line_obj = request.env['sale.order.line'].sudo().search([('id', '=', data.get('line_id'))])
            sale_order_obj = line_obj.order_id
            if line_obj:
                line_obj.sudo().unlink()
                order_lis = self.website_sale_order_get(url, sale_order_obj)
                return {'success': True,
                        'sale_order': sale_order_obj.id,
                        'order_data': order_lis,
                        'message': "Cart Product Details" if sale_order_obj.id else "Your cart is empty!"
                        }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    @http.route('/cart/update/item', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def cart_update_item(self):
        try:
            url = request.httprequest.host_url
            data = request.httprequest.data
            data = json.loads(data)
            line_id = data.get('line_id')
            qty = data.get('qty')
            order_line = request.env['sale.order.line'].sudo().search([('id', '=', line_id)])
            sale_order_id = order_line.order_id
            sale_order_lines = [line for line in order_line.option_line_ids]
            sale_order_lines.append(order_line)
            for rec in sale_order_lines:
                product = request.env['product.product'].sudo().search([('id', '=', rec.product_id.id)])
                print("productid",product)
                rec.product_uom_qty = qty
                # rec.price_subtotal = product.lst_price * qty
            order_lis = self.website_sale_order_get(url, sale_order_id)
            return {'success': True,
                    'sale_order': sale_order_id,
                    'order_data': order_lis,
                    'message': "Cart Product Details" if order_line.order_id.id else "Your cart is empty!"
                    }

        except Exception as e:
            return {
                'status': 0,
                'message': e
            }


    # api for editing the profile
    @http.route('/user/edit/get', type='json', auth="user", methods=['GET', 'POST'], csrf=False)
    def edit_details_get(self):
        try:
            countries = Login.get_country_list()
            states = Login.get_state_list()
            return {'success': True,
                    'countries': countries,
                    'states': states,
                    'message': "Get Sucessfully"
                    }

        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # api for editing the profile
    @http.route('/user/edit/post', type='json', auth="user", methods=['GET', 'POST'], csrf=False)
    def edit_details_post(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user_id = data.get('user_id')
            user_obj = request.env['res.users'].sudo().search([('id', '=', user_id)])
            if user_obj:
                dict = {
                    'name': data.get('name'),
                    'email': data.get('email'),
                    'phone': data.get('phone'),
                    'company_name': data.get('company_name'),
                    'street': data.get('street'),
                    'state_id': int(data.get('state')),
                    'zip': data.get('zip'),
                    'country_id': int(data.get('country'))
                }
                print('dct', dict,user_obj)
                partner = request.env['res.partner'].sudo().search([('id','=',user_obj.partner_id.id)])
                if partner.write(dict):
                    return {'success': True,
                            'user_id': user_obj.id,
                            'message': "Successfully Updated"
                              }

        except Exception as e:
            return {
                'status': 0,
                'message': e
            }














































































    @http.route('/order/delivery_address/get', type="json", auth="user", methods=['GET', 'POST'], csrf=False)
    def order_delivery_address_get(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            order_id = data.get('sale_order_id')
            order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
            post = {}
            values = self.checkout_values(order, **post)
            values.update({'website_sale_order': order})
            countries = self.get_country_list()
            states = self.get_state_list()
            return {'success': True,
                    'sale_order': order.id,
                    'address_data': values.get('delivery_address'),
                    'mode': values.get('mode'),
                    'partner_id': values.get('delivery_address')['id'] if values.get('delivery_address') else None,
                    'countries': countries,
                    'states': states,
                    'message': "Delivery Address"
                    }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    @http.route('/order/delivery_address/post', type="json", auth="user", methods=['GET', 'POST'], csrf=False)
    def order_delivery_address_post(self):
        try:
            url = request.httprequest.host_url
            data = request.httprequest.data
            website = request.env['website'].browse(request.website_routing)
            data = json.loads(data)
            order_id = data.get('sale_order_id')
            order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
            mode = data.get('mode')
            pre_values = self.values_preprocess(data.get('address_data'))
            errors, error_msg = self.checkout_form_validate(mode, data.get('address_data'), pre_values)
            if errors:
                return {
                    'status': False,
                    'message': error_msg
                }
            post = self.values_postprocess(order, mode, pre_values, website)
            partner_id = self._checkout_form_save(mode, post, data, order)
            order.partner_shipping_id = partner_id
            order.message_partner_ids = [(4, partner_id), (3, website.partner_id.id)]
            return self.payment_methods(order=order, url=url)
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    @staticmethod
    def get_state_list():
        state = request.env['res.country.state'].sudo().search([])
        state_lis = []
        for rec in state:
            state_lis.append(
                {'id': rec.id, 'name': rec.name, 'country_id': rec.country_id.id})
        return state_lis

    @staticmethod
    def get_country_list():
        country = request.env['res.country'].sudo().search([])
        country_lis = []
        for rec in country:
            country_lis.append(
                {'id': rec.id, 'name': rec.name})
        return country_lis

    @staticmethod
    def checkout_values(order, **kw):
        delivery_address = []
        website = request.env['website'].browse(request.website_routing)
        if order.partner_id != website.user_id.sudo().partner_id:
            Partner = order.partner_id.with_context(show_address=1).sudo()
            shipping = Partner.search([
                ("id", "child_of", order.partner_id.commercial_partner_id.ids),
                '|', ("type", "in", ["delivery", "other"]), ("id", "=", order.partner_id.commercial_partner_id.id)
            ], order='id desc')
            if shipping:
                if kw.get('partner_id') or 'use_billing' in kw:
                    if 'use_billing' in kw:
                        partner_id = order.partner_id.id
                    else:
                        partner_id = int(kw.get('partner_id'))
                    if partner_id in shipping.mapped('id'):
                        order.partner_shipping_id = partner_id
            delivery_address = [{'name': address.name,
                                 'id': address.id,
                                 'company_name': address.parent_id.name,
                                 'phone': address.phone,
                                 'street': address.street,
                                 'street2': address.street2,
                                 'city': address.city,
                                 'state_id': {'id': address.state_id.id,
                                              'name': address.state_id.name} if address.state_id else {},
                                 'zip': address.zip,
                                 'country_id': {'id': address.country_id.id, 'name': address.country_id.name}} for
                                address in list(filter(lambda ship: ship == order.partner_shipping_id, shipping))]
        return {
            'delivery_address': delivery_address[0] if delivery_address else None,
            'mode': 'edit' if delivery_address else 'new'
        }

    @staticmethod
    def values_preprocess(values):
        partner_fields = request.env['res.partner']._fields
        return {
            k: (bool(v) and int(v)) if k in partner_fields and partner_fields[k].type == 'many2one' else v
            for k, v in values.items()
        }

    @staticmethod
    def values_postprocess(order, mode, values, website):
        new_values = {}
        authorized_fields = request.env['ir.model']._get('res.partner')._get_form_writable_fields()
        for k, v in values.items():
            if k in authorized_fields and v is not None:
                new_values[k] = v
            else:
                if k not in ('field_required', 'partner_id', 'callback', 'submitted'):  # classic case
                    _logger.debug("website_sale postprocess: %s value has been dropped (empty or not writable)" % k)

        if website.specific_user_account:
            new_values['website_id'] = website.id

        if mode == 'new':
            new_values['company_id'] = website.company_id.id
            new_values['team_id'] = website.salesteam_id and website.salesteam_id.id
            new_values['user_id'] = website.salesperson_id.id
        new_values['parent_id'] = order.partner_id.commercial_partner_id.id
        new_values['type'] = 'delivery'

        return new_values

    @staticmethod
    def checkout_form_validate(mode, all_form_values, data):
        error = dict()
        error_message = []
        required_fields = ['name', 'phone', 'street', 'city', 'zip', 'country_id']
        for field_name in required_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message

    @staticmethod
    def _checkout_form_save(mode, checkout, all_values, order):
        Partner = request.env['res.partner']
        if mode == 'new':
            partner_id = Partner.sudo().with_context(tracking_disable=True).create(checkout).id
        elif mode == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                shippings = Partner.sudo().search([("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                    return Forbidden()
                Partner.browse(partner_id).sudo().write(checkout)
        return partner_id

    @http.route('/order/payment_methods', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def payment_methods(self, order=False, url=False):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            url = url if url else request.httprequest.host_url
            order_id = data.get('sale_order_id')
            acquirer_obj = request.env['payment.acquirer'].sudo().search([('state', '=', 'enabled')])
            if not acquirer_obj:
                acquirer_obj = request.env['payment.acquirer'].sudo().search([('state', '=', 'test')])
            order = order if order else request.env['sale.order'].sudo().search([('id', '=', order_id)])
            # total_amount = request.env['sale.order'].sudo().search
            total_amount = order.amount_total
            delivery_amount = order.amount_delivery
            applied_coupon = order.applied_coupon_ids
            reward_amount = order.reward_amount
            amount_before_reward = -(reward_amount)+(total_amount)

            # print("order",amount_undiscounted)
            acquirer_list = []
            order_data = self.website_sale_order_get(url, order)
            if acquirer_obj:
                for acquirer in acquirer_obj:
                    acquirer_dict = {'id': acquirer.id, 'name': acquirer.name}
                    acquirer_list.append(acquirer_dict)
            return {'success': True,
                    'payment_methods': acquirer_list,
                    'order_data': order_data,
                    'sub_total' : total_amount,
                    'sale_order_id': order.id,
                    'delivery_amount' :delivery_amount,
                    'applied_coupon': [coupon.code for coupon in order.applied_coupon_ids],
                    'reward_amount' : reward_amount,
                    'amount_before_reward' : amount_before_reward,
                    'message': 'Payment Methods Fetched Successfully'
                    }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    @http.route('/customize/mask/test', type="json", auth="user", methods=['GET', 'POST'], csrf=False)
    def customize_mask_test(self):
        try:
            # data = request.httprequest.data
            # data = json.loads(data)
            # user_obj = request.env['res.users'].sudo().search([('id', '=', request.uid)])
            # website = request.env['website'].browse(request.website_routing)
            # sale_order = request.env['sale.order'].sudo().search([('state', 'in', ['draft']),
            #                                                       ('website_id', '=', website.id),
            #                                                       ('user_id', '=', user_obj.id)], limit=1)

            return {'success': True,
                    'sale_order_id': "test",
                    'product_id': "test",
                    'message': "Customized Mask successfully"
                    }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    @http.route('/account/information', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def user_details(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user_id = data.get('user_id')
            user_obj = request.env['res.users'].sudo().search([('id', '=', user_id)])
            if user_obj:
                dict = {}
                dict['id'] = user_obj.id
                dict['name'] = user_obj.partner_id.name
                dict['email'] = user_obj.partner_id.email
                dict['phone'] = user_obj.partner_id.phone
                dict['street'] = user_obj.partner_id.street
                dict['street2'] = user_obj.partner_id.street2
                dict['country'] = user_obj.partner_id.country_id.name
                dict['state'] = user_obj.partner_id.state_id.name
                return {'success': True,
                        'user_id': user_obj.id,
                        'userdetails': dict,
                        'message': "User Details Fetched Successfully"
                        }

        except Exception as e:
            return {
                'status': 0,
                'message': e
            }
