from odoo import models, fields, _
import requests
import json
import logging
import base64

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    shipany_delivery_method = fields.Selection(
        [('pickup', 'PickUp'), ('std_delivery', 'Standard Delivery'), ('locker', 'Locker')], string="Destination",
        default=False)
    shipany_delivery_address = fields.Text(string="Delivery Address")
    shipany_locker_no = fields.Many2one('delivery.carrier', string="Delivery Method")
    shipany_order_id = fields.Char(string="ShipAny Order ID")
    shipany_waybill_url = fields.Char(string="Waybill URL")
    shipany_locker = fields.Char(string="Locker Number")
    carrier_tracking_ref = fields.Char(string="Tracking number")
    shipany_tracking_url = fields.Char(string="shipany Tracking Url")
    carrier_tracking_url = fields.Char(string="Carrier tracking url")

    # Create Shipany Order
    def action_create_shipany_order(self):

        line_details = []
        if self.sale_id.courier_uid:
            for data in self.move_ids_without_package:
                sale_line = self.sale_id.order_line.filtered(lambda r: r.product_id.id == data.product_id.id)
                value = {
                    'sku': sale_line.product_id.default_code,
                    'name': sale_line.product_id.name,
                    # 'stg': sale_line.product_id.detailed_type,
                    'descr': sale_line.name,
                    'ori': "HKG",
                    'unt_price': {"val": sale_line.price_unit, "ccy": "HKD"},
                    'qty': sale_line.product_uom_qty,
                    'wt': {"val": sale_line.product_id.weight, "unt": "kg"},
                    'dim': {"len": 0, "wid": 0, "hgt": 0, "unt": "cm"},
                    'cbm': 0,
                    'stg': "Normal"
                }
                line_details.append(value)
                values = {
                    'mch_order_id': "",
                    'cl_order_id': "",
                    'cour_uid': self.sale_id.courier_uid,
                    'mch_uid': self.carrier_id.merchant_uid,
                    'ext_mch_id': "",
                    'quots_uid': self.sale_id.carrier_quots_uid,
                    'quot_uid': self.sale_id.courier_quot_uid,
                    'cour_type': self.sale_id.courier_type,
                    'ext_order_ref': self.sale_id.name,
                    'wt': {"val": self.weight, "unt": "kg"},
                    'dim': {"len": 0, "wid": 0, "hgt": 0, "unt": "cm"},
                    'items': line_details,
                    'mch_ttl_val': {"val": self.sale_id.amount_total,
                                    "ccy": self.sale_id.currency_id.name if self.sale_id.currency_id.name else ""},
                    'cour_ttl_cost': {"val": self.sale_id.ship_amount if self.sale_id.ship_amount else 0,
                                      "ccy": self.sale_id.currency_id.name if self.sale_id.currency_id.name else ""},
                    'cour_svc_pl': self.sale_id.courier_plan,
                    'sndr_ctc': {
                        'ctc': {
                            'fname': self.sale_id.company_id.partner_id.name if self.sale_id.company_id.partner_id.name else "",
                            'l_name': "",
                            'phs': [{
                                'typ': 'Work',
                                "cnty_code": self.sale_id.company_id.partner_id.country_id.code if self.sale_id.company_id.partner_id.country_id.code else "",
                                "ar_code": "",
                                "num": self.sale_id.company_id.partner_id.phone if self.sale_id.company_id.partner_id.phone else "",
                                "ext_no": ""
                            }],
                            "email": self.sale_id.company_id.partner_id.email if self.sale_id.company_id.partner_id.email else "",
                            "note": "",
                        },
                        "addr":
                            {"typ": "Store",
                             "ln": self.sale_id.company_id.partner_id.street if self.sale_id.company_id.partner_id.street else "",
                             "ln2": self.sale_id.company_id.partner_id.street2 if self.sale_id.company_id.partner_id.street2 else "",
                             "ln3": "",
                             "distr": "",
                             "city": self.sale_id.company_id.partner_id.city if self.sale_id.company_id.partner_id.city else "",
                             "state": self.sale_id.company_id.partner_id.state_id.name if self.sale_id.company_id.partner_id.state_id.name else "",
                             "cnty": self.sale_id.company_id.partner_id.country_id.name if self.sale_id.company_id.partner_id.country_id.name else "",
                             "zc": self.sale_id.company_id.partner_id.zip if self.sale_id.company_id.partner_id.zip else ""
                             }
                    },
                    'rcvr_ctc': {
                        'ctc': {
                            'fname': self.sale_id.partner_shipping_id.name if self.sale_id.partner_shipping_id.name else "",
                            'l_name': "",
                            'phs': [{
                                'typ': 'Work',
                                "cnty_code": self.sale_id.partner_shipping_id.country_id.code if self.sale_id.partner_shipping_id.country_id.code else "",
                                "ar_code": "",
                                "num": self.sale_id.partner_shipping_id.phone if self.sale_id.partner_shipping_id.phone else "",
                                "ext_no": ""
                            }],
                            "email": self.sale_id.partner_shipping_id.email if self.sale_id.partner_shipping_id.email else "",
                            "note": "",
                        },
                        "addr":
                            {"typ": "Store",
                             "ln": self.sale_id.partner_shipping_id.street if self.sale_id.partner_shipping_id.street else "",
                             "ln2": self.sale_id.partner_shipping_id.street if self.sale_id.partner_shipping_id.street else "",
                             "ln3": "",
                             "distr": "",
                             "city": self.sale_id.partner_shipping_id.city if self.sale_id.partner_shipping_id.city else "",
                             "state": self.sale_id.partner_shipping_id.state_id.name if self.sale_id.partner_shipping_id.state_id.name else "",
                             "cnty": self.sale_id.partner_shipping_id.country_id.name if self.sale_id.partner_shipping_id.country_id.name else "",
                             "zc": self.sale_id.partner_shipping_id.zip if self.sale_id.partner_shipping_id.zip else ""
                             }
                    },
                }
                headers = {
                    'api-tk': self.carrier_id.shipany_api_key
                }
                order_json = json.dumps(values)
                end_point = "%s" % self.carrier_id.shipany_endpoint + 'orders/'
                response = requests.post(end_point, headers=headers, data=order_json)
                result = json.loads(response.content.decode('utf-8'))
                _logger.info("*******result")
                _logger.info(response.status_code)
                if result['result']:
                    result_response = result['result']
                    if result_response['code'] == 201:
                        for j in result['data']['objects']:
                            if j.get('uid') and j.get('trk_no'):
                                vals = {
                                    'shipany_order_id': j.get('uid'),
                                    'carrier_tracking_ref': j.get('trk_no'),
                                    'shipany_waybill_url': j.get('lab_url'),
                                    'shipany_tracking_url': j.get('shipany_trk_url'),
                                    'carrier_tracking_url': j.get('trk_url'),
                                    'has_tracking': True,
                                }
                                self.write(vals)

    # Get service Locations
    def get_service_locations(self):
        stock_obj = self.env['stock.picking'].search([('carrier_id', '!=', None)])
        for data in stock_obj:
            if data.carrier_id.shipany_endpoint and data.carrier_id.shipany_api_key:
                headers = {
                    'api-tk': data.carrier_id.shipany_api_key
                }
                end_point = "%s" % data.carrier_id.shipany_endpoint + 'courier-service-location/published-locations/'
                response = requests.get(end_point, headers=headers)
                result = json.loads(response.content.decode('utf-8'))
                if result['result']:
                    result_response = result['result']
                    if result_response['code'] == 200:
                        for datas in result['data']['objects']:
                            if datas.get('url'):
                                vals = {
                                    'url': datas.get('url'),
                                    'cour_type': datas.get('cour_type'),
                                    'cour_uid': datas.get('cour_uid'),
                                    'cour_name': datas.get('cour_name'),
                                    'stock_picking_id': data.id
                                }
                                service_obj = self.env['shipany.service.locations'].search(
                                    [('url', '=', datas.get('url'))])
                                if not service_obj:
                                    self.env['shipany.service.locations'].create(vals)

    # Get ShipAny Waybill
    def action_get_shipany_waybill(self):
        if self.shipany_waybill_url and self.carrier_tracking_ref:
            response = requests.get(self.shipany_waybill_url)
            obj = response.content
            myObj = [base64.b64encode(obj)]
            waybill = self.env["shipany.waybill"].create({
                 'stock_picking_id': self.id,
                 'waybill_url': self.shipany_waybill_url,
                 'shipany_trk_no': self.carrier_tracking_ref,
                 'waybill': myObj[0]})
            return {
                'type': 'ir.actions.act_window',
                'name': ('WayBill'),
                'res_model': 'shipany.waybill',
                'res_id': waybill.id,
                'view_mode': 'form',
                'target': 'new',
            }

    # Inherited parent function for shipany Specification
    def send_to_shipper(self):
        self.ensure_one()
        if self.carrier_id.delivery_type != 'shipany':
            res = self.carrier_id.send_shipping(self)[0]
            if self.carrier_id.free_over and self.sale_id and self.sale_id._compute_amount_total_without_delivery() >= self.carrier_id.amount:
                res['exact_price'] = 0.0
            self.carrier_price = res['exact_price'] * (1.0 + (self.carrier_id.margin / 100.0))
            if res['tracking_number']:
                self.carrier_tracking_ref = res['tracking_number']
            order_currency = self.sale_id.currency_id or self.company_id.currency_id
            msg = _("Shipment sent to carrier %s for shipping with tracking number %s<br/>Cost: %.2f %s") % (
                self.carrier_id.name, self.carrier_tracking_ref, self.carrier_price, order_currency.name)
            self.message_post(body=msg)
            self._add_delivery_cost_to_so()
