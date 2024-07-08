# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID
from odoo.http import request, route
from odoo.addons.bus.controllers.main import BusController
from odoo.http import Controller, route, request
from odoo import http
import time
from odoo import models, fields, api, tools, _
from datetime import timedelta
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)



class BoardRecallOrders(Controller):

    @route('/recall/orders', type="json", auth="public", cors="*")
    def recallOrders(self):
        pos = []
        sale = []
        posLine = request.env['pos.order'].sudo().search([('date_order', '>=', fields.Date.today())], order='id ASC', limit=1000)
        saleLine = request.env['sale.order'].sudo().search([('date_order', '>=', fields.Date.today()),('state','=','sale')], order='id ASC', limit=1000)
        for i in posLine:
            t2 = i.date_order + timedelta(hours=5, minutes=30)
            list = []
            for line in i.lines:
                data = {
                    'create_date': line.create_date + timedelta(hours=5, minutes=30),
                    'floor': line.floor,
                    'full_product_name': line.full_product_name,
                    'id': line.id,
                    'name': line.name,
                    'note': line.note,
                    'order_line_note': line.order_line_note,
                    'order_line_state': line.order_line_state,
                    'qty': line.qty,
                    'table': line.table,
                    'pos_categ_id': line.pos_categ_id,
                    'customer': [line.customer.id, line.customer.name] or False,
                    'price_lst': line.product_id.lst_price or False,
                    'price': line.price_subtotal or False,
                    'discount': line.discount or False,
                    'price_display': line.price_subtotal_incl or False,
                    'product_name': line.product_id.name or False,
                    'unit': line.product_uom_id.name or False,
                    'price_unit': line.price_unit or False
                    # 'display_discount_policy': line.display_discount_policy or False,
                    # 'price_with_tax_before_discount': line.price_with_tax_before_discount or False,
                }
                list.append(data)
            dict = {
                'name': i.name,
                'customer': [i.partner_id.id, i.partner_id.name] or False,
                'order_id': i.id,
                'lines': list,
                'order_time': t2.strftime('%H:%M'),
                'preparation_time': i.preparation_time,
                'type': 'pos',
                'amount_total': i.amount_total,
                'amount_tax': i.amount_tax,
                'preparation_date': i.preparation_date + timedelta(hours=5, minutes=30),
                'preparation_estimation': i.preparation_date + timedelta(hours=5, minutes=30) + timedelta(hours=0,minutes=i.preparation_time),
                'kitchen_screen': i.kitchen_screen,
                'pos_reference': i.pos_reference,
                'customer_name': i.partner_id.name
            }
            pos.append(dict)
        for i in saleLine:
            t2 = i.date_order + timedelta(hours=5, minutes=30)
            list = []
            for line in i.order_line:
                data = {
                    'create_date': line.create_date + timedelta(hours=5, minutes=30),
                    'floor': False,
                    'full_product_name': line.product_id.name,
                    'id': line.id,
                    'name': line.name,
                    'note': line.order_line_note or False,
                    'order_line_note': line.order_line_note,
                    'order_line_state': line.order_line_state,
                    'qty': line.product_uom_qty,
                    'table': False,
                    'pos_categ_id': line.pos_categ_id,
                    'customer': False,
                    'price_lst': line.product_id.lst_price or False,
                    'price': line.price_subtotal or False,
                    'discount': line.discount or False,
                    'price_display': line.price_subtotal or False,
                    'product_name': line.product_id.name or False,
                    'unit': line.product_uom.name or False,
                    'price_unit': line.price_unit or False
                    # 'display_discount_policy': line.display_discount_policy or False,
                    # 'price_with_tax_before_discount': line.price_with_tax_before_discount or False,
                }
                list.append(data)
            dict = {
                'name': i.name,
                'customer': [i.partner_id.id, i.partner_id.name] or False,
                'order_id': i.id,
                'lines': list,
                'order_time': t2.strftime('%H:%M'),
                'preparation_time': i.preparation_time,
                'type': 'pos',
                'amount_total': i.amount_total,
                'amount_tax': i.amount_tax,
                'preparation_date': i.preparation_date + timedelta(hours=5, minutes=30),
                'preparation_estimation': i.preparation_date + timedelta(hours=5, minutes=30) + timedelta(hours=0,
                                                                                                          minutes=i.preparation_time),
                'kitchen_screen': i.kitchen_screen,
                'pos_reference': i.name,
                'customer_name': i.partner_id.name
            }
            sale.append(dict)
        return [pos,sale]