# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError
from odoo.http import Controller, dispatch_rpc, request, route
import json
import hmac
import hashlib
import base64
# h = hmac.new( key, my, hashlib.sha256 )
# print( h.hexdigest() )
import hashlib
import hmac

class WebhookURLSWeb(Controller):

    @route(['/hubster/webhook'], type='json', auth="public", website=True, method=['POST'])
    def WooshWebhookApis(self, **kw):
        data = request.httprequest.data
        data = json.loads(data)
        info_order = data
        _logger.info('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww %s', info_order)
        hubster = request.env['hubster.order']
        hubster_line = request.env['hubster.order.line']
        partner = request.env['res.partner']
        payload = info_order.get('metadata')['payload']
        line_ids = []
        sale_line_ids = []
        if info_order:
            for line in payload.get('items'):
                dicts = {
                    'sku_price': line['skuPrice'],
                    'product_id': int(line['id']),
                    'name': line['name'],
                    'qty': int(line['quantity']),
                    'note': line['note'],
                    'base_price': line['price'],
                    'category': int(line['categoryId']),
                }

                lines = hubster_line.sudo().create(dicts)
                line_ids.append(lines.id)
                if line.get('modifiers',False):
                    for opt in line.get('modifiers'):
                        product=  request.env['product.product'].sudo().search([('product_tmpl_id','=',int(opt.get('id')))],limit=1)
                        pro = {
                            'sku_price': opt['skuPrice'],
                            'product_id': product.id,
                            'name': opt['name'],
                            'qty': int(opt['quantity']),
                            'base_price': opt['price'],
                        }
                        lines = hubster_line.sudo().create(pro)
                        line_ids.append(lines.id)
            val ={
                "event_id": info_order.get('eventId'),
                "event_time": info_order.get('eventTime'),
                "event_type": info_order.get('eventType'),
                "external_identifiers": payload.get('externalIdentifiers'),
                "source": payload.get('externalIdentifiers').get('source'),
                "friendly_id": payload.get('externalIdentifiers').get('friendlyId'),
                "ordered_at": payload.get('orderedAt'),
                "currency_code": payload.get('currencyCode'),
                "customer": payload.get('customer'),
                "customer_note": payload.get('customerNote'),
                "status": payload.get('status'),
                "delivery_info": payload.get('deliveryInfo'),
                'order_line': [(6, 0, line_ids)],
                'subtotal': payload.get('orderTotal').get('subtotal'),
                'discount': payload.get('orderTotal').get('discount'),
                'tax': payload.get('orderTotal').get('tax'),
                'deliveryFee': payload.get('orderTotal').get('deliveryFee'),
                'total': payload.get('orderTotal').get('total')
            }
            hubster_order = hubster.sudo().create(val)
            partners = False
            if payload.get('customer'):
                partners = partner.sudo().create({
                                'name': payload.get('customer')['name'],
                                'phone': payload.get('customer')['phone'],
                                'email': payload.get('customer')['email']
                            })
                hubster_order.sudo().write({
                    'partner': partners.id,
                })

            if hubster_order and partners:
                line_sales = []
                sale = request.env['sale.order']
                sale_line = request.env['sale.order.line']
                _logger.info('ttttttttttttttttttttttttt %s', partners)
                vals = {
                    'partner_id': hubster_order.partner.id,
                    'partner_invoice_id': hubster_order.partner.id,
                    'partner_shipping_id': hubster_order.partner.id,
                    'amount_untaxed': hubster_order.subtotal,
                    'amount_tax': hubster_order.tax,
                    'amount_total': hubster_order.total,
                    # 'order_id': [(6, 0, line_sales)],
                    'pricelist_id': 1,
                    'company_id': 1,
                    'is_hubster': True,
                    'friendly_id': hubster_order.source +"#"+hubster_order.friendly_id,
                }
                obj = sale.sudo().create(vals)
                hubster_order.write({
                    'source_document': obj.id,
                })

                _logger.info('rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr %s', obj)

                for line in payload.get('items'):
                    main_line = {
                        'product_id': int(line['id']),
                        'name': line['name'],
                        'product_uom_qty': int(line['quantity']),
                        'order_line_note': line['note'],
                        'price_unit': line['price'],
                        'order_id': obj.id,
                    }

                    s_lines = sale_line.sudo().create(main_line)
                    line_sales.append(s_lines.id)
                    optional_line = []
                    if line.get('modifiers', False):
                        for opt in line.get('modifiers'):
                            product = request.env['product.product'].sudo().search(
                                [('product_tmpl_id', '=', int(opt.get('id')))], limit=1)
                            pro = {
                                'product_id': product.id,
                                'name': opt['name'],
                                'product_uom_qty': int(opt['quantity']),
                                'price_unit': opt['price'],
                                'order_id': obj.id,
                            }
                            lines = sale_line.sudo().create(pro)
                            optional_line.append(lines.id)
                    s_lines.option_line_ids = [(6, 0, optional_line)]
                # for line in hubster_order.order_line:
                #     if line:
                #         sale_dict = {
                #             'product_id': line.product_id.id,
                #             'product_uom_qty': line.qty,
                #             'price_unit': line.base_price,
                #             'order_line_note': line.note,
                #             'order_id': obj.id,
                #         }
                #         line = sale_line.sudo().create(sale_dict)
                #         line_sales.append(line.id)
                if obj:
                    obj.action_confirm()




        # {'eventId': '122e0163-a290-428a-9605-b6950de7fdc0', 'eventTime': '2021-11-01T16:38:37Z',
        #  'eventType': 'orders.new_order',
        #  'metadata': {'storeId': 'HUB_STORE_1', 'applicationId': '735c2965-d331-4d07-ae5c-3c84f1452ad5',
        #               'resourceId': None, 'payload': {
        #          'externalIdentifiers': {'id': '8fc7b48a-5b43-4cd5-9044-ce31533f1486', 'friendlyId': '5',
        #                                  'source': 'phone'},
        #          'items': [
        #              {'skuPrice': 18.95, 'id': '963', 'name': 'Smash Hit Burger', 'quantity': 2, 'note': None,
        #               'categoryId': '62', 'categoryName': None, 'price': 18.95, 'modifiers': None}],
        #          'orderedAt': '2021-11-01T16:38:33Z', 'currencyCode': 'USD', 'customer': None, 'customerNote': None,
        #          'status': 'CONFIRMED', 'deliveryInfo': None,
        #          'orderTotal': {'subtotal': 37.9, 'claimedSubtotal': 37.9, 'discount': 0, 'tax': 0, 'tip': 0,
        #                         'deliveryFee': 0, 'total': 37.9, 'couponCode': None},
        #          'customerPayments': [{'value': 37.9, 'processingStatus': 'PROCESSED', 'paymentMethod': 'CARD'}],
        #          'fulfillmentInfo': {'pickupTime': None, 'deliveryTime': None, 'fulfillmentMode': 'PICKUP',
        #                              'schedulingType': 'ASAP', 'courierStatus': None}}, 'resourceHref': None}}

        # {"eventId": "e8ed3cea-ad1b-48e0-adfe-7734443d5246", "eventTime": "2021-10-12T04:58:23Z",
        #  "eventType": "orders.new_order",
        #  "metadata": {"storeId": "HUB_STORE_1",
        #               "applicationId": "735c2965-d331-4d07-ae5c-3c84f1452ad5",
        #               "resourceId": null,
        #               "payload": {
        #                      "externalIdentifiers": {"id": "e368d797-4507-43df-bc10-302b208267f8", "friendlyId": "5","source": "phone"},
        #                      "items": [
        #                          {"skuPrice": 13.95, "id": "587", "name": "On It Burger", "quantity": 1, "note": null,
        #                           "categoryId": "62", "categoryName": null, "price": 13.95, "modifiers": null}
        #                      ],
        #                      "orderedAt": "2021-10-12T04:58:21Z", "currencyCode": "USD", "customer": {
                                                    # "name": "Jane Doe",
                                                    # "phone": "+1-555-555-5555",
                                                    # "email": "email@email.com",
                                                    # "personalIdentifiers": {
                                                    # "taxIdentificationNumber": "01234567890"
                                                    # }, "customerNote": null,
        #                      "status": "CONFIRMED", "deliveryInfo": null,
        #                      "orderTotal": {"subtotal": 13.95, "claimedSubtotal": 13.95, "discount": 0, "tax": 0, "tip": 0,
        #                                     "deliveryFee": 0, "total": 13.95, "couponCode": null},
        #                      "customerPayments": [{"value": 13.95, "processingStatus": "PROCESSED", "paymentMethod": "CARD"}],
        #                      "fulfillmentInfo": {"pickupTime": null, "deliveryTime": null, "fulfillmentMode": "PICKUP",
        #                              "schedulingType": "ASAP", "courierStatus": null}}, "resourceHref": null}
        #  }


        return True
    
    
    @route(['/hubster/webhook/status'], type='json', auth="public", website=True, method=['POST'])
    def WooshWebhookStatus(self, **kw):
        data = request.httprequest.data
        data = json.loads(data)
        info_order = data
        _logger.info('sssssssssssssssssssssssssssssssssssssssssssssss %s', info_order)
        return True
    
    @route(['/hubster/webhook/cancel'], type='json', auth="public", website=True, method=['POST'])
    def WooshWebhookCancel(self, **kw):
        data = request.httprequest.data
        data = json.loads(data)
        info_order = data
        _logger.info('ccccccccccccccccccccccc %s', info_order)
        return True


