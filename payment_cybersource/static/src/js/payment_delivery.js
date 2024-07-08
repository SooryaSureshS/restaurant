odoo.define('payment_cybersource.payment_delivery', function (require) {
'use strict';

var core = require('web.core');
var publicWidget = require('web.public.widget');
require('website_sale_delivery.checkout');

var _t = core._t;

publicWidget.registry.websiteSaleDelivery.include({

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    _block_ui: function(){
         $('body').block({
                message: '<lottie-player src="https://assets9.lottiefiles.com/packages/lf20_p8bfn5to.json"  background="transparent"  speed="1"  style="height: 300px;"  loop autoplay></lottie-player>',
                overlayCSS: {backgroundColor: "#000", opacity: 0.3, zIndex: 1050, color: "#FFFFFF"},
        });
    },
    _un_block_ui: function (){
        var c = false;
        var $q = $('.o_wsale_delivery_badge_price').find('.fa-spin');
        $q.each(function(){
           c= true;
        });
        if (c == true) {
            setTimeout(function () {
                $('body').unblock();
                console.log("cccccccccccccc")
            }, 10000);
        }

    },
    _showLoading: function ($carrierInput) {
         this._super.apply(this, arguments);
         this._block_ui();
    },
    _handleCarrierUpdateResultBadge: function (result) {
        this._super.apply(this, arguments);
        this._un_block_ui();
        console.log("resultsss",result)

    },
});
});
