from odoo.fields import Datetime
from odoo.http import request
from odoo import http
import json
import logging
_logger = logging.getLogger(__name__)
import requests
import logging
import base64
import werkzeug
from odoo.tools import safe_eval, html_escape

_logger = logging.getLogger(__name__)
from datetime import timedelta
from odoo.http import request

class rf_id_api(http.Controller):

    @http.route('/rf/info', methods=['POST','GET'], auth='none', csrf=False, type="json")
    def rfcontainer(self, **kwargs):
        try:
            info = []
            container = request.env['rfid.container'].sudo().search([])
            for i in container:
                lp = []
                for j in i.product_ids:
                    c= {
                        'product_id': j.product_id or False,
                        'rfid_code': j.rfid_code or False,
                        'product_weight': j.product_weight or False,
                        'dynamic_ip': j.dynamic_ip or False,
                        'id': j.id
                    }
                    lp.append(c)
                dict = {
                    'name': i.name,
                    'barcode': i.barcode or False,
                    'weight': i.weight or False,
                    'ssid': i.ssid or False,
                    'password': i.password or False,
                    'lp': lp,
                    'id': i.id
                }
                info.append(dict)
            data = {'status': 1, 'info': info}
            return data
        except:
            data1 = {'status': 0}
            return data1

    @http.route('/rf/write', methods=['POST','GET'], auth='none', csrf=False, type="json")
    def rfcontainer_ip_write(self, **kwargs):
        try:
            info = request.jsonrequest
            rf_line_id = info.get('id')
            ip_address = info.get('ip_address')
            if rf_line_id:
                container = request.env['rfid.container.line'].sudo().search([('id','=',int(rf_line_id))])
                container.sudo().write({
                    'dynamic_ip': ip_address
                })
                data = {'status': 1}
                return data
        except:
            data1 = {'status': 0}
            return data1

    @http.route("/rf/status", methods=['POST'], csrf=False, type="json", auth="none")
    def rfstatus_ip_write(self, **kwargs):
        try:
            info = request.jsonrequest
            rf_line_id = info.get('id')
            status = info.get('status')
            if rf_line_id:
                container = request.env['rfid.container.line'].sudo().search([('id','=',int(rf_line_id))])
                container.sudo().write({
                    'status': status
                })
                data = {'status': 1}
                return data
        except:
            data1 = {'status': 0}
            return data1