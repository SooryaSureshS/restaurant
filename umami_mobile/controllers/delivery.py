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


_logger = logging.getLogger(__name__)


dataggl = {}
try:
    import Image
    import pycountry

except ImportError:
    from PIL import Image

def get_db_name():
    db = odoo.tools.config['db_name']
    if not db and hasattr(threading.current_thread(), 'dbname'):
        return threading.current_thread().dbname
    return db


class employeelogin(http.Controller):

    @http.route('/employee/register', type='json', auth="public", methods=['POST'], csrf=False)
    def employee_register(self):
        # param: username, email, password, confirm ,
        try:
            data = request.httprequest.data
            data = json.loads(data)
            if data.get('name') and data.get('email'):
                if request.env['hr.employee'].sudo().search([('work_email', '=', data.get('email'))]):
                    return {
                        'status': 0,
                        'message': "The given email is already registered as employee"
                    }

                else:
                    employee = request.env['hr.employee'].sudo().create({'company_id': request.env.company.id,
                                                                         'name': data.get('name'),
                                                                         'work_email': data.get('email'),
                                                                         })
                    partner = request.env['res.partner'].sudo().create({'name': data.get('name'),
                                                                        'email': data.get('email'),
                                                                        })
                    group_user = request.env.ref('base.group_user')
                    user = request.env['res.users'].sudo().create({
                        'company_id': request.env.company.id,
                        'email': data.get('email'),
                        'name': data.get('name'),
                        'login': data.get('email'),
                        'partner_id': partner.id,
                        'new_password': data.get('password'),
                        'groups_id': [(6, 0, [group_user.id])],
                        'totp_enabled': True
                    })

                    print("user", user)

                    employee.write({'user_id':user.id})
                    if user:
                        print ("change password")
                        user.write({'password': data.get('password'), 'new_password': data.get('password')})

                    return {'status': 1,
                            'user_id': user.id}

        except Exception as e:
            return {
                'status': 0,
                'message': "Please enter the valid data"
            }


    @http.route('/employee/login', type='json', auth="public", methods=['POST'], csrf=False)
    def employee_authenticate(self):
        # param: db, email, password
        try:
            data = request.httprequest.data
            data = json.loads(data)
            db = get_db_name()
            uid = request.session.authenticate(db, data.get('username', False),
                                               data.get('password', False))

            employee_details = {'status':1,
                                'user_id': uid
                                    }

            return employee_details

        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
                    }

    @http.route('/employee/homepage/new', type='json', auth="public", methods=['POST'], csrf=False)
    def employee_homepage_new(self):
        # param: db, email, password
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                sale_orders = request.env['sale.order'].sudo().search([('delivery_status', '=', 'new')])
                new_orders = []
                for order in sale_orders:
                    new_orders.append({'sale_order_id': order.id,
                                       'name': order.name,
                                       'date_order': order.date_order,
                                       'amount_total': order.amount_total,
                                        })

                return {'status': 1, 'new_orders': new_orders}

        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
            }

    @http.route('/employee/homepage/active', type='json', auth="public", methods=['POST'], csrf=False)
    def employee_homepage_active(self):
        # param: db, email, password
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                sale_orders = request.env['sale.order'].sudo().search([('delivery_status', '=', 'active'),('date_order', '<', datetime.today() + relativedelta(days=1))])
                new_orders = []
                for order in sale_orders:
                    new_orders.append({'sale_order_id': order.id,
                                       'name': order.name,
                                       'date_order': order.date_order,
                                       'amount_total': order.amount_total,
                                       })

                return {'status': 1, 'new_orders': new_orders}

        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
            }

    @http.route('/employee/homepage/history', type='json', auth="public", methods=['POST'], csrf=False)
    def employee_homepage_history(self):
        # param: db, email, password
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                url = request.httprequest.host_url
                sale_orders = request.env['sale.order'].sudo().search([('delivery_status', '=', 'history'),('date_order', '<', datetime.today() + relativedelta(days=1))])
                new_orders = []
                for order in sale_orders:
                    new_orders.append({'sale_order_id': order.id,
                                       'name': order.name,
                                       'date_order': order.date_order,
                                       'amount_total': order.amount_total,
                                       })

                return {'status': 1, 'new_orders': new_orders}

        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
            }

    @http.route('/order/details', type='json', auth="public", methods=['POST'], csrf=False)
    def create_order(self):
        # param: db, email, password, products:{product_id,quantity,price}
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                sale_order = request.env['sale.order'].sudo().search([('id', '=', data.get('sale_order_id'))])
                lines = []
                order = {'sale_order_id':sale_order.id,
                         'name':sale_order.name,
                         'date_order': sale_order.date_order,
                         'amount_total': sale_order.amount_total,
                         'customer_id':sale_order.partner_id.id,
                         'customer_name':sale_order.partner_id.name,
                         'customer_phone':sale_order.partner_id.phone,

                         }
                for line in sale_order.order_line:

                    products = data.get('products')
                    if type(products) is str:
                        products = json.loads(products)

                    for product in products:
                        product_tmpl_id = request.env['product.template'].sudo().search(
                            [('id', '=', int(product.get('product_id')))])
                        lines.append((0, 0, {'product_id': product.get('product_id'),
                                             'product_uom_qty': product.get('quantity'),
                                             'price_unit': product_tmpl_id.list_price}))
                    sale_order = request.env['sale.order'].sudo().create({
                        'partner_id': partner_id,
                        # 'l10n_in_gst_treatment':'consumer',
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
                        lines.append((0, 0, {'product_id': product.get('product_id'),
                                             'product_uom_qty': product.get('quantity'),
                                             'price_unit': product_tmpl_id.list_price}))
                    sale_order = request.env['sale.order'].sudo().search([('id', '=', data.get('update_sale_order'))])
                    po = sale_order.mapped('order_line.id')
                    for line in po:
                        sale_order.sudo().write({
                            'order_line': [(2, line)]})
                    sale_order.sudo().write({'order_line': lines})

                return {'status': 1,
                        'sale_order_id': sale_order.id}


        except Exception as e:
            return [{
                'status': 0,
                'message': "The given user name or password is wrong"
            }]

