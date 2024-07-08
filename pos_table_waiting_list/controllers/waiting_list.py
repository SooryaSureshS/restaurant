# -*- coding: utf-8 -*-
import json
import logging
import datetime as Datetime
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

# class WebsiteBookingInformation(WebsiteSale):


class WebsiteBookingWaitlist(http.Controller):

    @http.route(['''/waiting_list/cancel/<int:id>/screen/<string:access_token>'''], type='http', auth="public", website=True)
    def waiting_cancel_list(self, id=None, access_token=None, **kw):
        if id and access_token:
            order = request.env['table.waiting.line'].sudo().search([('id', '=', id)], limit=1)
            if order.token_random == access_token:
                order.sudo().write({'status': 'cancel'})
                order.sudo().write({'token_random': ''})
                return request.render('pos_table_waiting_list.cancel_pos_failed', {'reservation': order})
            else:
                return request.render('pos_table_waiting_list.cancel_pos_invalid', {})
        else:
            return request.render('pos_table_waiting_list.cancel_pos_invalid', {})


    @http.route(['''/waiting_list/confirm/<int:id>/screen/<string:access_token>'''], type='http', auth="public", website=True)
    def waiting_confirm_list(self, id=None, access_token=None, **kw):
        if id and access_token:
            order = request.env['table.waiting.line'].sudo().search([('id', '=', id)], limit=1)
            if order.token_random == access_token:
                order.sudo().write({'status': 'confirmed'})
                order.sudo().write({'token_random': ''})
                return request.render('pos_table_waiting_list.cancel_pos_reservation', {'reservation': order})
            else:
                return request.render('pos_table_waiting_list.cancel_pos_invalid', {})
        else:
            return request.render('pos_table_waiting_list.cancel_pos_invalid', {})

