from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    carrier_quots_uid = fields.Char(string="Carrier Quots UID")
    courier_quot_uid = fields.Char(string="Courier Quot UID")
    courier_uid = fields.Char(string="Courier UID", copy=False)
    courier_type = fields.Char(string="Courier Type", copy=False)
    ship_amount = fields.Char(string="Ship amount", copy=False)
    courier_plan = fields.Char(string="Courier Plan")
    shipany_delivery_method = fields.Selection(
        [('pickup', 'PickUp'), ('std_delivery', 'Standard Delivery'), ('locker', 'Locker')], string="Destination",
        default=False)
    shipany_delivery_address = fields.Text(string="Delivery Address")
    shipany_locker_no = fields.Many2one('delivery.carrier', string="Delivery Method", related='carrier_id')
    shipany_locker = fields.Char(string="Locker Number")

    # inherited this function to Get Rate from ShipAny
    # Get Rate
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.carrier_id:
            carrier_id = self.carrier_id.id
            delivery_type = self.get_delivery_type(self.carrier_id.id)
            if delivery_type == 'shipany':
                order = self
                flag = False
                total_cost = 0
                carrier_quots_uid = ''
                courier_quot_uid = ''
                courier_uid = ''
                courier_type = ''
                courier_plan = ''
                results = self.ship_any_get_val(order, carrier_id)
                for ordNum in results:
                    for data in results[ordNum]['data']['objects']:
                        for j in data.get('quots'):
                            if j.get('cour_uid') == self.carrier_id.shipany_delivery_type.carrier_uid and not flag:
                                flag = True
                                total_cost += j.get('cour_ttl_cost')['val']
                                carrier_quots_uid = data.get('quots_uid')
                                courier_quot_uid = j.get('quot_uid')
                                courier_uid = j.get('cour_uid')
                                courier_type = j.get('cour_type')
                                courier_plan = j.get('cour_svc_pl')
                if flag:
                    vals = {
                        'carrier_quots_uid': carrier_quots_uid,
                        'courier_quot_uid': courier_quot_uid,
                        'courier_uid': courier_uid,
                        'courier_type': courier_type,
                        'ship_amount': total_cost,
                        'courier_plan': courier_plan
                    }
                    self.write(vals)
                    line_vals = {
                        'product_id': self.carrier_id.product_id.id,
                        'product_uom_qty': 1,
                        'name': self.carrier_id.product_id.name,
                        'price_unit': total_cost,
                        'order_id': self.id,
                        'is_delivery': True,
                    }
                    taxes = map(lambda a: a.id, self.carrier_id.product_id.taxes_id)
                    line_obj = self.order_line.filtered(lambda line: line.is_delivery)
                    if not line_obj:
                        new_line_obj = self.order_line.sudo().create(line_vals)
                        if taxes:
                            new_line_obj.sudo().update({'tax_id': [(6, 0, taxes)]})
                    else:
                        line_obj.write(line_vals)
                        if taxes:
                            line_obj.sudo().update({'tax_id': [(6, 0, taxes)]})

            else:
                if self.order_line:
                    value = self.carrier_id.rate_shipment(res)
                    if value.get('success'):
                        line_vals = {
                            'product_id': self.carrier_id.product_id.id,
                            'product_uom_qty': 1,
                            'name': self.carrier_id.product_id.name,
                            'price_unit': value['price'],
                            'order_id': self.id,
                        }
                        taxes = map(lambda a: a.id, self.carrier_id.product_id.taxes_id)
                        line_obj = self.order_line.filtered(lambda r: r.product_id == self.carrier_id.product_id.id)
                        if not line_obj:
                            new_line_obj = self.order_line.sudo().create(line_vals)
                            if taxes:
                                new_line_obj.sudo().update({'tax_id': [(6, 0, taxes)]})
                        else:
                            line_obj.unlink()
                            new_line_obj = self.order_line.sudo().create(line_vals)
                            if taxes:
                                new_line_obj.sudo().update({'tax_id': [(6, 0, taxes)]})
        if self.picking_ids:
            for i in self.picking_ids:
                vals = {
                    'shipany_delivery_method': self.shipany_delivery_method,
                    'shipany_delivery_address': self.shipany_delivery_address if self.shipany_delivery_address else "",
                    'shipany_locker_no': self.shipany_locker_no,
                    'shipany_locker': self.shipany_locker
                }
                i.write(vals)
        return res

    def get_delivery_type(self, delivery_id):
        del_obj = self.env['delivery.carrier'].sudo().search_read(
            domain=[('id', '=', delivery_id)],
            fields=['delivery_type'])
        if del_obj:
            for data in del_obj:
                delivery_type = data.get('delivery_type')
            return delivery_type

    def create_ship_any_vals(self, order, carrier):
        max_weight = carrier.max_weight
        line_details = []
        total_weight = 0
        amount_total = 0
        if order.order_line:
            orders = dict()
            order_no = 1
            for line in order.order_line:
                if line.product_id.detailed_type != 'service':
                    total_weight_temp = total_weight + (line.product_id.shipping_weight * line.product_uom_qty)/1000
                    amount_total_temp = amount_total + (line.price_unit * line.product_uom_qty)
                    # when total weight exceeds max_weight
                    if total_weight_temp > max_weight:
                        line_details = []
                        if (line.product_id.shipping_weight * line.product_uom_qty)/1000 > max_weight:
                            rem_qty = line.product_uom_qty
                            min_qty = max_weight//(line.product_id.shipping_weight/1000)
                            while rem_qty > min_qty:
                                line_details = []
                                order_no += 1
                                rem_qty = rem_qty - min_qty
                                send_qty = min_qty
                                total_weight = (line.product_id.shipping_weight * send_qty)/1000
                                amount_total = send_qty * line.price_unit
                                self.weight_limited_order_setup(line, send_qty, order, line_details, orders, order_no, total_weight, amount_total)
                            order_no += 1
                            line_details = []
                            send_qty = rem_qty
                            total_weight = (line.product_id.shipping_weight * send_qty)/1000
                            self.weight_limited_order_setup(line, send_qty, order, line_details, orders, order_no, total_weight, amount_total)
                        else:
                            order_no += 1
                            total_weight = (line.product_id.shipping_weight * line.product_uom_qty)/1000
                            amount_total = line.product_uom_qty * line.price_unit
                            self.weight_limited_order_setup(line, line.product_uom_qty, order, line_details, orders, order_no, total_weight, amount_total)
                    else:
                        total_weight = total_weight_temp
                        amount_total = amount_total_temp
                        self.weight_limited_order_setup(line, line.product_uom_qty, order, line_details, orders, order_no, total_weight, amount_total)
            return orders, total_weight

    def weight_limited_order_setup(self, line, send_qty, order, line_details, orders, order_no, total_weight, amount_total):
        values_to_send = {
            "sku": line.product_id.default_code if line.product_id.default_code else "",
            "name": line.product_id.name,
            "typ": line.product_id.detailed_type if line.product_id.detailed_type else "",
            "descr": line.name,
            "ori": "HKG",
            "unt_price": {"val": line.price_unit,
                          "ccy": order.currency_id.name if order.currency_id.name else ""},
            "qty": send_qty,
            "wt": {"val": (line.product_id.shipping_weight * send_qty)/1000 if line.product_id.shipping_weight else 1},
            "dim": {"len": 0,
                    "wid": 0,
                    "hgt": 0},
            "stg": "Normal"
        }
        line_details.append(values_to_send)

        orders[order_no] = {
            'wt': {"val": total_weight if total_weight > 0 else 1},
            'dim': {"len": 1, "wid": 1, "hgt": 1},
            'items': line_details,
            'mch_ttl_val': {"val": amount_total,
                            "ccy": order.currency_id.name if order.currency_id.name else ""},
            'sndr_ctc': {
                'ctc': {
                    'fname': order.company_id.partner_id.first_name if order.company_id.partner_id.first_name else "",
                    'l_name': order.company_id.partner_id.last_name if order.company_id.partner_id.last_name else "",
                    'phs': [{
                        'typ': 'Work',
                        "cnty_code": order.company_id.partner_id.country_id.code if order.company_id.partner_id.country_id.code else "",
                        "ar_code": "",
                        "num": order.company_id.partner_id.phone if order.company_id.partner_id.phone else "",
                        "ext_no": ""
                    }],
                    "email": order.company_id.partner_id.email if order.company_id.partner_id.email else "",
                    "note": "",
                },
                "addr": {
                    "typ": "Business",
                    "ln": order.company_id.partner_id.street if order.company_id.partner_id.street else "",
                    "ln2": order.company_id.partner_id.street2 if order.company_id.partner_id.street2 else "",
                    "ln3": "",
                    "distr": "",
                    "city": order.company_id.partner_id.city if order.company_id.partner_id.city else "",
                    "state": order.company_id.partner_id.state_id.name if order.company_id.partner_id.state_id else "",
                    "cnty": order.company_id.partner_id.country_id.name if order.company_id.partner_id.country_id else "",
                    "zc": order.company_id.partner_id.zip if order.company_id.partner_id.zip else ""
                }
            },
            'rcvr_ctc': {
                'ctc': {
                    'fname': order.partner_shipping_id.first_name if order.partner_shipping_id.first_name else "",
                    'l_name': order.partner_shipping_id.last_name if order.partner_shipping_id.last_name else "",
                    'phs': [{
                        'typ': 'Work',
                        "cnty_code": order.partner_shipping_id.country_id.code if order.partner_shipping_id.country_id else "",
                        "ar_code": "",
                        "num": order.partner_shipping_id.phone if order.partner_shipping_id.phone else "",
                        "ext_no": ""
                    }],
                    "email": order.partner_shipping_id.email if order.partner_shipping_id.email else "",
                    "note": "",
                },
                "addr": {
                    "typ": "Business",
                    "ln": order.partner_shipping_id.street if order.partner_shipping_id.street else "",
                    "ln2": order.partner_shipping_id.street2 if order.partner_shipping_id.street2 else "",
                    "ln3": "",
                    "distr": "",
                    "city": order.partner_shipping_id.city if order.partner_shipping_id.city else "",
                    "state": order.partner_shipping_id.state_id.name if order.partner_shipping_id.state_id else "",
                    "cnty": order.partner_shipping_id.country_id.name if order.partner_shipping_id.country_id else "",
                    "zc": order.partner_shipping_id.zip if order.partner_shipping_id.zip else ""
                }
            }
        }

    def ship_any_get_val(self, order, carrier_id):
        carrier = self.env['delivery.carrier'].search([('id', '=', carrier_id)])
        created_vals = order.create_ship_any_vals(order, carrier)
        vals = created_vals[0]
        headers = {
            'api-tk': carrier.shipany_api_key
        }
        for ordNum in vals:
            order_json = json.dumps(vals[ordNum])
            end_point = "%s" % carrier.shipany_endpoint + 'couriers-connector/query-rate/'
            response = requests.post(end_point, headers=headers, data=order_json)
            vals[ordNum] = json.loads(response.content.decode('utf-8'))
        return vals

    def _check_carrier_quotation(self, force_carrier_id=None):
        res = super(SaleOrder, self)._check_carrier_quotation()
        carrier_id = force_carrier_id
        if force_carrier_id:
            if self.get_delivery_type(force_carrier_id) == 'shipany':
                order = self
                cost = self.get_ship_any_price(order, carrier_id)
                if cost:
                    order.set_delivery_lines(order, carrier_id, cost)
                    order.delivery_rating_success = True
                    return res
            else:
                return res

    def set_delivery_lines(self, order, carrier_id, cost):
        order._remove_delivery_line()
        carrier = self.env['delivery.carrier'].search([('id', '=', carrier_id)])
        for order in order:
            order.carrier_id = carrier_id
            order._create_delivery_line(carrier, cost)
        return True

    def get_ship_any_price(self, order, carrier_id):
        results = self.ship_any_get_val(order, carrier_id)
        carrier = self.env['delivery.carrier'].search([('id', '=', carrier_id)])
        cost = 0
        for ordNum in results:
            for data in results[ordNum]['data']['objects']:
                for j in data.get('quots'):
                    if j.get('cour_uid') == carrier.shipany_delivery_type.carrier_uid:
                        price = j.get('cour_ttl_cost')
                        cost += price['val']
        return cost
