odoo.define('website_tips.tip', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;

publicWidget.registry.tip = publicWidget.Widget.extend({
    selector: '#tip_website_data',
    events: {
//        'click #top_menu a[href="/shop"]': '_onshop_click',
//        'mouseover .tip_class_category': 'hover_tip_class_category',
        'click .tip_class_category': '_tip_class_category',
        'click #other_tip_tr_button': '_other_tip_tr_button',
    },
//    /**
//     * @constructor
//     */
    init: function () {
        var self = this;
        this._super.apply(this, arguments);
            this._rpc({
                    route: "/shop/website/tip/check",
                    params: {
                    },
                }).then(function (data) {
                    console.log("draft orderssdsds",data)
                    if(data){
                        if(data[0]){
                            console.log("draft orderssdsds",data[0])
                             $('#'+data[0]).css('background-color','rgba(255, 0, 0, .2)');
                             $('#'+data[0]).css('border','2px solid rgba(255, 0, 0, 1)');
                             $('#'+data[0]).css('border-top','2px solid rgba(255, 0, 0, 1) !important');
                        }else{
                            $('#tip_5').css('background-color','rgba(255, 0, 0, .2)');
                            $('#tip_5').css('border','2px solid rgba(255, 0, 0, 1)');
                            $('#tip_5').css('border-top','2px solid rgba(255, 0, 0, 1) !important');
                        }
                        self._rpc({
                            route: "/shop/website/tip/update",
                            params: {
                                tip: 5,
                                tip_data: 'tip_5'
                            },
                        }).then(function (data) {
                            $('#cart_products').load(window.location.href + " #cart_products" );
                            $('#cart_total').load(window.location.href + " #cart_total" );
                        });

                        if(data[1]){
                            $('#website_tips').show();
                        }else{
                            $('#website_tips').hide();
                        }

                    }
                });
    },
    hover_tip_class_category: function (ev){
        var self = this;

        $('.tip_class_category').css('background-color','');
        $('.tip_class_category').css('border','1px solid rgba(0, 0, 0, 0.125)');
        var $target = $(ev.currentTarget);
        $target.css('background-color','rgba(255, 0, 0, .2)');
        $target.css('border','2px solid rgba(255, 0, 0, 1)');
        $target.css('border-top','2px solid rgba(255, 0, 0, 1) !important');
    },
    _tip_class_category: function (ev){
        var self = this;
        var $target = $(ev.currentTarget);
        $('.tip_class_category').css('background-color','');
        $('.tip_class_category').css('border','1px solid rgba(0, 0, 0, 0.125)');
        $target.css('background-color','rgba(255, 0, 0, .2)');
        $target.css('border','2px solid rgba(255, 0, 0, 1)');
        $target.css('border-top','2px solid rgba(255, 0, 0, 1) !important');
        console.log("hover enevts new",$target.attr('data-info'))
        if ($target.attr('data-info') == 'tip_5'){
            $('#other_tip_tr').hide();
            self._rpc({
                    route: "/shop/website/tip/update",
                    params: {
                        tip: 5,
                        tip_data: $target.attr('data-info')
                    },
                }).then(function (data) {
//                    console.log("$('#cart_products').html(",$('#cart_products').html());
//                    $('#cart_products').html($('#cart_products').html());
//                    $('#cart_products').load(window.location.href);
                    $('#cart_products').load(window.location.href + " #cart_products" );
                    $('#cart_total').load(window.location.href + " #cart_total" );
                });
        }
        if ($target.attr('data-info') == 'tip_10'){
            $('#other_tip_tr').hide();
            self._rpc({
                    route: "/shop/website/tip/update",
                    params: {
                        tip: 10,
                        tip_data: $target.attr('data-info')
                    },
                }).then(function (data) {
                    $('#cart_products').load(window.location.href + " #cart_products" );
                    $('#cart_total').load(window.location.href + " #cart_total" );
                });
        }
        if ($target.attr('data-info') == 'tip_15'){
            $('#other_tip_tr').hide();
            self._rpc({
                    route: "/shop/website/tip/update",
                    params: {
                        tip: 15,
                        tip_data: $target.attr('data-info')
                    },
                }).then(function (data) {
                    $('#cart_products').load(window.location.href + " #cart_products" );
                    $('#cart_total').load(window.location.href + " #cart_total" );
                });
        }
        if ($target.attr('data-info') == 'tip_other'){
            $('#other_tip_tr').show();
        }
        if ($target.attr('data-info') == 'tip_none'){
            self._rpc({
                    route: "/shop/website/tip/update",
                    params: {
                        tip: false,
                        tip_data: $target.attr('data-info')
                    },
                }).then(function (data) {
                    $('#cart_products').load(window.location.href + " #cart_products" );
                    $('#cart_total').load(window.location.href + " #cart_total" );
                });
        }
    },
    _other_tip_tr_button: function (ev) {
        var self = this;
        var other_val = $('#other_tip_input_id').val();
        if($.isNumeric(other_val)){
            self._rpc({
                    route: "/shop/website/tip/update",
                    params: {
                        tip: other_val,
                        tip_data: 'tip_other'
                    },
                }).then(function (data) {
                    $('#other_tip_tr').hide();
                    $('#cart_products').load(window.location.href + " #cart_products" );
                    $('#cart_total').load(window.location.href + " #cart_total" );
                });
        }else{
            alert('Please Enter Amount Not Character')
        }

    },
    });
});