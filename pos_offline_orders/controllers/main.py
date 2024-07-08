from odoo.http import request
import pytz
from datetime import datetime
from odoo import http, api, fields, models, _
# import datetime
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import timedelta


class WebsiteCache(WebsiteSale):
    @http.route('/clear/order', type='json', auth="public", website=True, sitemap=False)
    def WebsiteCacheClear(self, **kw):
        try:
            order = request.website.sale_get_order()
            if order and order.state not in ['sale', 'sent', 'cancel']:
                order_date = order.date_order
                current = request.env.company
                tz = pytz.timezone(current.tz)
                current_date_time = datetime.now(tz).astimezone(tz)
                time_now1 = current_date_time.replace(microsecond=0)
                time_now = time_now1.replace(tzinfo=None)
                now = datetime.utcnow()
                utc = pytz.timezone('UTC')
                utc.localize(datetime.now())
                delta = utc.localize(now) - tz.localize(now)
                sec = delta.seconds
                total_minute = sec / 60
                order_time = order.date_order + timedelta(minutes=total_minute)
                time_difference = time_now - order_time
                kvs_sec_time = time_difference.total_seconds()
                kvs_min_time = kvs_sec_time / 60
                if kvs_min_time > 60:
                    order.sudo().unlink()
                    return False
                else:
                    return True
        except:
            pass
        # order_id = int(kw['order_id'])
        # delivery = str(kw['delivery_type'])
        # method = ""
        # if delivery == 'pickup':
        #     method = "pickup"
        # elif delivery == 'delivery':
        #     method = "delivery"
        # elif delivery == 'curb':
        #     method = "curb"
        # if order_id:
        #     order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
        #     if order:
        #         if order.order_line:
        #             for lines in order.order_line:
        #                 if lines.is_reward_line:
        #                     lines.unlink()
        #         order.sudo().write({'website_delivery_type': method})
