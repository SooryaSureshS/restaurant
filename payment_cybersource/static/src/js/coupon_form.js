odoo.define('payment_cybersource.coupon_form', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');
var QWeb = core.qweb;
publicWidget.registry.coupon_form_skypro = publicWidget.Widget.extend({
    selector: '#payment_method',
    events: {
        'click .use_coupon_code': '_use_coupon_code',
        'click #confirm_btn': '_confirm_btn',
        'click #confirm_cancel': '_confirm_cancel',
        'click #confirm_close': '_confirm_close',
    },

    /**
     * @constructor
     */
    init: function () {
     console.log("****************************Coupon Form");
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    _loadTemplates: function(){
        return ajax.loadXML('/payment_cybersource/static/xml/coupon.xml', QWeb);
    },
    _block_ui: function(){
         $('body').block({
                message: '<lottie-player src="https://assets9.lottiefiles.com/packages/lf20_p8bfn5to.json"  background="transparent"  speed="1"  style="height: 300px;"  loop autoplay></lottie-player>',
                overlayCSS: {backgroundColor: "#000", opacity: 0.3, zIndex: 1050, color: "#FFFFFF"},
        });
    },
    _un_block_ui: function (){
        setTimeout(function () {
            $('body').unblock();
        }, 1000);
    },
    _use_coupon_code: function (ev) {
        var self = this;
        $('#coupon_code_div').show('swing');
        $('#overlay').show('swing');
    },
    _confirm_btn: function (ev) {
        var self = this;
        var coupon = $('#promo_field').val();
        $('#coupon_code_apply').closest('form').submit();

    },
    _confirm_cancel: function (ev) {
        var self = this;
        $('#coupon_code_div').hide('swing');
        $('#overlay').hide('swing');
    },
    _confirm_close: function (ev) {
        var self = this;
        window.location.href = '/shop/payment';
    },

    });
});
