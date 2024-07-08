from __future__ import absolute_import, division, print_function
import passlib.context
import math, random
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
from passlib.context import CryptContext
from hashlib import sha256
from odoo.fields import Command


# function for getting the current database
def get_db_name():
    db = odoo.tools.config['db_name']
    if not db and hasattr(threading.current_thread(), 'dbname'):
        return threading.current_thread().dbname
    return db


class Login1(http.Controller):

    # api for listing all companies
    @http.route('/company/all', type='json', auth="public", methods=['POST', 'GET'], csrf=False)
    def company_all(self):
        try:
            company_obj = request.env['res.company'].sudo().search([])
            list = []
            if company_obj:
                dict = {}
                for company in company_obj:
                    dict['company_id'] = company.id
                    dict['name'] = company.name
                    list.append(dict)
            return {'success': True, 'company_details': list}
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # api for showing contact us
    @http.route('/company/contact_us.css', type='json', auth="public", methods=['POST', 'GET'], csrf=False)
    def company(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            company_id = data.get('company _id"')

            company_obj = request.env['res.company'].sudo().search([('id', '=', company_id)])
            list = []
            if company_obj:
                dict = {}
                for company in company_obj:
                    dict['company_id'] = company.id
                    dict['name'] = company.name
                    dict['street'] = company.street
                    dict['steet2'] = company.street2
                    dict['city'] = company.city
                    dict['state'] = company.state_id.name
                    dict['zip'] = company.zip
                    dict['country'] = company.country_id.name
                    dict['phone'] = company.phone
                    dict['email'] = company.email

            return {'success': True, 'company_details': dict}
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # api for company policy
    @http.route('/company/policy', type='json', auth="public", methods=['POST', 'GET'], csrf=False)
    def policy(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            company_id = data.get('company_obj')

            company_obj = request.env['res.company'].sudo().search([('id', '=', company_id)])
            if company_obj:
                dict = {}
                for company in company_obj:
                    dict['company_id'] = company.id
                    dict['policy'] = company.policy
            return {'success': True, 'company_details': dict}
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # api for listing the about_us  of company
    @http.route('/company/about_us', type='json', auth="public", methods=['POST', 'GET'], csrf=False)
    def about_us(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            company_id = data.get('company_obj')

            company_obj = request.env['res.company'].sudo().search([('id', '=', company_id)])
            if company_obj:
                dict = {}
                for company in company_obj:
                    dict['company_id'] = company.id
                    dict['about_us'] = company.about_us
            return {'success': True, 'company_details': dict}
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # api for listing the payment delivery of company
    @http.route('/company/payment_delivery', type='json', auth="public", methods=['POST', 'GET'], csrf=False)
    def payment_delivery(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            company_id = data.get('company_obj')

            company_obj = request.env['res.company'].sudo().search([('id', '=', company_id)])
            if company_obj:
                dict = {}
                for company in company_obj:
                    dict['company_id'] = company.id
                    dict['payment_delivery'] = company.payment_delivery
            return {'success': True, 'company_details': dict}
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # api for listing lang
    @http.route('/company/lang', type='json', auth="public", methods=['POST', 'GET'], csrf=False)
    def lang_details(self):
        try:
            lang_obj = request.env['res.lang'].sudo().search([('active', '=', True)])
            list = []
            for lang in lang_obj:
                dict = {}
                dict['lang_id'] = lang.id
                dict['name'] = lang.name
                dict['code'] = lang.code
                list.append(dict)
            return {'success': True, 'lang_details': list}
        except Exception as e:
            return {
                'status': 0,
                'message': "No Lang Found"
            }

    # change password api for logged user
    @http.route('/change/user/password', type='json', auth="user", methods=['POST'], csrf=False)
    def reset_password(self):
        ctx = passlib.context.CryptContext(
            ['pbkdf2_sha512', 'plaintext'],
            deprecated=['plaintext'],
        )

        try:
            data = request.httprequest.data
            data = json.loads(data)
            user_id = data.get('user_id')
            user_id = request.env['res.users'].sudo().search([('id', '=', user_id)])
            old_password = data.get('old_password')

            new_password = data.get('new_password')
            confirmed_password = data.get('confirmed_password')
            if user_id:
                if new_password == confirmed_password:
                    hash_password = ctx.hash if hasattr(ctx, 'hash') else ctx.encrypt
                    user_id._set_encrypted_password(user_id.id, hash_password(confirmed_password))
                    return {'success': True, 'message': "New Password has been reset"}
                else:
                    return {
                        'status': 0,
                        'message': "Passwords are not match"
                    }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # api for editing the profile
    # @http.route('/user/edit_details', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    # def edit_details(self):
    #     try:
    #         data = request.httprequest.data
    #         data = json.loads(data)
    #         user_id = data.get('user_id')
    #         user_obj = request.env['res.users'].sudo().search([('id', '=', user_id)])
    #         if user_obj:
    #             dict = {
    #                 # 'name':data.get('name'),
    #                 'email': data.get('email'),
    #                 'phone': data.get('phone'),
    #                 'street': data.get('street'),
    #                 'street2': data.get('street2'),
    #                 'city': data.get('city'),
    #                 'state_id': data.get('state'),
    #                 'zip': data.get('zip'),
    #                 'country_id': data.get('country')
    #             }
    #             print('dct', user_obj.partner_id.id, dict)
    #             user_obj.partner_id.sudo().write(dict)
    #         return {'success': True,
    #                 'user_id': user_obj.id,
    #                 'message': "Sucessfully Updated"
    #                 }
    #
    #     except Exception as e:
    #         return {
    #             'status': 0,
    #             'message': e
    #         }

    # api for notification
    @http.route('/user/notification', type='json', auth="public", methods=['POST', 'GET'], csrf=False)
    def notification(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user_id = data.get('user_id')
            notification = data.get('notification')
            user_obj = request.env['res.users'].sudo().search([('id', '=', user_id)])
            if user_obj:
                if notification == True:
                    user_obj.write({'notification': True})
                else:
                    user_obj.write({'notification': False})

                return {'success': True,
                        'user_id': user_obj.id,
                        'message': "Notification Updated"
                        }
            else:
                return {'success': True,
                        'user_id': user_obj.id,
                        'message': "User is Not  Correct"
                        }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # api for Information Connection
    @http.route('/user/details', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def UserDetails(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user_id = data.get('user_id')
            user_obj = request.env['res.users'].sudo().search([('id', '=', user_id)])
            if user_obj:
                dict = {}
                dict['id'] = user_obj.id
                dict['company'] = user_obj.partner_id.company_name if user_obj.partner_id.company_name else user_obj.company_id.name
                dict['name'] = user_obj.partner_id.name
                dict['email'] = user_obj.partner_id.email
                dict['phone'] = user_obj.partner_id.phone
                dict['street'] = user_obj.partner_id.street
                dict['street2'] = user_obj.partner_id.street2
                dict['zip'] = user_obj.partner_id.zip if user_obj.partner_id.zip else ''
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

    # api for users orders list
    # apram:user_id
    @http.route('/user/orderlist', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def orderlist(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user_id = data.get('user_id')
            user_obj = request.env['res.users'].sudo().search([('id', '=', user_id)])
            if user_obj:
                saleorder_obj = request.env['sale.order'].sudo().search([('user_id', '=', user_obj.id),
                                                                         ('state', 'in', ['sale', 'done'])])
                order_list = {}
                if saleorder_obj:
                    for saleorder in saleorder_obj:
                        dict = {}
                        dict['id'] = saleorder.id
                        dict['name'] = saleorder.name
                        dict['date_order'] = saleorder.date_order
                        order_list.append(dict)
                return {'success': True,
                        'user_id': user_obj.id,
                        'orderlist': order_list,
                        'message': "Order Listed Successfully"
                        }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # api for user order
    # param: saleorder id
    @http.route('/user/order', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def orderdetails(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            order_id = data.get('order_id')
            saleorder_obj = request.env['sale.order'].sudo().search([('id', '=', order_id)])
            if saleorder_obj:
                sale_dict = {}
                sale_dict['order_id'] = saleorder_obj.id
                sale_dict['name'] = saleorder_obj.name
                sale_dict['order_date'] = saleorder_obj.date_order

                total_json = json.loads(saleorder_obj.tax_totals_json)
                sale_dict['amount_total'] = total_json.get('amount_total')
                sale_dict['amount_untaxed'] = total_json.get('amount_untaxed')
                sale_dict['amount_taxed'] = total_json.get('amount_total') - total_json.get('amount_untaxed')
                delivery_dict = {}
                delivery_dict['street'] = saleorder_obj.partner_shipping_id.street or ''
                delivery_dict['street2'] = saleorder_obj.partner_shipping_id.street2 or ''
                delivery_dict['city'] = saleorder_obj.partner_shipping_id.city or ''
                delivery_dict['state'] = saleorder_obj.partner_shipping_id.state_id.name or ''
                delivery_dict['country_id'] = saleorder_obj.partner_shipping_id.country_id.name or ''
                delivery_dict['zip'] = saleorder_obj.partner_shipping_id.zip or ''
                delivery_dict['delivery_method'] = ''
                sale_dict['delivery_details'] = delivery_dict
                line_list = []
                for line in saleorder_obj.order_line:
                    line_dict = {}
                    line_dict['id'] = line.id
                    line_dict['product'] = line.product_id.display_name
                    line_dict['qty'] = line.product_uom_qty
                    line_dict['unit_price'] = line.price_unit
                    line_dict['subtotal'] = line.price_subtotal
                    line_list.append(line_dict)
                sale_dict['order_line'] = line_list
                invoice_obj = request.env['account.move'].sudo().search([('invoice_origin', '=', saleorder_obj.name)])
                if invoice_obj:
                    sale_dict['invoice_id'] = invoice_obj.id
                    sale_dict['invoice_number'] = invoice_obj.name
                    if invoice_obj.state in ['draft', 'posted']:
                        payment_json = json.loads(invoice_obj.invoice_payments_widget)
                        for payment_data in payment_json.get('content'):
                            payment_dict = {}
                            payment_dict['payment_method'] = payment_data.get('journal_name')
                            payment_dict['amount'] = payment_data.get('amount')
                            payment_dict['currency'] = payment_data.get('currency')
                            payment_dict['payment_date'] = payment_data.get('date')
                            payment_dict['payment_id'] = payment_data.get('payment_id')
                        sale_dict['payment_details'] = payment_dict

            return {'success': True,
                    'saleorder_id': saleorder_obj.id,
                    'order_details': sale_dict,
                    'message': "Order Fetched Successfully"
                    }

        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # param: saleorder id
    # api for user order invoice
    @http.route('/user/order/invoice', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def OrderInvoice(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            order_id = data.get('order_id')
            saleorder_obj = request.env['sale.order'].sudo().search([('id', '=', order_id)])
            if saleorder_obj:
                invoice_obj = request.env['account.move'].sudo().search([('invoice_origin', '=', saleorder_obj.name)])
                invoice_dict = {}
                if invoice_obj:
                    invoice_dict['id'] = invoice_obj.id
                    invoice_dict['number'] = invoice_obj.name
                    invoice_dict['invoice_date'] = invoice_obj.invoice_date
                    line_list = []

                    for line in invoice_obj.invoice_line_ids:
                        line_dict = {}
                        line_dict['line_id'] = line.id
                        line_dict['product_id'] = line.product_id.id
                        line_dict['product_name'] = line.product_id.display_name
                        line_dict['qty'] = line.quantity
                        line_dict['price_unit'] = line.price_unit
                        line_dict['subtotal'] = line.price_subtotal
                        line_list.append(line_dict)
                    invoice_dict['invoice_line'] = line_list
                    total_json = json.loads(invoice_obj.tax_totals_json)

                    invoice_dict['amount_total'] = total_json.get('amount_total')
                    invoice_dict['amount_untaxed'] = total_json.get('amount_untaxed')
                    invoice_dict['amount_taxed'] = total_json.get('amount_total') - total_json.get('amount_untaxed')
                    # payment_json=json.loads(invoice_obj.invoice_payments_widget)
                    #
                    # for payment_data in payment_json.get('content'):
                    #     payment_dict={}
                    #     payment_dict['payment_method']=payment_data.get('journal_name')
                    #     payment_dict['amount']=payment_data.get('amount')
                    #     payment_dict['currency']=payment_data.get('currency')
                    #     payment_dict['payment_date']=payment_data.get('date')
                    #     payment_dict['payment_id']=payment_data.get('payment_id')
                    # invoice_dict['payment_details']=payment_dict

                return {'success': True,
                        'saleorder_id': saleorder_obj.id,
                        'invoice_details': invoice_dict,
                        'message': "Invoice Fetched Successfully"
                        }

        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # param: user_id
    # api for listout the user quotations
    @http.route('/user/quotation', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def AddingCart(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            user_id = data.get('user_id')
            quotation_obj = request.env['sale.order'].sudo().search(
                [('state', 'in', ['draft', 'sent']), ('user_id', '=', user_id)])
            if quotation_obj:
                quotation_list = []
                for quotation in quotation_obj:
                    quotation_dict = {}
                    quotation_dict['id'] = quotation.id
                    quotation_dict['name'] = quotation.name
                    quotation_dict['order_date'] = quotation.date_order
                    line_list = []
                    for line in quotation.order_line:
                        print('ff', line.product_id.id, line.product_id.display_name)
                        line_dict = {}
                        line_dict['id'] = line.id
                        line_dict['product'] = line.product_id.display_name
                        line_dict['qty'] = line.product_uom_qty
                        line_dict['unit_price'] = line.price_unit
                        line_dict['subtotal'] = line.price_subtotal
                        line_list.append(line_dict)
                    quotation_dict['line_details'] = line_list
                    quotation_list.append(quotation_dict)
            return {
                'success': True,
                'quotation_details': quotation_list,
                'message': "Quotation Fetched Successfully"
            }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # param: order id
    # api for clearing  cart(full)
    @http.route('/empty/cart', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def EmptyCart(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            order_id = data.get('order_id')
            saleorder_obj = request.env['sale.order'].sudo().search([('id', '=', order_id)])
            if saleorder_obj:
                saleorder_obj.sudo().write({'state': 'cancel'})
                return {'success': True,
                        'saleorder_id': saleorder_obj.id,
                        'message': "Cart Empted Successfully"
                        }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # param: saleorderline id
    # api for remove item in cart
    @http.route('/cart/empty_item', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def removeitem(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            line_id = data.get('line_id')
            for rec in line_id:
                line_obj = request.env['sale.order.line'].sudo().search([('id', '=', rec)])
                if line_obj:
                    line_obj.sudo().unlink()
            return {'success': True,
                    'sale_order_id': line_id,
                    'message': "Remove Item Successfully"
                    }

        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # api for add/update the product details in cart
    @http.route('/create/cart', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def productdetails1(self):
        print('productdetails')
        try:
            data = request.httprequest.data
            data = json.loads(data)
            order_details = data.get('order_details')
            sale_id = order_details.get('saleorder_id')
            user_obj = request.env['res.users'].sudo().search([('id', '=', order_details.get('user_id'))])
            if user_obj:
                if order_details.get('saleorder_id') == False:
                    saleorder_obj = request.env['sale.order']
                    saleorder_vals = {
                        'partner_id': user_obj.partner_id.id,
                        'partner_invoice_id': user_obj.partner_id.id,
                        'partner_shipping_id': user_obj.partner_id.id,
                        'date_order': datetime.now(),
                        'pricelist_id': user_obj.partner_id.property_product_pricelist.id,
                        'state': 'draft',
                        'picking_policy': 'direct',
                        'user_id': user_obj.id
                    }
                    saleorder_obj = saleorder_obj.sudo().create(saleorder_vals)
                    sale_id = saleorder_obj.id
                for line in order_details.get('orderline'):
                    product_obj = request.env['product.product'].sudo().search([('id', '=', line.get('product_id'))])
                    line_dict = {
                        'order_id': sale_id,
                        'product_id': line.get('product_id'),
                        'product_template_id': product_obj.product_tmpl_id.id,
                        'name': product_obj.description_sale or 'DES',
                        'product_uom_qty': line.get('qty'),
                        'product_uom': product_obj.uom_id.id,
                        'price_unit': product_obj.lst_price,
                        'customer_lead': 0,
                        'price_subtotal': product_obj.lst_price * line.get('qty')
                    }
                    saleline_obj = request.env['sale.order.line'].sudo().create(line_dict)

            return {'success': True,
                    'saleorder_id': sale_id,
                    'message': "Item Added Successfully"
                    }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # param:saleorder id,coupon code
    # api for add/update the product details in cart
    @http.route('/apply/coupon', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def apply_coupon(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            order_obj = request.env['sale.order'].sudo().search([('id', '=', data.get('order_id'))])
            if order_obj:
                coupon_status = request.env['sale.coupon.apply.code'].sudo().apply_coupon(order_obj,
                                                                                          data.get('coupon_code'))
                if coupon_status.get('not_found', False):
                    coupon_message = "Not Found"
                elif coupon_status.get('error', False):
                    coupon_message = coupon_status.get('error')
                else:
                    coupon_message = "Coupon Applied"
                return {'success': True,
                        'saleorder_id': data.get('order_id'),
                        'message': coupon_message
                        }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # param:saleorder id
    # checkout page contains details about shipping methods,delivery address,contact details
    @http.route('/user/checkout/1', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def Checkout(self):
        print('checkout')
        try:
            data = request.httprequest.data
            data = json.loads(data)
            print('data', data)
            shipping_method_obj = request.env['delivery.carrier'].sudo().search([('is_published', '=', True)])
            result = {}
            if shipping_method_obj:
                shipping_method_list = []
                for shipping in shipping_method_obj:
                    dict = {}
                    dict['id'] = shipping.id
                    dict['name'] = shipping.name
                    dict['amount'] = shipping.fixed_price
                    shipping_method_list.append(dict)
                result['shipping_methods'] = shipping_method_list
            saleorder_obj = request.env['sale.order'].sudo().search([('id', '=', data.get('order_id'))])
            if saleorder_obj:
                result['order_id'] = data.get('order_id')
                result['saleorder'] = saleorder_obj.name
                delivery = saleorder_obj.partner_id.child_ids.filtered(lambda c: c.type == 'delivery')
                if delivery:
                    delivery_details = {}
                    delivery_details['customer_id'] = delivery.id
                    delivery_details['customer_name'] = delivery.name
                    delivery_details['street'] = delivery.street
                    delivery_details['street2'] = delivery.street2
                    delivery_details['state'] = delivery.state_id.name
                    delivery_details['country'] = delivery.country_id.name
                    delivery_details['zip'] = delivery.zip
                result['delivery_address'] = delivery_details
                result['company'] = saleorder_obj.partner_id.company_id.name
                result['mobile'] = saleorder_obj.partner_id.mobile
                result['phone'] = saleorder_obj.partner_id.phone

            return {'success': True,
                    'checkout_details': result,
                    'message': 'Checkout Details Fetched Successfully'
                    }

        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # param:saleorder id
    # checkout page contains details about shipping methods,delivery address,contact details
    @http.route('/user/checkout/1/edit', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def CheckoutEdit(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            if data.get('delivery_method'):
                shipping_method_obj = request.env['delivery.carrier'].sudo().search(
                    [('id', '=', data.get('delivery_method'))])
                if shipping_method_obj:
                    order_obj = request.env['sale.order'].sudo().search([('id', '=', data.get('order_id'))])
                    if order_obj:
                        order_obj._check_carrier_quotation(force_carrier_id=shipping_method_obj.id)

            return {'success': True,
                    'message': 'Checkout Details Updated Successfully'
                    }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # for list out the payment methods
    @http.route('/user/paymentmethods', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def Paymentmethods(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            acquirer_obj = request.env['payment.acquirer'].sudo().search([('state', '=', 'enabled')])
            acquirer_list = []
            if acquirer_obj:
                for acquirer in acquirer_obj:
                    acquirer_dict = {}
                    acquirer_dict['id'] = acquirer.id
                    acquirer_dict['name'] = acquirer.name
                    acquirer_list.append(acquirer_dict)
            return {'success': True,
                    'payment_methods': acquirer_list,
                    'message': 'Payment Methods Fetched Successfully'
                    }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # api checkout order details
    # param:saleorder_id
    @http.route('/checkout/order', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def CheckoutOrder(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            saleorder = data.get('saleorder_id')
            saleorder_obj = request.env['sale.order'].sudo().search([('id', '=', saleorder)])
            saleorder_dict = {}
            if saleorder_obj:
                saleorder_dict['id'] = saleorder_obj.id
                saleorder_dict['number'] = saleorder_obj.name
                line_list = []
                for line in saleorder_obj.order_line.filtered(lambda x: x.product_id.type in ['storable']):
                    line_dict = {}
                    line_dict['id'] = line.id
                    line_dict['product_name'] = line.product_id.display_name
                    line_dict['qty'] = line.product_uom_qty
                    line_dict['unit_price'] = line.price_unit
                    line_dict['subtotal'] = line.price_subtotal
                    line_list.append(line_dict)

                # saleorder_dict['amount_total'] = sum(
                #     saleorder_obj.order_line.filtered(lambda x: x.product_id.detailed_type == 'product').mapped(
                #         'price_subtotal'))
                # saleorder_dict['delivery_amt'] = sum(
                #     saleorder_obj.order_line.filtered(lambda x: x.is_delivery == True).mapped('price_subtotal'))
                # saleorder_dict['reward_amt'] = sum(
                #     saleorder_obj.order_line.filtered(lambda x: x.is_reward_line == True).mapped('price_subtotal'))
                # saleorder_dict['Final_total'] = saleorder_dict['amount_total'] + saleorder_dict['delivery_amt'] + \
                #                                 saleorder_dict['reward_amt']
            return {'success': True,
                    'order_details': saleorder_dict,
                    'message': 'Payment Methods Fetched Successfully'
                    }

        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # for list out the payment methods
    @http.route('/update/user/paymentmethod', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def UpdatePaymentmethod(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            acquirer_obj = request.env['payment.acquirer'].sudo().search([('state', '=', 'enabled')])
            acquirer_list = []
            if acquirer_obj:
                for acquirer in acquirer_obj:
                    acquirer_dict = {}
                    acquirer_dict['id'] = acquirer.id
                    acquirer_dict['name'] = acquirer.name
                    acquirer_list.append(acquirer_dict)
            return {'success': True,
                    'payment_methods': acquirer_list,
                    'message': 'Payment Methods Fetched Successfully'
                    }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    # Api for order process
    @http.route('/order/process', type='json', auth="user", methods=['POST', 'GET'], csrf=False)
    def OrderProcess(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            order_id = data.get('order_id')
            acquirer = data.get('payment_details')['payment_method']

            order_obj = request.env['sale.order'].sudo().search([('id', '=', order_id)])
            acquirer_obj = request.env['payment.acquirer'].sudo().search([('id', '=', acquirer)])

            custom_create_values = {}
            custom_create_values['sale_order_ids'] = [Command.set([int(order_obj.id)])]

            reference = request.env['payment.transaction'].sudo()._compute_reference(
                acquirer_obj.provider,
                prefix=order_obj.name,
                **(custom_create_values or {})
            )
            values = {
                # 'sale_order_ids':order_obj.ids or False,
                'acquirer_id': int(acquirer),
                'reference': reference,
                'amount': float(data.get('payment_details')['amount']),
                'currency_id': int(order_obj.currency_id.id),
                'partner_id': order_obj.partner_id.id,
                'operation': 'online_direct',

            }
            tx = request.env['payment.transaction'].sudo().with_context(lang=None).create(values)
            if data.get('payment_details')['payment_status'] == 'success':
                tx.sudo().write({'state': 'done'})
                order_obj.sudo().write({'state': 'sale'})
            elif data.get('payment_details')['payment_status'] == 'pending':
                tx.sudo().write({'state': 'pending'})
            elif data.get('payment_details')['payment_status'] in ['cancel', 'fail']:
                tx.sudo().write({'state': 'cancel'})

            return {
                'status': 0,
                'transcation_id': 1,
                'payment_id': 1,
                'message': "Payment Updated Successfully"
            }

        except Exception as e:
            return {
                'status': 0,
                'message': e
            }
