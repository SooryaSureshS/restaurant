from odoo.addons.theme_wineshop.controllers.main import WineWebsiteSale
from odoo.http import request
import pytz
from odoo import http, api, fields, models, _

from datetime import timedelta
from datetime import datetime


class WineWebsiteSaleQrcodeBanner(WineWebsiteSale):

    @http.route(['/check/auth/banner'], type='json', auth="public", methods=['POST'], website=True)
    def index_sale_banner_auth(self, **kw):
        config_check_parms = self.config_check_parms()
        if config_check_parms:
            res_config_settings = request.env['ir.config_parameter'].sudo()
            popup_timing = res_config_settings.get_param('busy_banner.popup_timing')
            current_order = request.website.sale_get_order(force_create=True)
            return {'order': current_order.id, 'status':True, 'popup_timing': popup_timing}
        else:
            return False
        return False

    def _check_qr_code_process(self):
        current_order = request.website.sale_get_order(force_create=True)
        if current_order.qrcode_order:
            return True
        else:
            return False

    def config_check_parms(self):
        res_config_settings = request.env['ir.config_parameter'].sudo()
        enable_busy_banner = res_config_settings.get_param('busy_banner.enable_busy_banner')
        if enable_busy_banner:
            busy_banner_display = res_config_settings.get_param('busy_banner.busy_banner_display')
            if float(busy_banner_display) > 0:
                qr_order = self._check_qr_code_process()
                if qr_order:
                    return True
            else:
                return False

    @http.route(['/check/banner'], type='json', auth="public", methods=['POST'], website=True)
    def index_sale_bannerfetching(self, data=None, **kw):
        if data !='null':
            qr_order = request.env['sale.order'].sudo().search([('id','=',data),('order_line.order_line_state', 'not in', ['cancel', 'return', 'done', 'delivering'])], limit=1)
            if qr_order.date_order:
                if qr_order.state in ['sale']:
                    res_config_settings = request.env['ir.config_parameter'].sudo()
                    busy_banner_display = res_config_settings.get_param('busy_banner.busy_banner_display')
                    pos_order_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(busy_banner_display) * 60, 60))
                    pos_kitchen_pre_order_time = datetime.strptime(pos_order_time, '%H:%M').time()
                    pos_tot_secs = (pos_kitchen_pre_order_time.hour * 60 + pos_kitchen_pre_order_time.minute) * 60 + pos_kitchen_pre_order_time.second
                    pos_min_kitchen_display_time = pos_tot_secs / 60
                    tz = pytz.timezone(qr_order.company_id.tz or 'UTC')
                    estimation = qr_order.date_order.astimezone(tz) + timedelta(hours=0, minutes=pos_min_kitchen_display_time)
                    banner_title = res_config_settings.get_param('busy_banner.banner_title')
                    banner_body = res_config_settings.get_param('busy_banner.banner_body')
                    return {
                    'estimation': estimation,'banner_title': banner_title, 'banner_body': banner_body,'status':qr_order.state
                    }
                else:
                    return False
            else:
                return {
                    'process_kill': True,
                }
