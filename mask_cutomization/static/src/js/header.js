odoo.define('mask_cutomization.header', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');
publicWidget.registry.header_class = publicWidget.Widget.extend({
    selector: '.header_class',
    events: {
//        'input #player_kit': '_player_kit',
//        'input #player_kit': '_player_kit',
//        'click .fold_button': '_fold_button',
//        'click .3d_button': '_3d_button',
//        'click .image_button': '_image_button',
//        'click .product_packaging': '_product_packaging',
//        'click #gui_back': '_gui_back',
    },

    /**
     * @constructor
     */
    init: function () {
     console.log("****************************header")
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
//        var product = $('#product').val();
//        var line = $('#line').val();
//
//
//        $('.all_btn').each(function (){
//            $(this).removeClass('active_block')
//            $(this).removeClass('active_none')
//        });
//        $('.fold_button').last().trigger('click');
//        self._rpc({
//                    route: "/package/image/delete",
//                    params: {
//                        line: line,
//                    },
//                }).then(function (data) {
//                console.log("product_varient_id",data)
//                if (data){
//                    $('#cart_number').html(2)
//                }
//        });

        return this._super.apply(this, arguments);
    },
    });
});