from __future__ import absolute_import, division, print_function

import json
import odoo
from odoo import http, _
from odoo.http import request
import logging
import threading
import base64
import werkzeug.urls
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import html_escape
# import stripe

_logger = logging.getLogger(__name__)

# function for getting the current database
def get_db_name():
    db = odoo.tools.config['db_name']
    if not db and hasattr(threading.current_thread(), 'dbname'):
        return threading.current_thread().dbname
    return db

class login(http.Controller):

    def get_auth_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""
        data = request.httprequest.data
        data = json.loads(data)
        get_param = request.env['ir.config_parameter'].sudo().get_param
        return {
            'signup_enabled': request.env['res.users']._get_signup_invitation_scope() == 'b2c',
            'reset_password_enabled': get_param('auth_signup.reset_password') == 'True',
            'login': data.get('email'),
        }

    def get_auth_signup_qcontext(self):
        qcontext = request.params.copy()
        """ Shared helper returning the rendering context for signup and reset password """
        qcontext.update(self.get_auth_signup_config())
        if not qcontext.get('token') and request.session.get('auth_signup_token'):
            qcontext['token'] = request.session.get('auth_signup_token')
        if qcontext.get('token'):
            try:
                token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext

    # Function for reset password
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        data = request.httprequest.data
        data = json.loads(data)
        _logger.info("1111111111111111")
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            _logger.info("111111111ssssferewteg1111111")
            raise werkzeug.exceptions.NotFound()
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    _logger.info("pspfjidshkfjbg")
                    self.do_signup(qcontext)
                    _logger.info ("maniniknaihdniad")
                    return self.web_login(*args, **kw)
                else:
                    login = qcontext.get('login')
                    _logger.info(login)
                    assert login, _("No login provided.")
                    m = request.env['res.users'].sudo().reset_password(login)
            except Exception as e:
                _logger.info("3333333333333")
                qcontext['error'] = str(e)

    @http.route('/user/register', type='json', auth="public", methods=['POST'], csrf=False)
    def user_register(self):
        # User registration api
        # param: username, email, password, confirm ,
        try:
            data = request.httprequest.data
            data = json.loads(data)
            if data.get('name') and data.get('email'):
                if request.env['res.partner'].sudo().search([('email','=',data.get('email'))]):
                    return {
                        'status': 0,
                        'message': "The given email is already registered"
                    }
                else:
                    partner = request.env['res.partner'].sudo().create({'name': data.get('name'),
                                                                        'email': data.get('email'),
                                                                        'mobile': data.get('mobile')
                                                                        })
                    group_portal_user = request.env.ref('base.group_portal')
                    user = request.env['res.users'].sudo().create({
                                                                   'company_id': request.env.company.id,
                                                                   'email': data.get('email'),
                                                                   'name': data.get('name'),
                                                                   'login': data.get('email'),
                                                                   'partner_id': partner.id,
                                                                   'new_password': data.get('password'),
                                                                   'groups_id': [(6, 0, [group_portal_user.id])],
                                                                   'totp_enabled': True
                                                                   })
                    if user:
                        user.write({'password':data.get('password'), 'new_password': data.get('password')})

                    return {'status': 1,
                            'user_id': user.id}

        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
            }


    # forgot password api
    # param: username, email, password, confirm
    @http.route('/forgot/password', type='json', auth="public", methods=['POST'], csrf=False)
    def forgot_password(self):

        try:
            data = request.httprequest.data
            data = json.loads(data)
            if data.get('email'):
                user = request.env['res.users'].sudo().search([('email', '=', data.get('email'))])
                _logger.info("1111111111333333333")
                _logger.info(user)
                if user:
                    self.web_auth_reset_password()
                    _logger.info("poiuyyttrtdcgcxhgzxc")
                    return {'status': 1, 'mail_sent': "Password reset mail sent"}
                else:
                    return {
                        'status': 0,
                        'message': "Email doesn't registered or exist"
                    }
        except Exception as e:
            return {
                'status': 0,
                'message': "Email doesn't registered or exist"
            }

    # param: email, password
    @http.route('/user/login', type='json', auth="public", methods=['POST'], csrf=False)
    def authenticate(self):

        try:
            data = request.httprequest.data
            data = json.loads(data)
            db = get_db_name()
            uid = request.session.authenticate(db, data.get('username', False),
                                               data.get('password', False))

            user_details = {'status': 1,
                             'user_id': uid}

            return user_details

        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
                    }


    # api for user homepage, listing the products
    # param: email, password
    @http.route('/user/homepage', type='json', auth="public", methods=['POST'], csrf=False)
    def homepage(self):

        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                menu_items = request.env['product.template'].sudo().search([('available_in_pos', '=', True)])
                product_menu_items = []
                trending_products = []
                order = request.env['sale.order'].sudo().search(
                    [('date_order', '<', datetime.today() + relativedelta(days=7))])
                order_lines_ids = order.mapped('order_line').ids
                order_lines = request.env['sale.order.line'].sudo().browse(order_lines_ids)
                product_ids = order_lines.mapped('product_id').ids
                products = request.env['product.template'].sudo().browse(product_ids)
                products = products.sudo().search([('available_in_pos', '=', True)])
                for product in products:
                    if request.env['product.template'].sudo().search([('id', '=', product.id)]).name:
                        if product.image_1920:
                            trending_products.append({'product_id': product.id,
                                                      'name': product.name,
                                                      'description': product.description or product.name,
                                                      'rating': int(product.rating),
                                                      'sale price': product.list_price,
                                                      'image': url + "product/image/" + str(product.id) + "/.jpeg"})
                        else:
                            demo_img = request.env['product.template'].sudo().search([], limit=1)
                            trending_products.append({'product_id': product.id,
                                                      'name': product.name,
                                                      'description': product.description or product.name,
                                                      'rating': int(product.rating),
                                                      'sale price': product.list_price,
                                                      'image': url + "product/image/" + str(demo_img.id) + "/.jpeg"})

                    else:
                        pass
                for item in menu_items:
                    if request.env['product.template'].sudo().search([('id', '=', item.id)]).name:
                        if item.image_1920:
                            product_menu_items.append({
                                'name': item.name,
                                'product_id': item.id,
                                'description': item.description or item.name,
                                'rating': int(item.rating),
                                'sale price': item.list_price,
                                'image': url + "product/image/" + str(item.id) + "/.jpeg" or ''
                            })
                        else:
                            demo_img = request.env['product.template'].sudo().search([],limit=1)
                            product_menu_items.append({
                                'name': item.name,
                                'product_id': item.id,
                                'description': item.description or item.name,
                                'rating': int(item.rating),
                                'sale price': item.list_price,
                                'image': url + "product/image/" + str(demo_img.id) + "/.jpeg"})

                    else:
                        pass
                return {'status': 1, 'products': product_menu_items, 'trending_products': trending_products}

        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
            }

    # api for getting a product details
    # params: product_id
    @http.route('/product/details', type='json', auth="public", methods=['POST'], csrf=False)
    def product_details(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                item = request.env['product.template'].sudo().search([('id', '=', data.get('product_id'))])
                items = request.env['res.users'].sudo().search(
                    [('id', '=', data.get('user_id'))]).partner_id.favourite_product_ids
                products = items.mapped('product_id').ids
                if data.get('product_id') in products:
                    fav_status = 1
                else:
                    fav_status = 0
                if item.image_1920:
                    product = { 'status': 1,
                                'name': item.name,
                                'description': item.description or item.name,
                                'rating': int(item.rating),
                                'fav_status':fav_status,
                                'sale price': item.list_price,
                                'image':url + "product/image/" + str(item.id) + "/.jpeg" or ''
                                }
                else:
                    demo_img = request.env['product.template'].sudo().search([], limit=1)
                    product = {'status': 1,
                               'name': item.name,
                               'description': item.description or item.name,
                               'rating': int(item.rating),
                               'fav_status': fav_status,
                               'sale price': item.list_price,
                               'image': url + "product/image/" + str(demo_img.id) + "/.jpeg"
                               }

                return product

        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]

    # api for adding deleting a product to favourite list
    @http.route('/favourite/product', type='json', auth="public", methods=['POST'], csrf=False)
    def favourite_product(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:

                url = request.httprequest.host_url
                partner_id = request.env['res.users'].sudo().search([('id', '=', data.get('user_id'))]).partner_id
                products = partner_id.favourite_product_ids
                products = products.mapped('product_id').ids

                if data.get('product_id') in products:
                    request.env['res.partner'].sudo().delete_fav_products(data.get('product_id'),partner_id.id)
                    fav_status = 0
                else:
                    request.env['res.partner'].sudo().add_fav_products(data.get('product_id'),partner_id.id)
                    fav_status = 1
                product = {'status': 1,
                           'fav_status':fav_status
                           }
                return product

        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]

    # api for trending products based on last week sales
    @http.route('/trending/products', type='json', auth="public", methods=['POST'], csrf=False)
    def trending_products(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                trending_products = []
                order = request.env['sale.order'].sudo().search([('date_order', '<', datetime.today()+relativedelta(days=7))])
                order_lines_ids = order.mapped('order_line').ids
                order_lines = request.env['sale.order.line'].sudo().browse(order_lines_ids)
                product_ids = order_lines.mapped('product_id').ids
                products = request.env['product.template'].sudo().browse(product_ids)
                products = products.sudo().search([('available_in_pos', '=', True)])
                for product in products:
                    if request.env['product.template'].sudo().search([('id', '=', product.id)]).name:
                        if product.image_1920:
                            image = url + "product/image/" + str(product.id) + "/.jpeg"
                            trending_products.append({'product_id': product.id,
                                                          'name': product.name,
                                                          'description': product.description or product.name,
                                                          'rating': int(product.rating),
                                                          'sale price': product.list_price,
                                                          'image': image})
                        else:
                            demo_img = request.env['product.template'].sudo().search([],limit=1)
                            trending_products.append({'product_id': product.id,
                                                      'name': product.name,
                                                      'description': product.description or product.name,
                                                      'rating': int(product.rating),
                                                      'sale price': product.list_price,
                                                      'image': url + "product/image/" + str(demo_img.id) + "/.jpeg"})
                    else:
                        pass

                return {'status': 1, 'products': trending_products}

        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]

    # point of sale categories which doesn't have a parent category
    @http.route('/parent/categories', type='json', auth="public", methods=['POST'], csrf=False)
    def parent_categories(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                categories_list = []
                categories = request.env['pos.category'].sudo().search([('parent_id', '=', None)])
                for category in categories:
                    child_categories_list = []
                    child_categories = request.env['pos.category'].sudo().search([('parent_id', '=', category.id)])
                    for child in child_categories:
                        child_categories_list.append({'category_id': child.id,
                                                'name': child.name})
                    categories_list.append({'parent_id': category.id,
                                            'name': category.name,
                                            'child_categories_list': child_categories_list})

                return {'status': 1, 'categories_list': categories_list}

        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]

    # chld cattegories of a specific parent category
    @http.route('/child/categories', type='json', auth="public", methods=['POST'], csrf=False)
    def child_categories(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                categories_list = []
                categories = request.env['pos.category'].sudo().search([('parent_id', '=', data.get('parent_id'))])
                for category in categories:
                    categories_list.append({'category_id': category.id,
                                            'name': category.name})
                return {'status': 1, 'categories_list': categories_list}

        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]

    @http.route('/category/product', type='json', auth="public", methods=['POST'], csrf=False)
    def category_product(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)

            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                products = []
                categ_products = request.env['product.template'].sudo().search([('pos_categ_id','=',data.get('category_id')),('available_in_pos','=',True)])
                for product in categ_products:
                    if request.env['product.template'].sudo().search([('id', '=', product.id)]).name:
                        if product.image_1920:
                            products.append({'product_id': product.id,
                                                       'name': product.name,
                                                       'description': product.description or product.name,
                                                       'rating': int(product.rating),
                                                       'sale price': product.list_price,
                                                       'image': url + "product/image/" + str(product.id) + "/.jpeg"})
                        else:
                            demo_img = request.env['product.template'].sudo().search([], limit=1)
                            products.append({'product_id': product.id,
                                             'name': product.name,
                                             'description': product.description or product.name,
                                             'rating': int(product.rating),
                                             'sale price': product.list_price,
                                             'image': url + "product/image/" + str(demo_img.id) + "/.jpeg"})
                    else:
                        pass
                return {'status': 1, 'products': products}

        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]

    # list of favourite products
    @http.route('/favourite/products', type='json', auth="public", methods=['POST'], csrf=False)
    def favourite_products(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)

            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                partner_id = request.env['res.users'].sudo().search([('id', '=', data.get('user_id'))]).partner_id
                products = partner_id.favourite_product_ids
                products = products.mapped('product_id').ids
                favourite_products = []
                products = request.env['product.template'].sudo().browse(products)
                # products = products.sudo().search([('available_in_pos', '=', True)])
                for product in products:
                    if request.env['product.template'].sudo().search([('id', '=', product.id)]).name:
                        if product.available_in_pos == True:
                            if product.image_1920:
                                favourite_products.append({'product_id': product.id,
                                                          'name': product.name,
                                                          'description': product.description or product.name,
                                                          'rating': int(product.rating),
                                                          'sale price': product.list_price,
                                                          'image': url + "product/image/" + str(product.id) + "/.jpeg"})
                            else:
                                demo_img = request.env['product.template'].sudo().search([], limit=1)
                                favourite_products.append({'product_id': product.id,
                                                           'name': product.name,
                                                           'description': product.description or product.name,
                                                           'rating': int(product.rating),
                                                           'sale price': product.list_price,
                                                           'image': url + "product/image/" + str(demo_img.id) + "/.jpeg"})
                    else:
                        pass
                return {'status': 1, 'products': favourite_products}

        except Exception as e:
                return [{
                    'status': 0,
                    'message': "The given user name or password is wrong"
                }]

    @http.route('/cart/products', type='json', auth="public", methods=['POST'], csrf=False)
    def cart_products(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                partner_id = request.env['res.users'].sudo().search([('id', '=', data.get('user_id'))]).partner_id
                sale_order = request.env['sale.order'].sudo().search([('partner_id', '=', partner_id.id),('state','=','draft')], limit=1, order="date_order desc, id desc")
                cart_products = []
                if data.get('products') and sale_order:
                    lines = []
                    products = data.get('products')
                    if type(products) is str:
                        products = json.loads(products)
                    for product in products:
                        product_tmpl_id = request.env['product.template'].sudo().search(
                            [('id', '=', int(product.get('product_id')))])
                        lines.append((0, 0, {'product_id': product_tmpl_id.product_variant_id.id,
                                             'product_uom_qty': product.get('quantity'),
                                             'price_unit': product_tmpl_id.list_price}))
                    sale_order = request.env['sale.order'].sudo().search([('id', '=', sale_order.id)])
                    po = sale_order.mapped('order_line.id')
                    for line in po:
                        sale_order.sudo().write({
                            'order_line': [(2, line)]})
                    sale_order.sudo().write({'order_line': lines})

                    return {'status': 1, 'sale_order_id': sale_order.id}

                elif data.get('products'):
                    lines = []
                    products = data.get('products')
                    if type(products) is str:
                        products = json.loads(products)
                    for product in products:
                        product_tmpl_id = request.env['product.template'].sudo().search(
                            [('id', '=', int(product.get('product_id')))])
                        lines.append((0, 0, {'product_id': product_tmpl_id.product_variant_id.id,
                                             'product_uom_qty': product.get('quantity'),
                                             'price_unit': product_tmpl_id.list_price}))
                    sale_order = request.env['sale.order'].sudo().create({
                        'partner_id': partner_id.id,
                        'order_line': lines,
                    })
                    return {'status': 1, 'cart_sale_order_id': sale_order.id }

                elif sale_order:
                    try:
                        if len(data.get('products'))==0:
                            if len(data.get('products'))==0:
                                products = data.get('products')
                                if type(products) is str:
                                    products = json.loads(products)
                                if len(products) == 0:
                                    sale_order.write({'state': 'cancel'})
                                    return {'status': 1, 'cart_sale_order_id': 0}
                    except:
                        pass
                    try:
                            for line in sale_order.order_line:
                                if request.env['product.template'].sudo().search(
                                        [('id', '=', line.product_id.product_tmpl_id.id)]).name:
                                    if line.product_id.product_tmpl_id.image_1920:
                                        cart_products.append({'product_id': line.product_id.product_tmpl_id.id,
                                                              'name': line.product_id.name,
                                                              'product_qty': int(line.product_uom_qty),
                                                              'sale price': line.product_id.list_price,
                                                              'image': url + "product/image/" + str(
                                                                  line.product_id.product_tmpl_id.id) + "/.jpeg"})
                                    else:
                                        sale_order.write({'state': 'cancel'})
                                        return {'status': 1, 'cart_sale_order_id': 0}
                                        demo_img = request.env['product.template'].sudo().search([], limit=1)
                                        cart_products.append({'product_id': line.product_id.product_tmpl_id.id,
                                                              'name': line.product_id.name,
                                                              'product_qty': int(line.product_uom_qty),
                                                              'sale price': line.product_id.list_price,
                                                              'image': url + "product/image/" + str(
                                                                  demo_img.id) + "/.jpeg"})
                            return {'status': 1, 'cart_sale_order_id': sale_order.id, 'products': cart_products}

                    except:
                        pass

                    return {'status': 1, 'cart_sale_order_id': 0, 'products': cart_products}

                else:
                    return {'status': 1, 'cart_sale_order_id': 0, 'products': cart_products}


        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]


    @http.route('/create/order', type='json', auth="public", methods=['POST'], csrf=False)
    def create_order(self):
        # param: db, email, password, products:{product_id,quantity,price}
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                partner_id = request.env['res.users'].sudo().search([('id','=',data.get('user_id'))]).partner_id.id
                if data.get('update_sale_order') == 0 or None:
                    lines = []
                    products = data.get('products')
                    if type(products) is str:
                        products = json.loads(products)
                    for product in products:
                        product_tmpl_id = request.env['product.template'].sudo().search(
                            [('id', '=', int(product.get('product_id')))])
                        lines.append((0, 0, {'product_id': product_tmpl_id.product_variant_id.id,
                                             'product_uom_qty': product.get('quantity'),
                                             'price_unit': product_tmpl_id.list_price}))
                    sale_order = request.env['sale.order'].sudo().create({
                        'partner_id': partner_id,
                        'order_line': lines,
                    })
                else:
                    lines = []
                    products = data.get('products')
                    if type(products) is str:
                        products = json.loads(products)
                    for product in products:
                        product_tmpl_id = request.env['product.template'].sudo().search(
                            [('id', '=', int(product.get('product_id')))])
                        lines.append((0, 0, {'product_id': product_tmpl_id.product_variant_id.id,
                                             'product_uom_qty': product.get('quantity'),
                                             'price_unit': product_tmpl_id.list_price}))
                    sale_order = request.env['sale.order'].sudo().search([('id','=',data.get('update_sale_order'))])
                    po = sale_order.mapped('order_line.id')
                    for line in po:
                        sale_order.sudo().write({
                            'order_line': [(2,line)]})
                    sale_order.sudo().write({'order_line':lines})
                cod_option = request.env['ir.config_parameter'].sudo().search([('key','=','umami_mobile.cod_available')])
                if cod_option.value == 'on':
                    cod_option = 1
                else:
                    cod_option = 0

                return {'status': 1,
                        'cod_option': cod_option,
                        'sale_order_id': sale_order.id}

        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]

    @http.route('/order/name', type='json', auth="public", methods=['POST'], csrf=False)
    def sale_order_name(self):
        # param: db, email, password, products:{product_id,quantity,price}
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                order = request.env['sale.order'].sudo().search([('id', '=', data.get('order_id'))])

                return {'status': 1,
                        'order_name': order.name
                        }

        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]

    @http.route('/order/details', type='json', auth="public", methods=['POST'], csrf=False)
    def sale_order_details(self):
        # param: db, email, password, products:{product_id,quantity,price}
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                products = []
                order = request.env['sale.order'].sudo().search([('id', '=', data.get('order_id'))])
                for line in order.order_line:
                    products.append({'product_id': line.product_id.product_tmpl_id.id,
                                     'name': line.product_id.product_tmpl_id.name,
                                     'product_qty': int(line.product_uom_qty),
                                     'details': line.product_id.product_tmpl_id.description or line.product_id.product_tmpl_id.name,
                                     'price': line.product_id.product_tmpl_id.list_price,
                                     'image': url + "product/image/" + str(line.product_id.product_tmpl_id.id) + "/.jpeg" or ''})
                return {'status': 1,
                        'order_id': order.id,
                        'order_name': order.name,
                        'date_order': order.date_order,
                        'tax_total': order.amount_tax,
                        'delivery_status': order.delivery_status,
                        'delivery_price': 0.0,
                        'amount_total': order.amount_total,
                        'amount_untaxed': order.amount_untaxed,
                        'products': products
                        }

        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]


    @http.route(['/customer/form/<string:order_id>'], type='http', auth="public", website=True)
    def partner_form(self, order_id,**kwargs):
        order_id = order_id
        if order_id != '':
            return request.render("umami_mobile.tmp_customer_form", {"order_id":order_id})
        else:
            return {"status": "faild", "description": "please provide order id of the order"}

    @http.route(['/customer/success'], type='http', auth="public", website=True)
    def success(self, **kwargs):
        return request.render("umami_mobile.return_message_success")

    @http.route(['/customer/paymentfailed'], type='http', auth="public", website=True)
    def paymentfailed(self, **kwargs):
        return request.render("umami_mobile.return_message_failed")

    @http.route(['/customer/form/submit'], type='http', auth="public", website=True)
    # next controller with url for submitting data from the form#
    def customer_form_submit(self, **post):
        try:
            stripe.api_key = "sk_test_51HOGVxDJiZWXANqt3OkN6p6KBKS1rF43mGlDz6cUamLpwFsiHNd31gImbfKY8WNiqjiHQp7pvQj5wVwXi0LZSy6900UuvGr697"
            sale_order_id = request.env['sale.order'].sudo().search([('id', '=', int(post.get('order_id')))])
            customer_id = stripe.Customer.create(
                name=sale_order_id.partner_id.name,
                address={
                    'line1': sale_order_id.partner_id.street or '',
                    'postal_code': sale_order_id.partner_id.zip or '',
                    'city': sale_order_id.partner_id.city or '',
                    'state': sale_order_id.partner_id.state_id.name,
                    'country': sale_order_id.partner_id.country_id.code or "US",
                },
            )
            _logger.info("customer")
            _logger.info(customer_id)

            payment_intent = stripe.PaymentIntent.create(
                amount=round(sale_order_id.amount_total),
                currency="usd",
                payment_method_types=['card'],
                description="demo",
                customer=customer_id.get('id')
            )

            _logger.info("payment_intent")
            _logger.info(payment_intent)

            payment_method = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": post.get('card_number'),
                    "exp_month": post.get('exp_month'),
                    "exp_year": post.get('exp_year'),
                    "cvc": post.get('cvv'),
                },
            )
            _logger.info("payment_method")
            _logger.info(payment_method)

            payment_method_obj = stripe.PaymentMethod.retrieve(
                payment_method.get('id')
            )

            _logger.info("payment_method_obj")
            _logger.info(payment_method_obj)

            stripe.PaymentMethod.attach(
                payment_method_obj.get('id'),
                customer=customer_id.get('id'),
            )

            stripe.PaymentMethod.modify(
                payment_method_obj.get('id'),
                metadata={"order_id": str(sale_order_id.id)},
            )

            response = stripe.PaymentIntent.modify(
                payment_intent.get('id'),
                metadata={"order_id": str(sale_order_id.id)},
            )

            confirm_payment = stripe.PaymentIntent.confirm(
                payment_intent.get('id'),
                payment_method=payment_method.get('id'),
            )

            sale_order_id.sudo().action_confirm()
            stock_picking = request.env['stock.picking'].sudo().search([('origin', '=', sale_order_id.name)])
            for line in stock_picking.move_ids_without_package:
                line.write({'quantity_done': line.product_uom_qty})
            stock_picking.button_validate()
            adv_wiz = request.env['sale.advance.payment.inv'].sudo().with_context(
                active_ids=[sale_order_id.id]).create({
                'advance_payment_method': 'delivered',
            })
            adv_wiz.with_context(open_invoices=True).sudo().create_invoices()
            confirm_invoices = request.env['account.move'].sudo().search(
                [('invoice_origin', '=', sale_order_id.name)])
            invoice_post = confirm_invoices.sudo().action_post()
            journal_id = request.env['account.journal'].sudo().search([('name', '=', "Stripe")])
            payment_method_id = request.env['account.payment.method'].sudo().search([('name', '=', "Manual")],
                                                                                    limit=1)
            register_payments = request.env['account.payment.register'].sudo().with_context(
                active_model='account.move',
                active_ids=confirm_invoices.id).create(
                {
                    'journal_id': journal_id.id,
                    'payment_date': confirm_invoices.invoice_date,
                    'payment_method_id': payment_method_id.id,
                    'amount': confirm_invoices.amount_total
                })

            register_payments._create_payments()
            url = request.httprequest.host_url
            url = url + "customer/success"
            return werkzeug.utils.redirect(url)

        except Exception as e:
            url = request.httprequest.host_url
            url = url + "customer/paymentfailed"
            return werkzeug.utils.redirect(url)


    @http.route('/order/payment', type='json', auth="public", methods=['POST'], csrf=False)
    def create_payment(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                sale_order_id = request.env['sale.order'].sudo().search([('id', '=', data.get('sale_order_id'))])
                if data.get('cod_option') == 1:
                    sale_order_id.sudo().write({'payment_method':'cod'})
                    sale_order_id.sudo().action_confirm()
                    return {'status': 1,
                            'sale_order_id': sale_order_id.id}
                if data.get('cod_option') == 0:
                    sale_order_id.sudo().write({'payment_method': 'stripe'})
                    url = request.httprequest.host_url
                    url = url+"customer/form/<string:order_id>"
                    return {'status': 1,
                            'response': url}

        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]


    @http.route('/user/image/<string:id>/.jpeg', type='http', auth="none")
    def user_image(self, id, **kwargs):
        try:
            attachment_ids = request.env['res.users'].sudo().search([('id', '=', id)])
            if attachment_ids:
                for attachment_obj in attachment_ids:
                    filecontent = base64.b64decode(attachment_obj.image_1920)
                    disposition = 'attachment; filename=%s' % werkzeug.urls.url_quote(attachment_obj.name)
                    return request.make_response(
                        filecontent,
                        [('Content-Type', 'image/jpeg')
                         ])
            else:
                error = {
                    'code': 200,
                    'message': "Unable to find the attachments",
                }
            return request.make_response(html_escape(json.dumps(error)))

        except Exception as e:
            error = {
                'code': 200,
                'message': "Odoo Server Error",
            }
            return request.make_response(html_escape(json.dumps(error)))

    @http.route('/product/image/<string:id>/.jpeg', type='http', auth="none")
    def product_image(self, id, **kwargs):
        try:
            attachment_ids = request.env['product.template'].sudo().search([('id', '=', id)])
            print(attachment_ids)
            if attachment_ids:
                for attachment_obj in attachment_ids:
                    filecontent = base64.b64decode(attachment_obj.image_1920)
                    disposition = 'attachment; filename=%s' % werkzeug.urls.url_quote(attachment_obj.name)
                    return request.make_response(
                        filecontent,
                        [('Content-Type', 'image/jpeg')
                         ])
            else:
                error = {
                    'code': 200,
                    'message': "Unable to find the attachments",
                }
            return request.make_response(html_escape(json.dumps(error)))

        except Exception as e:
            error = {
                'code': 200,
                'message': "Odoo Server Error",
            }
            return request.make_response(html_escape(json.dumps(error)))

    @http.route('/user/profile', type='json', auth="public", methods=['POST'], csrf=False)
    def user_profile(self):
        # param: db, email, password
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                if user.image_1920:
                    return_data = {
                        'status': 1,
                        'uid': data.get('user_id'),
                        'image_url': url + "user/image/" + str(data.get('user_id')) + "/.jpeg",
                        'name': user.name,
                        'gender':user.partner_id.gender or '',
                        'email': user.partner_id.email or '',
                        'phone': user.partner_id.phone or '',
                        'street': user.partner_id.street or '',
                        'street2': user.partner_id.street2 or '',
                        'city': user.partner_id.city or '',
                        'zip': user.partner_id.zip or '',
                        'country': user.partner_id.country_id.name if user.partner_id.country_id else '',
                        'state': user.partner_id.state_id.name if user.partner_id.state_id else '',
                        'country_id': user.partner_id.country_id.id if user.partner_id.country_id else 0,
                        'state_id': user.partner_id.state_id.id if user.partner_id.state_id else 0,
                        'mobile': user.partner_id.mobile or '',
                        'latitude': user.partner_id.latitude or '',
                        'longitude': user.partner_id.longitude or '',
                    }
                else:
                    demo_user_image = request.env['res.users'].sudo().search([('name','=',"Default User Template")],limit=1)
                    return_data = {
                        'status': 1,
                        'uid': data.get('user_id'),
                        'image_url': url + "user/image/" + str(demo_user_image.id) + "/.jpeg",
                        'name': user.name,
                        'gender': user.partner_id.gender or '',
                        'email': user.partner_id.email or '',
                        'phone': user.partner_id.phone or '',
                        'street': user.partner_id.street or '',
                        'street2': user.partner_id.street2 or '',
                        'city': user.partner_id.city or '',
                        'zip': user.partner_id.zip or '',
                        'country': user.partner_id.country_id.name if user.partner_id.country_id else '',
                        'state': user.partner_id.state_id.name if user.partner_id.state_id else '',
                        'country_id': user.partner_id.country_id.id if user.partner_id.country_id else 0,
                        'state_id': user.partner_id.state_id.id if user.partner_id.state_id else 0,
                        'mobile': user.partner_id.mobile or '',
                        'latitude': user.partner_id.latitude or '',
                        'longitude': user.partner_id.longitude or '',
                    }


                return return_data


        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]



    @http.route('/user/edit', type='json', auth="public", methods=['POST'], csrf=False)
    def user_edit(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                partner_id = request.env['res.users'].sudo().search([('id','=',data.get('user_id'))]).partner_id
                if data.get('state'):
                    state = request.env['res.country.state'].sudo().search([('id','=',data.get('state'))])
                    partner_id.update({'state_id': state.id})
                if data.get('country'):
                    country = request.env['res.country'].sudo().search([('id','=',data.get('country'))])
                    partner_id.update({'country_id': country.id or user.partner_id.country_id})
                if data.get('gender'):
                    if data.get('gender') == "male":
                        gender = 'male'
                    if data.get('gender') == "female":
                        gender = 'female'
                    if data.get('gender') == "other":
                        gender = 'other'
                    partner_id.update({'gender': gender})

                partner_id.update({'name': str(data.get('name')),
                                   'email': str(data.get('email')) or user.partner_id.email,
                                   'phone': str(data.get('phone')) or user.partner_id.phone,
                                   'street': str(data.get('street')) or user.partner_id.street,
                                   'street2': str(data.get('street2')) or user.partner_id.street2,
                                   'city': str(data.get('city')) or user.partner_id.city,
                                   'zip': str(data.get('zip')) or user.partner_id.zip,
                                   'mobile': data.get('mobile') or user.partner_id.mobile or '',
                                   'latitude': data.get('latitude') or user.partner_id.latitude or '',
                                   'longitude': data.get('longitude') or user.partner_id.longitude or ''
                                   })

                return {'status': 1}


        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]


    @http.route('/product/search', type='json', auth="public", methods=['POST'], csrf=False)
    def search_products(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                searched_products = []
                products = request.env['product.template'].sudo().search([('name', 'ilike',data.get('product_name'))])
                for product in products:
                    if product.image_1920:
                        searched_products.append({'product_id': product.id,
                                                  'name': product.name,
                                                  'description': product.description or product.name,
                                                  'rating': int(product.rating),
                                                  'sale price': product.list_price,
                                                  'image': url + "product/image/" + str(product.id) + "/.jpeg"})
                    else:
                        demo_img = request.env['product.template'].sudo().search([], limit=1)
                        searched_products.append({'product_id': product.id,
                                                  'name': product.name,
                                                  'description': product.description or product.name,
                                                  'rating': int(product.rating),
                                                  'sale price': product.list_price,
                                                  'image': url + "product/image/" + str(demo_img.id) + "/.jpeg"})

                return {'status': 1, 'products': searched_products}

        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]

    @http.route('/country/list', type='json', auth="public", methods=['POST'], csrf=False)
    def country_list(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                country_list = []
                countries = request.env['res.country'].sudo().search([])
                for country in countries:
                        country_list.append({'country_id': country.id,
                                                  'name': country.name,
                                                  'code': country.code})

                return {'status': 1, 'response': country_list}

        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]

    @http.route('/states/list', type='json', auth="public", methods=['POST'], csrf=False)
    def states_list(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                states_list = []
                states = request.env['res.country.state'].sudo().search([('country_id', '=', data.get('country_id'))])
                for state in states:
                    states_list.append({'state_id': state.id,
                                        'name': state.name,
                                        'code': state.code,
                                        })

                return {'status': 1, 'response': states_list}

        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]

    @http.route('/user/orders', type='json', auth="public", methods=['POST'], csrf=False)
    def user_orders(self):
        # param: db, email, password
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                partner_id = request.env['res.users'].sudo().search([('id', '=', data.get('user_id'))]).partner_id
                user_so = []
                sale_orders = request.env['sale.order'].sudo().search([('partner_id', '=',partner_id.id)])
                for so in sale_orders:
                    user_so.append({'order_id': so.id,
                                    'name': so.name,
                                    'delivery_status': so.delivery_status,
                                    'date_order': so.date_order,
                                    'amount_total': so.amount_total
                                    })
                return {'status': 1, 'response': user_so}



        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]