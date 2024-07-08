odoo.define('payment_cybersource.payment_form', require => {
    'use strict';

    const checkoutForm = require('payment.checkout_form');
    const manageForm = require('payment.manage_form');

    const paymentTestMixin = {
        _processDirectPayment: function (provider, acquirerId, processingValues) {
            if (provider !== 'cyber') {
                return this._super(...arguments);
            }
            const cc_number = document.getElementById('cc_number').value;
            const cc_holder_name = document.getElementById('cc_holder_name').value;
            const cc_expiry = document.getElementById('cc_expiry').value;
            const cc_cvc = document.getElementById('cc_cvc').value;
            const acquirer_id = document.getElementById('acquirer_id').value;
            const csrf_token = document.getElementById('csrf_token').value;
            const partner_id = document.getElementById('partner_id').value;
            return this._rpc({
                route: '/payment/cyber/cybersource_payment',
                params: {
                    'reference': processingValues.reference,
                    'cc_number': cc_number,
                    'cc_holder_name': cc_holder_name,
                    'cc_expiry': cc_expiry,
                    'cc_cvc': cc_cvc,
                    'acquirer_id': acquirer_id,
                    'csrf_token': csrf_token,
                    'partner_id': partner_id
                },
            }).then(() => {
                window.location = '/payment/status';
            });
        },
        _prepareInlineForm: function (provider, paymentOptionId, flow) {
            if (provider !== 'cyber') {
                return this._super(...arguments);
            } else if (flow === 'token') {
                return Promise.resolve();
            }
            this._setPaymentFlow('direct');
            return Promise.resolve()
        },
    };
    checkoutForm.include(paymentTestMixin);
    manageForm.include(paymentTestMixin);
});
