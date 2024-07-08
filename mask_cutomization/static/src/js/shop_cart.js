odoo.define('mask_cutomization.shop_cart', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');

var qweb = core.qweb;

publicWidget.registry.shop_cart_container = publicWidget.Widget.extend({
    selector: '#shop_cart_container',
    events: {
//        'input #upload_file_change': '_upload_file_change',
//        'click #fetch_upload': '_fetch_upload',
        'change #qnty-width': '_qty_update',
        'click #gui_back': '_gui_back',
        'click #cbtn1': '_remove_product',
        'click #cbtn2': '_cancel_popup',
        'click .product_delete': '_product_delete',
        'click #checkout_button': '_checkout_button',
    },

    /**
     * @constructor
     */
    init: function () {
     console.log("*****************cart page loaded")
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },

    _qty_update: function (ev){
        var self = this;
        var line_id = $(ev.currentTarget).attr('data_line_id');
        var min_qty = $(ev.currentTarget).attr('data_min_qty');
        var min_step = $(ev.currentTarget).attr('data_min_qty_step');
        var qty = $(ev.currentTarget).val();
        if (qty <=0 ){
            console.log("qty",qty);
            $('#popup_alert_message').show('swing');
            $('#product_line').val(line_id);
            $('#product_qty').val(qty);
            $('#overlay').show('swing');
        }else{
            if (line_id && qty) {
                if (parseFloat(qty) < parseFloat(min_qty)){
                    $(ev.currentTarget).val(parseFloat(min_qty));
                }
                else if (parseFloat(qty)%parseFloat(min_step) > 0.0) {
                    $(ev.currentTarget).val(
                        parseFloat(qty) + (parseFloat(min_step)-(parseFloat(qty)%parseFloat(min_step)))
                    );
                }
                self._rpc({
                        route: "/shop/cart/qty/update",
                        params: {
                            line: line_id,
                            qty: $(ev.currentTarget).val(),
                        },
                    }).then(function (data) {
                        console.log("amount",data)
                        if (data){
                            $("#shop_cart_container").load(location.href + " #shop_cart_container>*", "");
                        }
                   });
            }
        }

    },
    _remove_product: function (ev) {
        var self = this;
        var product_line = $('#product_line').val();
        var product_qty = $('#product_qty').val();
        $('#popup_alert_message').hide();
        $('#product_line').val();
        $('#product_qty').val();
        $('#overlay').hide();
        if (product_line && product_qty) {
                self._rpc({
                        route: "/shop/cart/qty/update",
                        params: {
                            line: product_line,
                            qty: product_qty,
                        },
                    }).then(function (data) {
                        console.log("amount",data)
                        if (data){
                            $("#shop_cart_container").load(location.href + " #shop_cart_container>*", "");
                        }
                   });
            }

    },
     _cancel_popup: function (ev) {
        var self = this;
          $('#popup_alert_message').hide();
        $('#product_line').val('');
        $('#product_qty').val('');
        $('#overlay').hide();
         $("#shop_cart_container").load(location.href + " #shop_cart_container>*", "");

    },
     _product_delete: function (ev) {
        var self = this;
        var qty = 0;
        var line_id = $(ev.currentTarget).attr('data_line_id');
         $('#popup_alert_message').show('swing');
         $('#product_line').val(line_id);
         $('#product_qty').val(qty);
         $('#overlay').show('swing');
    },
    _checkout_button: function (ev) {
        var self = this;
        console.log("window location")
        window.location.href='/shop/checkout'
//        var qty = 0;
//        var line_id = $(ev.currentTarget).attr('data_line_id');
//         $('#popup_alert_message').show('swing');
//         $('#product_line').val(line_id);
//         $('#product_qty').val(qty);
//         $('#overlay').show('swing');
    },
    _gui_back: function (ev) {
        var self = this;
        window.history.go(-1)
    },

    });
});