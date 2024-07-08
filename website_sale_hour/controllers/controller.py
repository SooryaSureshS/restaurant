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
from odoo import http, api, fields, models,_
import datetime
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class WebsiteSale(WebsiteSale):

    @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        """
        Main cart management + abandoned cart revival
        access_token: Abandoned cart SO access token
        revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
        """
        order = request.website.sale_get_order()
        # surcharge = order.order_line.search([("name", '=', "Holiday surcharge")], limit=1)
        # _logger.info("ahkbhcdbc", surcharge)
        # surcharge_product = request.env['product.product'].sudo().search([('name', '=', "Holiday surcharge")], limit=1)
        # if surcharge_product:
        #     try:
        #         request.env['sale.order.line'].browse(surcharge.id).unlink()
        #     except:
        #     #     surcharge.write({'product_uom_qty': 0})
        #         pass
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        values = {}
        if access_token:
            abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
            if not abandoned_order:  # wrong token (or SO has been deleted)
                raise NotFound()
            if abandoned_order.state != 'draft':  # abandoned cart already finished
                values.update({'abandoned_proceed': True})
            elif revive == 'squash' or (revive == 'merge' and not request.session.get('sale_order_id')):  # restore old cart or merge with unexistant
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cart')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session.get('sale_order_id'):  # abandoned cart found, user have to choose what to do
                values.update({'access_token': abandoned_order.access_token})

        values.update({
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': [],
        })
        if order:
            order.order_line.filtered(lambda l: not l.product_id.active).unlink()
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})
        blocked = self.block_order()
        order_id = order.id
        order.sudo().write({'hour_website': blocked})

        if order.order_line:
            sorted_product = sorted(order.order_line, key=lambda x: x.product_id.pos_categ_id.sequence)
            print(sorted_product)
            seq = 0
            for k in sorted_product:
                print(k.product_id.name)
                k.sudo().write({'sequence': seq})
                for i in order.order_line:
                    if i.linked_line_id:
                        i.sudo().write({'sequence': i.linked_line_id.sequence})
                        # i.sequence = i.linked_line_id.sequence
                seq += 1
        values = {
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': [],
        }
        return request.render("website_sale.cart", values)

    def block_order(self):

        res_config_settings = request.env['ir.config_parameter'].sudo()
        weekday_from_1 = res_config_settings.get_param('website_sale_hour.weekday_from_1')
        weekday_from_2 = res_config_settings.get_param('website_sale_hour.weekday_from_2')
        weekday_to_1 = res_config_settings.get_param('website_sale_hour.weekday_to_1')
        weekday_to_2 = res_config_settings.get_param('website_sale_hour.weekday_to_2')

        from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_1')
        to_time_1 = res_config_settings.get_param('website_sale_hour.time_to_1')
        from_time_2 = res_config_settings.get_param('website_sale_hour.time_from_2')
        to_time_2 = res_config_settings.get_param('website_sale_hour.time_to_2')
        time_from_1 = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_1) * 60, 60))
        time_from_2 = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_2) * 60, 60))
        time_to_1 = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_1) * 60, 60))
        time_to_2 = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_2) * 60, 60))

        days = [0,1,2,3,4,5,6]
        this_day1 = datetime.datetime.now()
        this_day_1 = this_day1.weekday()
        this_time1 = datetime.datetime.now()
        this_time = this_time1.strftime('%H:%M')
        from_1 = int(weekday_from_1)
        to_1 = int(weekday_to_1)
        from_2 = int(weekday_from_2)
        to_2 = int(weekday_to_2)

        tz = pytz.timezone('Australia/Brisbane')
        this_day1 = datetime.datetime.now(tz)
        this_day = this_day1.weekday()
        this_time1 = datetime.datetime.now()+datetime.timedelta(hours=10, minutes=00)
        this_timee = this_time1.strftime('%H.%M')
        this_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(this_timee) * 60, 60))
        now = int(this_day)



        if not weekday_from_1 and not weekday_from_2:
            return True
        if not weekday_to_2 and not weekday_to_1:
            return True
        if not time_from_1 and not time_from_2:
            return True
        if not time_to_1 and not time_to_2:
            return True
        if int(weekday_from_1) >= 0 and int(weekday_to_1) >= 0:
            data = []
            if weekday_from_1 is '6':
                frm_index = [6]
                data = days[:int(weekday_to_1) + 1] + frm_index
            else:
                data = days[int(weekday_from_1):int(weekday_to_1) + 1]
            if data:
                if now in data:
                    if this_time >= time_from_1 and this_time <= time_to_1:
                        return True
                    else:
                        pass
                else:
                    pass
        else:
            pass

        if int(weekday_from_2) >= 0 and int(weekday_to_2) >= 0:
            frm_index = days[int(weekday_from_2):]
            to_index = days[:int(weekday_to_2) + 1]
            data = []
            if weekday_from_2 is '6':
                frm_index = [6]
                data = days[:int(weekday_to_2) + 1] + frm_index
            else:
                data = days[int(weekday_from_2):int(weekday_to_2) + 1]

            if data:
                if now in data:
                    if this_time >= time_from_2 and this_time <= time_to_2:
                        return True
                    else:
                        return False
                else:
                    return False
        else:
            return False
