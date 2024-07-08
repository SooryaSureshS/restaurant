from odoo import api, fields, models, _, tools
import json
import logging

from odoo import http
from odoo.http import request
_logger = logging.getLogger(__name__)

import requests
class UberEats(http.Controller):

    #webhook url

    # uber doc : https://developer.uber.com/docs/eats/guides/order-integration

    # once order is created in uber will trigger event from uber  (event_type) will trigger the api(webhook url)
    # then trigger this api to get an order from uber https://api.uber.com/v2/eats/order/{order_id}
    #once order created we accept and deny the order by using https://api.uber.com/v1/eats/orders/{order_id}/accept_pos_order
    # and https://api.uber.com/v1/eats/orders/{order_id}/deny_pos_order

    @http.route('/uber/orders', auth='public', type='http')
    def uber_orders(self,**kwargs):
        event = kwargs
        response=self.uber_login()
        if response:
            order_api = 'https://api.uber.com/v2/eats/order/'+str(event.get('order_id'))
            headers = {'Content-Type': 'application/json','Authorization': 'Bearer {}'.format(response.get('access_token'))}
            response = requests.post(order_api,headers=headers)
            _logger.info(response)
            _logger.info(response.content)

        return 'ok'

    def uber_login(self):
        api = 'https://login.uber.com/oauth/v2/token'
        uber_record = self.env.ref('uber_eats_pos.uber_record')
        if uber_record:

            data = {'client_secret':uber_record.client_secret,'client_id':uber_record.client_id,'scope':'eats.order'
                    ,'grant_type':'client_credentials'}
            try:
                response = requests.post(api,data=data)
                return response.content
            except Exception as e:

                _logger.info("uber authentication failed",e)
                return False
        else:
            return False


