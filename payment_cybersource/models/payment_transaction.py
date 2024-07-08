import logging
import time
from odoo import fields, _, api, models
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _send_payment_request(self):
        super(PaymentTransaction, self)._send_payment_request()
        # super()._send_payment_request()
        if self.provider != 'cyber':
            return
        self._handle_feedback_data('cyber', {'reference': self.reference})

    def _get_specific_processing_values(self, processing_values):
        res = super(PaymentTransaction, self)._get_specific_processing_values(processing_values)
        # res = super()._get_specific_processing_values(processing_values)
        if self.provider != 'cyber':
            return res
        sale_order = processing_values.get('reference').split('-')[0]
        sale_order_obj = self.env['sale.order'].search([('name', '=', sale_order)])
        self.amount = sale_order_obj.amount_total
        processing_values['amount'] = sale_order_obj.amount_total
        return {
            'access_token': payment_utils.generate_access_token(
                processing_values['reference'],
                processing_values['partner_id']
            )
        }

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        tx = super(PaymentTransaction, self)._get_tx_from_feedback_data(provider, data)
        # tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'cyber':
            return tx

        reference = data.get('reference')
        tx = self.search([('reference', '=', reference), ('provider', '=', 'cyber')])
        if not tx:
            raise ValidationError(
                "Test: " + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_feedback_data(self, data):
        super(PaymentTransaction, self)._process_feedback_data(data)
        # super()._process_feedback_data(data)
        if self.provider != "cyber":
            return

        self._set_done()  # Dummy transactions are always successful
        if self.tokenize:
            token = self.env['payment.token'].create({
                'acquirer_id': self.acquirer_id.id,
                'name': payment_utils.build_token_name(payment_details_short=data['reference']),
                'partner_id': self.partner_id.id,
                'acquirer_ref': 'ODOO-NEW-ALIAS-%s' % time.time(),
                'verified': True,  # The payment is authorized, so the payment method is valid
            })
            self.token_id = token.id

    def _cyber_tokenize_from_feedback_data(self, data):
        self.ensure_one()

        token = self.env['payment.token'].create({
            'acquirer_id': self.acquirer_id.id,
            'name': payment_utils.build_token_name(payment_details_short=data['cc_summary']),
            'partner_id': self.partner_id.id,
            'acquirer_ref': 'ODOO-NEW-ALIAS-%s' % time.time(),
            'adyen_shopper_reference': data['additionalData']['recurring.shopperReference'],
            'verified': True,  # The payment is authorized, so the payment method is valid
        })
        self.write({
            'token_id': token,
            'tokenize': False,
        })
        _logger.info(
            "created token with id %s for partner with id %s", token.id, self.partner_id.id
        )


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    cybersource_profile = fields.Char(string='cybersource_profile')
