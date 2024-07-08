import json
from odoo.exceptions import ValidationError
from odoo import http
from odoo.http import request
from .payment_cybersource import CyberSourceAPI, CYBERSOURCE_RESPONSES
from odoo.addons.payment import utils as payment_utils
from .payment_encrypt import PaymentCardEncrypt


class PaymentTestController(http.Controller):

    @http.route('/payment/cyber/cybersource_payment', type='json', auth='public')
    def cybersource_payment(self, reference, cc_number, cc_holder_name, cc_expiry, cc_cvc, acquirer_id, csrf_token,
                            partner_id):
        self.validate_card_details(cc_number, cc_holder_name, cc_expiry, cc_cvc)
        acquirer = request.env['payment.acquirer'].sudo().search([('provider', '=', "cyber")])
        sale_order_id = int(request.session.get('sale_order_id'))
        order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
        sale_order_data = self.get_sale_order_data(sale_order_id)
        bill_to_data = self.get_bill_to_data(int(order.partner_id.id))
        card_data = self.get_card_data(
            {'cc_number': cc_number, 'cc_holder_name': cc_holder_name, 'cc_expiry': cc_expiry, 'cvNumber': cc_cvc,
             'cc_brand': ''})
        cybersource_cls = CyberSourceAPI(acquirer)
        cybersource_cls.create_headers()
        cybersource_cls.billing_info(bill_to_data)
        cybersource_cls.payment_amount(sale_order_data)
        cybersource_cls.set_card_info(card_data)
        response = cybersource_cls.cybersource_request()
        if response is None:
            raise ValidationError('An error occurred while processing the payment')

        data = json.loads(json.dumps(self.recursive_dict(response)))
        payment_response_data = CYBERSOURCE_RESPONSES.get(data.get('reasonCode'), 'Invalid Data')

        if data.get('reasonCode') in [100, 480]:
            api_response = {
                'reference': reference,
            }
        else:
            raise ValidationError(CYBERSOURCE_RESPONSES.get(data.get('reasonCode')))
        data = {'acquirer_id': acquirer.id, 'cc_number': cc_number, 'cc_holder_name': cc_holder_name, 'partner_id': order.partner_id.id,
                'acquirer_ref': response.get('requestID')}
        # self.create_payment_token(data)
        request.env['payment.transaction'].sudo()._handle_feedback_data('cyber', api_response)

    # @http.route('/payment/cyber/cybersource_payment', type='json', auth='public')
    # def cybersource_payment(self, reference, cc_number, cc_holder_name, cc_expiry, cc_cvc, acquirer_id, csrf_token,
    #                         partner_id, is_card_save, card_detail_id, use_saved_card):
    #     self.validate_card_details(cc_number, cc_holder_name, cc_expiry, cc_cvc)
    #     acquirer = request.env['payment.acquirer'].sudo().search([('provider', '=', "cyber")])
    #     sale_order_id = int(request.session.get('sale_order_id'))
    #     order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
    #     sale_order_data = self.get_sale_order_data(sale_order_id)
    #     bill_to_data = self.get_bill_to_data(int(order.partner_id.id))
    #     saved_card = None
    #     if is_card_save:
    #         saved_card = self.save_card_details(cc_number, cc_holder_name, cc_expiry, cc_cvc, acquirer,
    #                                             order.partner_id)
    #     if card_detail_id and use_saved_card:
    #         cc_number, cc_cvc, cc_expiry, cc_holder_name = self.get_saved_card_data(card_detail_id)
    #     card_data = self.get_card_data(
    #         {'cc_number': cc_number, 'cc_holder_name': cc_holder_name, 'cc_expiry': cc_expiry, 'cvNumber': cc_cvc,
    #          'cc_brand': ''})
    #     cybersource_cls = CyberSourceAPI(acquirer)
    #     cybersource_cls.create_headers()
    #     cybersource_cls.billing_info(bill_to_data)
    #     cybersource_cls.payment_amount(sale_order_data)
    #     cybersource_cls.set_card_info(card_data)
    #     response = cybersource_cls.cybersource_request()
    #     if response is None:
    #         raise ValidationError('An error occurred while processing the payment')
    #
    #     data = json.loads(json.dumps(self.recursive_dict(response)))
    #     payment_response_data = CYBERSOURCE_RESPONSES.get(data.get('reasonCode'), 'Invalid Data')
    #
    #     if data.get('reasonCode') in [100, 480]:
    #         api_response = {
    #             'reference': reference,
    #         }
    #         if is_card_save and saved_card is not None:
    #             saved_card_obj = request.env['payment.card.data'].sudo().search([('id', '=', saved_card)])
    #             saved_card_obj.verified = True
    #     else:
    #         raise ValidationError(CYBERSOURCE_RESPONSES.get(data.get('reasonCode')))
    #     data = {'acquirer_id': acquirer.id, 'cc_number': cc_number, 'cc_holder_name': cc_holder_name,
    #             'partner_id': order.partner_id.id,
    #             'acquirer_ref': response.get('requestID')}
    #     # self.create_payment_token(data)
    #     request.env['payment.transaction'].sudo()._handle_feedback_data('cyber', api_response)

    @staticmethod
    def get_saved_card_data(card_detail_id):
        saved_card_obj = request.env['payment.card.data'].sudo().search([('id', '=', card_detail_id)])
        encrypt_data = PaymentCardEncrypt(key=saved_card_obj.key)
        card_number = encrypt_data.get_decrypt_data(saved_card_obj.card_number)
        card_cvc = encrypt_data.get_decrypt_data(saved_card_obj.card_cvc)
        card_expiry = encrypt_data.get_decrypt_data(saved_card_obj.card_expiry)
        return card_number, card_cvc, card_expiry, saved_card_obj.card_holder_name

    @staticmethod
    def save_card_details(cc_number, cc_holder_name, cc_expiry, cc_cvc, acquirer, partner):
        generate_key = PaymentCardEncrypt(card_holder=cc_holder_name, cvv=cc_cvc, card_number=cc_number)
        generate_key.url_safe_base64_encoded_key()
        name = f"XXXX-XXXX-XXXX-X{cc_number[-3:]}"
        val = {'key': generate_key.key, 'card_number': generate_key.get_encrypted_string(cc_number),
               'card_cvc': generate_key.get_encrypted_string(cc_cvc),
               'card_expiry': generate_key.get_encrypted_string(cc_expiry), 'card_holder_name': cc_holder_name,
               'acquirer_id': acquirer.id, 'partner_id': partner.id, 'active': True, 'name': name,
               'acquirer_ref': 'cyber'}
        return request.env['payment.card.data'].sudo().create(val)


    @staticmethod
    def validate_card_details(cc_number, cc_holder_name, cc_expiry, cc_cvc):
        if not len(cc_cvc) or not len(cc_number) or not len(cc_holder_name) or not len(cc_expiry):
            raise ValidationError('Please Provide Card Details')

    def recursive_dict(self, d):
        out = {}
        for k, v in d.items():
            try:
                if hasattr(v, '__keylist__'):
                    out[k] = self.recursive_dict(v)
                elif isinstance(v, list):
                    out[k] = []
                    for item in v:
                        if hasattr(item, '__keylist__'):
                            out[k].append(self.recursive_dict(item))
                        else:
                            out[k].append(item)
            except:
                continue
            else:
                out[k] = v
        return out

    @staticmethod
    def get_sale_order_data(sale_order_id):
        sale_order = request.env['sale.order'].sudo().browse(sale_order_id)
        values = {
            'currency': sale_order.company_id.currency_id.name,
            'grandTotalAmount': sale_order.amount_total,
        }
        return values

    @staticmethod
    def get_bill_to_data(partner_id):
        partner = request.env['res.partner'].sudo().browse(partner_id)
        values = {
            'firstName': partner.name,
            'title': partner.title,
            'email': partner.email,
            'city': partner.city,
            'street': partner.street,
            'street2': partner.street2,
            'postalCode': partner.zip,
            'country': partner.country_id.name,
            'company': partner.company_id.name,
            'phone': partner.phone,
            'customer_id': partner.id
        }
        return values

    @staticmethod
    def get_card_data(card):
        values = {
            'fullName': card.get('cc_holder_name'),
            'accountNumber': card.get('cc_number'),
            'cc_expiry': card.get('cc_expiry'),
            'cvNumber': card.get('cvNumber')
        }
        return values

    def _update_website_sale_delivery_return(self, order, **post):
        Monetary = request.env['ir.qweb.field.monetary']
        carrier_id = int(post['carrier_id'])
        currency = order.currency_id
        print("carried id",order)
        print("carried id",carrier_id)
        print("carried id",order.amount_delivery)
        if order:
            return {
                'status': order.delivery_rating_success,
                'error_message': order.delivery_message,
                'carrier_id': carrier_id,
                'is_free_delivery': not bool(order.amount_delivery),
                'new_amount_delivery': Monetary.value_to_html(order.amount_delivery, {'display_currency': currency}),
                'new_amount_untaxed': Monetary.value_to_html(order.amount_untaxed, {'display_currency': currency}),
                'new_amount_tax': Monetary.value_to_html(order.amount_tax, {'display_currency': currency}),
                'new_amount_total': Monetary.value_to_html(order.amount_total, {'display_currency': currency}),
                'new_amount_total_raw': order.amount_total,
                'delivery_charge': order.amount_delivery,
                'amount_untaxed': order.amount_untaxed,
                'amount_total': order.amount_total,
            }
        return {}

    @http.route(['/shop/update_carrier1'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_eshop_carrier(self, **post):
        order = request.website.sale_get_order()
        carrier_id = int(post['carrier_id'])
        if order:
            order._check_carrier_quotation(force_carrier_id=carrier_id)
        # return self._update_website_sale_delivery_return(order, **post)
        return self._update_website_sale_delivery_return(order, **post)


