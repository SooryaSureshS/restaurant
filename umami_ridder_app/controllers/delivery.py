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
from datetime import timedelta
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
            if uid:
                user = request.env['res.users'].sudo().browse([uid])
                if user.partner_id.is_rider:
                    employee_details = {'status': 1,
                                        'user_id': uid
                                        }

                    return employee_details
                else:
                    employee_details = {'status': 2,
                                        'message': "The given user name or password is wrong or he is not rider"
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
                import datetime
                TIMEOUT = 50
                utc_now_start = datetime.datetime.utcnow() - datetime.timedelta(seconds=TIMEOUT * 2) - relativedelta(
                    hours=15)
                utc_now = datetime.datetime.utcnow() - datetime.timedelta(seconds=TIMEOUT * 2) + relativedelta(hours=5)
                sale_orders = request.env['sale.order'].sudo().search([
                    ('state', '=', 'sale'), ('delivery_status', '=', 'new'),('website_delivery_type','=','delivery'), ('delivery_boy', '=', False),
                    ('date_order', '>=', utc_now_start),
                    ('date_order', '<=', utc_now)])
                new_orders = []

                for order in sale_orders:
                    order_line = []
                    status = ''
                    waiting = 0
                    delivery = 0
                    ready = 0
                    done = 0
                    count = 0
                    is_delivery_address = order.order_line.search(
                        [('is_delivery', '=', True), ('order_id', '=', order.id)])
                    for line in order.order_line:
                        order_len = len(order.order_line) - len(is_delivery_address)
                        count += 1
                        if line.order_line_state == 'done' and line.is_delivery == False:
                            done += 1
                        if line.order_line_state == 'waiting' and line.is_delivery == False:
                            waiting += 1
                        if line.order_line_state == 'delivering' and line.is_delivery == False:
                            delivery += 1
                        if line.order_line_state == 'preparing' and line.is_delivery == False:
                            status = 'Preparing'
                        if line.order_line_state == 'ready' and line.is_delivery == False:
                            ready += 1;
                        if waiting == order_len:
                            status = 'Waiting'
                        if ready == order_len:
                            status = 'Ready'
                        if delivery == order_len:
                            status = 'On the Way'
                        if done == order_len:
                            status = 'Received'
                        taxs = []
                        # print("999: ", order.date_order)
                        for tax in line.tax_id:
                            taxs.append({
                                'tax_id': tax.id,
                                'tax_name': tax.name
                            })
                        order_line.append({
                            'product_id': line.product_id.id or False,
                            'product_name': line.product_id.name or False,
                            'description': line.name or False,
                            'product_uom_qty': line.product_uom_qty or False,
                            'price_unit': line.price_unit or False,
                            'tax': taxs,
                            'product_image': url + 'web/image?model=product.product&field=image_1920&id=' + str(
                                line.product_id.id),
                        })

                    order_date = order.date_order + timedelta(hours=5, minutes=30)
                    delivery_rejected = False
                    for delivery_boy in order.rejected_order_ids:
                        if user.partner_id.id == delivery_boy.delivery_boy.id:
                            delivery_rejected = True
                    if delivery_rejected == False:
                        new_orders.append({'sale_order_id': order.id,
                                           'name': order.name,
                                           'date_order': order_date,
                                           'amount_total': order.amount_total,
                                           'status': status,
                                           'order_line': order_line,
                                           'delivery_address': {
                                               'name': order.partner_shipping_id.name or False,
                                               'street': order.partner_shipping_id.street or False,
                                               'street2': order.partner_shipping_id.street2 or False,
                                               'city': order.partner_shipping_id.city or False,
                                               'state': order.partner_shipping_id.state_id.name or False,
                                               'zip': order.partner_shipping_id.zip or False,
                                               'country': order.partner_shipping_id.country_id.name or False,
                                               'phone': order.partner_shipping_id.phone or False,
                                               'latitude': order.partner_shipping_id.latitude or False,
                                               'longitude': order.partner_shipping_id.longitude or False,
                                           },
                                           'latitude': order.latitude or False,
                                           'longitude': order.longitude or False,
                                           'amount_untaxed': order.amount_untaxed,
                                           'amount_tax': order.amount_tax,
                                           'partner_name': order.partner_shipping_id.name or False,
                                           'street': order.partner_shipping_id.street or False,
                                           'street2': order.partner_shipping_id.street2 or False,
                                           'city': order.partner_shipping_id.city or False,
                                           'state': order.partner_shipping_id.state_id.name or False,
                                           'zip': order.partner_shipping_id.zip or False,
                                           'country': order.partner_shipping_id.country_id.name or False,
                                           'phone': order.partner_shipping_id.phone or False,
                                           'cod': order.payment_method or False,
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
                import datetime
                TIMEOUT = 50
                utc_now_start = datetime.datetime.utcnow() - datetime.timedelta(seconds=TIMEOUT * 2) - relativedelta(
                    hours=15)
                utc_now = datetime.datetime.utcnow() - datetime.timedelta(seconds=TIMEOUT * 2) + relativedelta(hours=5)
                # sale_orders = request.env['sale.order'].sudo().search([('delivery_status', '=', 'active'),('delivery_boy','=',user.partner_id.id),('date_order', '>=', datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')),('date_order', '<=',datetime.datetime.now().strftime('%Y-%m-%d 23:23:59'))])
                sale_orders = request.env['sale.order'].sudo().search(
                    [('delivery_status', '=', 'active'), ('delivery_boy', '=', user.partner_id.id),
                     ('date_order', '>=', utc_now_start), ('date_order', '<=', utc_now)])
                new_orders = []
                for order in sale_orders:
                    order_line = []
                    status = '';
                    waiting = 0;
                    delivery = 0;
                    ready = 0;
                    done = 0;
                    count = 0;
                    is_delivery_address = order.order_line.search(
                        [('is_delivery', '=', True), ('order_id', '=', order.id)])
                    for line in order.order_line:
                        order_len = len(order.order_line) - len(is_delivery_address)
                        count += 1;
                        if line.order_line_state == 'done' and line.is_delivery == False:
                            done += 1;
                        if line.order_line_state == 'waiting' and line.is_delivery == False:
                            waiting += 1;
                        if line.order_line_state == 'delivering' and line.is_delivery == False:
                            delivery += 1;
                        if line.order_line_state == 'preparing' and line.is_delivery == False:
                            status = 'Preparing'
                        if line.order_line_state == 'ready' and line.is_delivery == False:
                            ready += 1;
                        if waiting == order_len:
                            status = 'Waiting'
                        if ready == order_len:
                            status = 'Ready'
                        if delivery == order_len:
                            status = 'On the Way'
                        if done == order_len:
                            status = 'Received'
                        taxs = []
                        for tax in line.tax_id:
                            taxs.append({
                                'tax_id': tax.id,
                                'tax_name': tax.name
                            })
                        order_line.append({
                            'product_id': line.product_id.id or False,
                            'product_name': line.product_id.name or False,
                            'description': line.name or False,
                            'product_uom_qty': line.product_uom_qty or False,
                            'price_unit': line.price_unit or False,
                            'tax': taxs,
                            'product_image': url + 'web/image?model=product.product&field=image_1920&id=' + str(
                                line.product_id.id),
                        })
                    order_date = order.date_order + timedelta(hours=5, minutes=30)
                    delivery_rejected = False
                    for delivery_boy in order.rejected_order_ids:
                        if user.partner_id.id == delivery_boy.delivery_boy.id:
                            delivery_rejected = True
                    if delivery_rejected == False:
                        new_orders.append({'sale_order_id': order.id,
                                           'name': order.name,
                                           'date_order': order_date,
                                           'amount_total': order.amount_total,
                                           'status': status,
                                           'order_line': order_line,
                                           'delivery_address': {
                                               'name': order.partner_shipping_id.name or False,
                                               'street': order.partner_shipping_id.street or False,
                                               'street2': order.partner_shipping_id.street2 or False,
                                               'city': order.partner_shipping_id.city or False,
                                               'state': order.partner_shipping_id.state_id.name or False,
                                               'zip': order.partner_shipping_id.zip or False,
                                               'country': order.partner_shipping_id.country_id.name or False,
                                               'phone': order.partner_shipping_id.phone or False,
                                               'latitude': order.partner_shipping_id.latitude or False,
                                               'longitude': order.partner_shipping_id.longitude or False,
                                           },
                                           'latitude': order.latitude or False,
                                           'longitude': order.longitude or False,
                                           'amount_untaxed': order.amount_untaxed,
                                           'amount_tax': order.amount_tax,
                                           'partner_name': order.partner_shipping_id.name or False,
                                           'street': order.partner_shipping_id.street or False,
                                           'street2': order.partner_shipping_id.street2 or False,
                                           'city': order.partner_shipping_id.city or False,
                                           'state': order.partner_shipping_id.state_id.name or False,
                                           'zip': order.partner_shipping_id.zip or False,
                                           'country': order.partner_shipping_id.country_id.name or False,
                                           'phone': order.partner_shipping_id.phone or False,
                                           'cod': order.payment_method or False,
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
                import datetime
                TIMEOUT = 50
                utc_now_start = datetime.datetime.utcnow() - datetime.timedelta(seconds=TIMEOUT * 2) - relativedelta(
                    hours=15)
                utc_now = datetime.datetime.utcnow() - datetime.timedelta(seconds=TIMEOUT * 2) + relativedelta(hours=5)
                # sale_orders = request.env['sale.order'].sudo().search([('delivery_status', '=', 'history'),
                # ('delivery_boy','=',user.partner_id.id),
                # ('date_order', '>=', datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')),('date_order', '<=',datetime.datetime.now().strftime('%Y-%m-%d 23:23:59'))])
                sale_orders = request.env['sale.order'].sudo().search([('delivery_status', '=', 'history'),
                                                                       ('delivery_boy', '=', user.partner_id.id)])
                new_orders = []
                for order in sale_orders:
                    order_line = []
                    status = '';
                    waiting = 0;
                    ready = 0;
                    delivery = 0;
                    done = 0;
                    count = 0;
                    is_delivery_address = order.order_line.search(
                        [('is_delivery', '=', True), ('order_id', '=', order.id)])
                    for line in order.order_line:
                        order_len = len(order.order_line) - len(is_delivery_address)
                        count += 1;
                        if line.order_line_state == 'done' and line.is_delivery == False:
                            done += 1;
                        if line.order_line_state == 'waiting' and line.is_delivery == False:
                            waiting += 1;
                        if line.order_line_state == 'delivering' and line.is_delivery == False:
                            delivery += 1;
                        if line.order_line_state == 'preparing' and line.is_delivery == False:
                            status = 'Preparing'
                        if line.order_line_state == 'ready' and line.is_delivery == False:
                            ready += 1;
                        if waiting == order_len:
                            status = 'Waiting'
                        if ready == order_len:
                            status = 'Ready'
                        if delivery == order_len:
                            status = 'On the Way'
                        if done == order_len:
                            status = 'Received'
                        taxs = []
                        for tax in line.tax_id:
                            taxs.append({
                                'tax_id': tax.id,
                                'tax_name': tax.name
                            })
                        order_line.append({
                            'product_id': line.product_id.id or False,
                            'product_name': line.product_id.name or False,
                            'description': line.name or False,
                            'product_uom_qty': line.product_uom_qty or False,
                            'price_unit': line.price_unit or False,
                            'tax': taxs,
                            'product_image': url + 'web/image?model=product.product&field=image_1920&id=' + str(
                                line.product_id.id),
                        })
                    order_date = order.date_order + timedelta(hours=5, minutes=30)
                    delivery_rejected = False
                    for delivery_boy in order.rejected_order_ids:
                        if user.partner_id.id == delivery_boy.delivery_boy.id:
                            delivery_rejected = True
                    if delivery_rejected == False:
                        new_orders.append({'sale_order_id': order.id,
                                           'name': order.name,
                                           'date_order': order_date,
                                           'amount_total': order.amount_total,
                                           'status': status,
                                           'order_line': order_line,
                                           'delivery_address': {
                                               'name': order.partner_shipping_id.name or False,
                                               'street': order.partner_shipping_id.street or False,
                                               'street2': order.partner_shipping_id.street2 or False,
                                               'city': order.partner_shipping_id.city or False,
                                               'state': order.partner_shipping_id.state_id.name or False,
                                               'zip': order.partner_shipping_id.zip or False,
                                               'country': order.partner_shipping_id.country_id.name or False,
                                               'phone': order.partner_shipping_id.phone or False,
                                               'latitude': order.partner_shipping_id.latitude or False,
                                               'longitude': order.partner_shipping_id.longitude or False,
                                           },
                                           'latitude': order.latitude or False,
                                           'longitude': order.longitude or False,
                                           'amount_untaxed': order.amount_untaxed,
                                           'amount_tax': order.amount_tax,
                                           'partner_name': order.partner_shipping_id.name or False,
                                           'street': order.partner_shipping_id.street or False,
                                           'street2': order.partner_shipping_id.street2 or False,
                                           'city': order.partner_shipping_id.city or False,
                                           'state': order.partner_shipping_id.state_id.name or False,
                                           'zip': order.partner_shipping_id.zip or False,
                                           'country': order.partner_shipping_id.country_id.name or False,
                                           'phone': order.partner_shipping_id.phone or False,
                                           'cod': order.payment_method or False,
                                           })

                return {'status': 1, 'new_orders': new_orders}

        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
            }

    @http.route('/employee/sale/order', type='json', auth="public", methods=['POST'], csrf=False)
    def employee_sale_order(self):
        # param: db, email, password
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            order_id = data.get('order_id', False)
            if user and order_id:
                url = request.httprequest.host_url
                sale_orders = request.env['sale.order'].sudo().search([('name', '=', order_id)])
                new_orders = []
                for order in sale_orders:
                    order_line = []
                    status = '';
                    waiting = 0;
                    delivery = 0;
                    ready = 0;
                    done = 0;
                    count = 0;
                    is_delivery_address = order.order_line.search(
                        [('is_delivery', '=', True), ('order_id', '=', order.id)])
                    for line in order.order_line:
                        order_len = len(order.order_line) - len(is_delivery_address)
                        count += 1;
                        if line.order_line_state == 'done' and line.is_delivery == False:
                            done += 1;
                        if line.order_line_state == 'waiting' and line.is_delivery == False:
                            waiting += 1;
                        if line.order_line_state == 'delivering' and line.is_delivery == False:
                            delivery += 1;
                        if line.order_line_state == 'preparing' and line.is_delivery == False:
                            status = 'Preparing'
                        if line.order_line_state == 'ready' and line.is_delivery == False:
                            ready += 1;
                        if waiting == order_len:
                            status = 'Waiting'
                        if ready == order_len:
                            status = 'Ready'
                        if delivery == order_len:
                            status = 'On the Way'
                        if done == order_len:
                            status = 'Received'
                        taxs = []
                        for tax in line.tax_id:
                            taxs.append({
                                'tax_id': tax.id,
                                'tax_name': tax.name
                            })
                        order_line.append({
                            'product_id': line.product_id.id or False,
                            'product_name': line.product_id.name or False,
                            'description': line.name or False,
                            'product_uom_qty': line.product_uom_qty or False,
                            'price_unit': line.price_unit or False,
                            'tax': taxs,
                            'product_image': url + 'web/image?model=product.product&field=image_1920&id=' + str(
                                line.product_id.id),
                        })

                    new_orders.append({'sale_order_id': order.id,
                                       'name': order.name,
                                       'date_order': order.date_order + timedelta(hours=5, minutes=30),
                                       'amount_total': order.amount_total,
                                       'status': status,
                                       'order_line': order_line,
                                       'delivery_address': {
                                           'name': order.partner_shipping_id.name or False,
                                           'street': order.partner_shipping_id.street or False,
                                           'street2': order.partner_shipping_id.street2 or False,
                                           'city': order.partner_shipping_id.city or False,
                                           'state': order.partner_shipping_id.state_id.name or False,
                                           'zip': order.partner_shipping_id.zip or False,
                                           'country': order.partner_shipping_id.country_id.name or False,
                                           'phone': order.partner_shipping_id.phone or False,
                                           'latitude': order.partner_shipping_id.latitude or False,
                                           'longitude': order.partner_shipping_id.longitude or False,
                                       },
                                       'latitude': order.latitude or False,
                                       'longitude': order.longitude or False,
                                       'amount_untaxed': order.amount_untaxed,
                                       'amount_tax': order.amount_tax,
                                       'partner_name': order.partner_shipping_id.name or False,
                                       'street': order.partner_shipping_id.street or False,
                                       'street2': order.partner_shipping_id.street2 or False,
                                       'city': order.partner_shipping_id.city or False,
                                       'state': order.partner_shipping_id.state_id.name or False,
                                       'zip': order.partner_shipping_id.zip or False,
                                       'country': order.partner_shipping_id.country_id.name or False,
                                       'phone': order.partner_shipping_id.phone or False,
                                       'cod': order.payment_method or False,
                                       })

                return {'status': 1, 'new_orders': new_orders}

        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
            }

    @http.route('/employee/order/reject', type='json', auth="public", methods=['POST'], csrf=False)
    def employee_order_reject(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            order_id = data.get('order_id', False)
            reason = data.get('reason', False)
            if user and order_id and reason:
                sale_orders = request.env['sale.order'].sudo().search([('name', '=', order_id)],limit=1)
                if sale_orders:
                    print("data",sale_orders.rejected_order_ids)
                    sale_orders.write({
                        'delivery_boy': False,
                    })
                    request.env['sale.reject'].sudo().create({
                        'delivery_boy': user.partner_id.id,
                        'reject_reason': reason,
                        'rejected_order_id': sale_orders.id
                    })
                    return {'status': 1, 'message': 'Order Rejected'}
            else:
                return {'status': 2, 'message': 'The Given Parameter are not matching'}
        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
            }

    @http.route('/employee/order/accept', type='json', auth="public", methods=['POST'], csrf=False)
    def employee_order_accept(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            order_id = data.get('order_id', False)
            if user and order_id:
                sale_orders = request.env['sale.order'].sudo().search(
                    [('name', '=', order_id), ('delivery_boy', '=', False)], limit=1)
                if sale_orders:
                    sale_orders.write({
                        'delivery_boy': user.partner_id.id,
                        'delivery_status': 'active'
                    })
                    for line in sale_orders.order_line:
                        if line.order_line_state == 'ready':
                            line.write({
                                'order_line_state': 'delivering'
                            })
                    return {'status': 1, 'message': 'Order Accepted'}
                else:
                    return {'status': 3, 'message': 'Sorry , Order already assigned to another person'}
            else:
                return {'status': 2, 'message': 'The Given Parameter are not matching'}
        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
            }

    @http.route('/employee/order/delivery', type='json', auth="public", methods=['POST'], csrf=False)
    def employee_order_delivery(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            order_id = data.get('order_id', False)
            cod = data.get('cod', False)
            if user and order_id and cod:
                sale_orders = request.env['sale.order'].sudo().search([('name', '=', order_id)], limit=1)
                if sale_orders:
                    sale_orders.write({
                        'delivery_boy': user.partner_id.id,
                        'delivery_status': 'history'
                    })
                    sale_orders.sudo().action_confirm()
                    stock_picking = request.env['stock.picking'].sudo().search([('sale_id', '=', sale_orders.id)])
                    for move in stock_picking:
                        for line in move.move_ids_without_package:
                            line.write({'quantity_done': line.product_uom_qty})
                    w = stock_picking.button_validate()
                    adv_wiz = request.env['sale.advance.payment.inv'].sudo().with_context(
                        active_ids=[sale_orders.id]).create({
                        'advance_payment_method': 'delivered',
                    })
                    adv_wiz.with_context(open_invoices=True).sudo().create_invoices()
                    confirm_invoices = request.env['account.move'].sudo().search(
                        [('invoice_origin', '=', sale_orders.name)])
                    invoice_post = confirm_invoices.sudo().action_post()
                    journal_id = request.env['account.journal'].sudo().search([('name', '=', "Cash")])
                    payment_method_id = request.env['account.payment.method'].sudo().search([('name', '=', "Manual")],
                                                                                            limit=1)
                    register_payments = request.env['account.payment.register'].sudo().with_context(
                        active_model='account.move', active_ids=confirm_invoices.id).create(
                        {
                            'journal_id': journal_id.id,
                            'payment_date': confirm_invoices.invoice_date,
                            'payment_method_id': payment_method_id.id,
                            'amount': confirm_invoices.amount_total
                        })
                    register_payments._create_payments()
                    for line in sale_orders.order_line:
                        if line.order_line_state == 'delivering':
                            line.write({
                                'order_line_state': 'done'
                            })
                    return {'status': 1, 'message': 'Order Delivery Confirmed and created invoice'}
            elif user and order_id:
                sale_orders = request.env['sale.order'].sudo().search([('name', '=', order_id)], limit=1)
                if sale_orders:
                    sale_orders.write({
                        'delivery_boy': user.partner_id.id,
                        'delivery_status': 'history'
                    })
                    sale_orders.sudo().action_confirm()
                    for line in sale_orders.order_line:
                        if line.order_line_state == 'delivering':
                            line.write({
                                'order_line_state': 'done'
                            })
                    return {'status': 1, 'message': 'Order Delivery Confirmed'}
            else:
                return {'status': 2, 'message': 'The Given Parameter are not matching'}
        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
            }

    @http.route('/employee/order/earnings', type='json', auth="public", methods=['POST'], csrf=False)
    def employee_order_earnings(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                sale_orders = request.env['sale.order'].sudo().search([('delivery_boy', '=', user.partner_id.id)])
                if sale_orders:
                    earning_dataset = []
                    order_dataset = []
                    import datetime
                    cr = request.env.cr
                    last_month_end = (datetime.datetime.today() + relativedelta(days=1)).strftime('%Y-%m-%d')
                    last_month_start = (datetime.datetime.today() - relativedelta(days=10)).strftime('%Y-%m-%d')
                    query = """SELECT so.date_order::date as date ,sum(sl.price_subtotal) as total
                                                        FROM sale_order so
                                                        LEFT JOIN sale_order_line sl ON sl.order_id = so.id
                                                        WHERE so.date_order >= %s and so.date_order <= %s and so.delivery_boy = %s and sl.is_delivery = 'True'
                                                        GROUP BY so.date_order"""
                    cr.execute(query, [str(last_month_start), str(last_month_end), user.partner_id.id])
                    sale_earning = cr.dictfetchall()
                    earning_label = []
                    earning_total_dataset = []
                    earning_count = []
                    count = 1;
                    for data in sale_earning:
                        earning_count.append(count)
                        earning_label.append(data['date'])
                        earning_total_dataset.append(data['total'])
                        count +=1;
                    query = """SELECT so.date_order::date as date ,count(so.id) as total_id
                                                                        FROM sale_order so
                                                                        LEFT JOIN sale_order_line sl ON sl.order_id = so.id
                                                                        WHERE so.date_order >= %s and so.date_order <= %s and so.delivery_boy = %s and sl.is_delivery = 'True'
                                                                        GROUP BY so.date_order"""
                    cr.execute(query, [str(last_month_start), str(last_month_end), user.partner_id.id])
                    sale_order = cr.dictfetchall()
                    order_label = []
                    order_total_dataset = []
                    order_count = []
                    count = 1;
                    for data in sale_order:
                        order_count.append(count)
                        order_label.append(data['date'])
                        order_total_dataset.append(data['total_id'])
                        count += 1;
                    order_dataset.append({
                        'order_count': order_count,
                        'order_label': order_label,
                        'order_total_dataset': order_total_dataset
                    })
                    earning_dataset.append({
                        'earning_count':earning_count,
                        'earning_label':earning_label,
                        'earning_total_dataset':earning_total_dataset
                    })

                    return {'status': 1, 'message': 'Success', 'earning_dataset': earning_dataset,'order_dataset':order_dataset}
                else:
                    return {'status': 3, 'message': 'No Orders For This User'}
            else:
                return {'status': 2, 'message': 'The Given Parameter are not matching'}
        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
            }

    @http.route('/employee/customer/lat_lang', type='json', auth="public", methods=['POST'], csrf=False)
    def employee_latitude_longitude(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                street = data.get('street')
                city = data.get('city')
                streets = str(street) + " " + str(city)
                from geopy.geocoders import Nominatim
                geolocator = Nominatim(user_agent="http")
                if streets and city:
                    try:
                        location = geolocator.geocode(streets)
                        return {'status': 1, 'message': 'Success', 'latitude': location.latitude, 'longitude': location.longitude,'address': location.address}
                    except Exception as e:
                        return {'status': 2, 'message': 'Please check the city and street parameter'}
                else:
                    return {'status': 2, 'message': 'Please check the city and street parameter'}
            else:
                return {'status': 3, 'message': 'The Given Parameter are not matching'}
        except Exception as e:
            return {
                'status': 0,
                'message': "The given user id or params is wrong"
            }

    @http.route('/employee/user/details', type='json', auth="public", methods=['POST'], csrf=False)
    def employee_user_details(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            if user:
                user_image = False
                if user.image_1920:
                    user_image = user.image_1920.decode("utf-8")
                url = request.httprequest.host_url
                user_details = {
                    'partner_name': user.partner_id.name,
                    'partner_email': user.partner_id.email,
                    'partner_phone': user.partner_id.phone,
                    'user_name': user.name,
                    'user_login': user.login,
                    'last_login': user.login_date,
                    'user_image': user_image,
                }
                print(user_details)
                return {'status': 1, 'message': 'Success', 'user_details': user_details}
            else:
                return {'status': 2, 'message': 'The Given Parameter are not matching'}
        except Exception as e:
            return {
                'status': 0,
                'message': "The given user id or params is wrong"
            }

    @http.route('/employee/forgot/password', type='json', auth="public", methods=['POST'], csrf=False)
    def forgot_password(self):
        # param: username, email, password, confirm ,
        try:
            data = request.httprequest.data
            data = json.loads(data)
            if data.get('email'):
                user = request.env['res.users'].sudo().search([('email', '=', data.get('email'))])
                if user:
                    self.web_auth_reset_password()
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

    @http.route('/employee/update/image', type='json', auth="public", methods=['POST'], csrf=False)
    def update_profile_image(self):
        # param: username, email, password, confirm ,
        try:
            data = request.httprequest.data
            data = json.loads(data)
            if data.get('user_id'):
                user = request.env['res.users'].sudo().search([('id', '=', data.get('user_id'))])
                if user:
                    if data.get('profile_image'):
                        user.sudo().write({'image_1920': data.get('profile_image')})
                        partner = request.env['res.partner'].sudo().search([('user_id', '=', data.get('user_id'))])
                        employee = request.env['hr.employee'].sudo().search([('user_id', '=', data.get('user_id'))])
                        if partner:
                            partner.sudo().write({'image_1920': data.get('profile_image')})
                        if employee:
                            employee.sudo().write({'image_1920': data.get('profile_image')})
                        return {'status': 1, 'message': "success"}
                else:
                    return {
                        'status': 0,
                        'message': "Failed"
                    }
        except Exception as e:
            return {
                'status': 0,
                'message': "Failed"
            }

    @http.route('/employee/cod/reject', type='json', auth="public", methods=['POST'], csrf=False)
    def cod_order_reject(self):
        # param: username, email, password, confirm ,
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            order_id = data.get('order_id', False)
            cod = data.get('cod', False)
            cancel_reason = data.get('cancel_reason', False)
            if user and order_id and cod and cancel_reason:
                sale_orders = request.env['sale.order'].sudo().search([('name', '=', order_id)], limit=1)
                if sale_orders:
                    sale_orders.action_cancel();
                    sale_orders.sudo().write({'delivery_status': 'cancel','cancel_reason': cancel_reason})
                    return {'status': 1, 'message': "Order Canceled"}
                else:
                    return {
                        'status': 2,
                        'message': "Order Not Found"
                    }
            else:
                return {
                    'status': 0,
                    'message': "The given user id or params is wrong"
                }
        except Exception as e:
            return {
                'status': 0,
                'message': "The given user id or params is wrong"
            }

    @http.route('/employee/update/lat_lang', type='json', auth="public", methods=['POST'], csrf=False)
    def update_lat_lang_details(self):
        # param: username, email, password, confirm ,
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user = request.env['res.users'].sudo().browse([data.get('user_id', False)])
            latitude = data.get('latitude', False)
            longitude = data.get('longitude', False)
            if user and latitude and longitude:
                user.partner_id.write({
                       'latitude': latitude,
                       'longitude': longitude
                   })
                return {
                    'status': 2,
                    'message': "Latitude and longitude updated"
                }
            else:
                return {
                    'status': 1,
                    'message': "The given user id or params is wrong"
                }
        except Exception as e:
            return {
                'status': 0,
                'message': "The given user id or params is wrong"
            }

