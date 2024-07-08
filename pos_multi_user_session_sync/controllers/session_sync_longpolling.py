# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID
from odoo.http import request, route
from odoo.addons.bus.controllers.main import BusController
from odoo.http import Controller, route, request
from odoo import http
import time
from odoo import models, fields, api, tools, _
import pytz
import datetime
from datetime import date
from datetime import datetime
from odoo.addons.kitchen_order.controllers import order_template
from dateutil.relativedelta import relativedelta



class OrderSyncLongPooling(Controller):

    @route('/polling/userinfo', type="json", auth="public", cors="*", csrf=False)
    def PollFetchDataNew(self, session_id, name):
        print("info data",name)
        data = {}
        if name:
            orders = request.env['pos.order'].sudo().search([('pos_reference','=',name)],limit=1)
            for i in orders:
                data = {
                    'payment_initiation': i.payment_initiation.id,
                    'payment_proceed': i.payment_proceed,
                    'employee': i.payment_initiation.name,
                }
                # data.append(d)

        # for order in orders:
        #     line = []
        #     for i in order.lines:
        #         p = {
        #             'product_id': i.product_id.id,
        #             'product_name': i.product_id.name,
        #             'qty': i.qty,
        #         }
        #         line.append(p)
        #     dict = {
        #         'order_id': order.id,
        #         'employee_id': order.employee_id.id,
        #         'date_order': order.date_order,
        #         'table_id': order.table_id.id,
        #         'partner_id': order.partner_id.id,
        #         'line': line
        #     }
        #     data.append(dict)
        return data

