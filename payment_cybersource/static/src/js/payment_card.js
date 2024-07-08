odoo.define('payment_cybersource.payment_card', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');
publicWidget.registry.payment_method_inline = publicWidget.Widget.extend({
    selector: '#payment_method',
    events: {
        'click .o_payment_option_card input': '_o_payment_option_card',
    },

    /**
     * @constructor
     */
    init: function () {
     console.log("****************************payment card");
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    _o_payment_option_card: function (ev) {
        var self = this;

        var paymentOptionId = $(ev.currentTarget).attr('data-payment-option-id');
        console.log("info",$(ev.currentTarget).attr('data-payment-option-id'))

        const $inlineForm = $('#o_payment_acquirer_inline_form_'+paymentOptionId);
        if ($inlineForm.children().length > 0) {
             $('#o_payment_acquirer_inline_form_'+paymentOptionId).show()
             $('.card_hide').hide();
             $('#delivery_carrier').hide();
        }
    },
    });

publicWidget.registry.delivery_carrier_inline = publicWidget.Widget.extend({
    selector: '#delivery_carrier',
    events: {
        'click .o_delivery_carrier_select1 input': '_o_payment_option_card',
    },

    /**
     * @constructor
     */
    init: function () {
     console.log("****************************payment card");
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
     _block_ui: function(){
         $('body').block({
                message: '<lottie-player src="https://assets9.lottiefiles.com/packages/lf20_p8bfn5to.json"  background="transparent"  speed="1"  style="height: 300px;"  loop autoplay></lottie-player>',
                overlayCSS: {backgroundColor: "#000", opacity: 0.3, zIndex: 1050, color: "#FFFFFF"},
        });
    },
    _un_block_ui: function (){
        setTimeout(function () {
            $('body').unblock();
        }, 5000);
    },
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    _o_payment_option_card: function (ev) {
        var self = this;
        var $radio = $(ev.currentTarget);
        self._block_ui();
        console.log("delivery changes",$radio)
        console.log("delivery changes",$radio.val())
        if ($radio.val()) {
         self._rpc({
            route: '/shop/update_carrier1',
            params: {
                carrier_id: $radio.val(),
            },
        }).then(function (values) {
            console.log("vavavavva fgfg",values)
             self._un_block_ui();
//            $("#cart_left_container").load(location.href + " #cart_left_container>*", "");
               $("#amount_total").html(values['new_amount_total'])
               $("#amount_delivery").html(values['new_amount_delivery'])
               $("#amount_subtotal").html(values['new_amount_untaxed'])
        });
        }

    },

    });
});