from odoo import models, fields, _
import requests
import json


class DeliverCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('shipany', 'ShipAny')],
                                     ondelete={'shipany': lambda recs: recs.write({
                                         'delivery_type': 'fixed', 'fixed_price': 0,
                                     })})
    max_weight = fields.Float("Max weight", default=20, readonly=True)
    shipany_api_key = fields.Char("API Key", help="Enter your API key from ShipAny account.")
    shipany_endpoint = fields.Char("End Point", help="Enter your Endpoint.")
    shipany_label_file_type = fields.Selection([
        ('PNG', 'PNG'), ('PDF', 'PDF'),
        ('ZPL', 'ZPL'), ('EPL2', 'EPL2')],
        string="ShipAny Label File Type", default='PDF')
    shipany_delivery_type = fields.Many2one('shipany.carrier', readonly=True, string="Carrier Category")
    shipany_default_packaging_id = fields.Many2one('product.packaging', string="Default Packaging type")
    merchant_name = fields.Char(string="Merchant name")
    merchant_uid = fields.Char(string="Merchant UID")

    # To get list of carriers
    def action_get_shipany_carrier_type(self):
        headers = {
            'api-tk': self.shipany_api_key
        }
        end_point = "%s" % self.shipany_endpoint + 'couriers'
        response = requests.get(end_point, headers=headers)
        result = json.loads(response.content.decode('utf-8'))
        for data in result['data']['objects']:
            if data.get('uid') and data.get('name'):
                try:
                    max_weight = data['cour_props']['delivery_services']['cour_svc_plans'][0]['wt_dim_restrictions'][
                        'max_weight']
                except:
                    max_weight = 20
                self.max_weight = max_weight
                vals = {
                    'name': data.get('name'),
                    'carrier_uid': data.get('uid')
                }
                shipcarrier_obj = self.env['shipany.carrier'].search([('carrier_uid', '=', data.get('uid'))])
                if not shipcarrier_obj:
                    carrier_obj = self.env['shipany.carrier'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'name': ('Carrier'),
            'res_model': 'delivery.carrier.shipany',
            'view_mode': 'form',
            'target': 'new',
            'context': {'delivery_carrier_id': self.id}

        }

    # To get list of merchants
    def action_get_merchant_info(self):
        headers = {
            'api-tk': self.shipany_api_key
        }
        end_point = "%s" % self.shipany_endpoint + 'merchants/self/'
        response = requests.get(end_point, headers=headers)
        result = json.loads(response.content.decode('utf-8'))
        for data in result['data']['objects']:
            for info in data.get('co_info').get('org_ctcs'):
                vals = {
                    'merchant_name': info.get('ctc').get('f_name')
                }
                self.write(vals)
            if data.get('uid') and data.get('name'):
                vals = {
                    'merchant_uid': data.get('uid')
                }
                self.write(vals)

    def shipany_rate_shipment(self, order):
        results = order.ship_any_get_val(order, self.id)
        price = 0
        if results:
            for ordNum in results:
                for data in results[ordNum]['data']['objects']:
                    for j in data.get('quots'):
                        if j.get('cour_uid') == self.shipany_delivery_type.carrier_uid:
                            price += j.get('cour_ttl_cost')['val']
            return {'success': True,
                    'price': price,
                    'error_message': False,
                    'warning_message': False}
        else:
            return {'success': False,
                    'price': 0.0,
                    'error_message': _("Error: Couldn't get the shipping rate."),
                    'warning_message': True}
