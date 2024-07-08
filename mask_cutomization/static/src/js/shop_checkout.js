odoo.define('mask_cutomization.shop_checkout', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');

var qweb = core.qweb;

publicWidget.registry.shop_checkout_container = publicWidget.Widget.extend({
    selector: '#shop_checkout_container',
    events: {
//        'input #upload_file_change': '_upload_file_change',
//        'click #fetch_upload': '_fetch_upload',
//        'change #qnty-width': '_qty_update',
//        'click #gui_back': '_gui_back',
//        'click #cbtn1': '_remove_product',
//        'click #cbtn2': '_cancel_popup',
//        'click .product_delete': '_product_delete',
//        'click #checkout_button': '_checkout_button',
            'click .js_edit_address': '_onClickEditAddress',
             'click .js_change_shipping': '_onClickChangeShipping',
             'click #billing_address': '_billing_address',
             'click #shipping_address': '_shipping_address',
    },

    /**
     * @constructor
     */
    init: function () {
     console.log("*****************cart checkout")
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
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
            $("#shop_checkout_container").load(location.href + " #shop_checkout_container>*", "");
        }, 4000);
    },
   _onClickChangeShipping: function (ev) {
        this._block_ui();
        var $old = $('.all_shipping').find('.card.border.border-primary');
        $old.find('.btn-ship').toggle();
        $old.addClass('js_change_shipping');
        $old.removeClass('border border-primary');

        var $new = $(ev.currentTarget).parent('div.one_kanban').find('.card');
        $new.find('.btn-ship').toggle();
        $new.removeClass('js_change_shipping');
        $new.addClass('border border-primary');

        var $form = $(ev.currentTarget).parent('div.one_kanban').find('form.d-none');
        $.post($form.attr('action'), $form.serialize()+'&xhr=1');
        console.log("_onClickChangeShipping")
        this._un_block_ui();
//        window.location.reload();
//        $("#shop_checkout_container").load(location.href + " #shop_checkout_container>*", "");
    },
    _onClickEditAddress: function (ev) {
        ev.preventDefault();
        console.log("*****************cart checkout")
        console.log("********** ssssssssss*******cart checkout",$(ev.currentTarget).attr('title'))
        $(ev.currentTarget).closest('div.one_kanban').find('form.d-none').attr('action', '/shop/address').submit();
    },
    _billing_address: function (ev) {
        var self = this;
        if ($(ev.currentTarget).hasClass('active')){
            $('#billing_info').hide('swing');
            $(ev.currentTarget).removeClass('active');
        }else{
            $('#billing_info').show('swing');
            $(ev.currentTarget).addClass('active');
        }
    },
    _shipping_address: function (ev) {
        var self = this;
        if ($(ev.currentTarget).hasClass('active')){
            $('#shipping_info').hide('swing');
            $(ev.currentTarget).removeClass('active');
        }else{
            $('#shipping_info').show('swing');
            $(ev.currentTarget).addClass('active');
        }
    },
    _gui_back: function (ev) {
        var self = this;
        window.history.go(-1)
    },

    });
   publicWidget.registry.confirm_page_skypro = publicWidget.Widget.extend({
    selector: '#confirm_page_skypro',
    events: {
             'click #go_home': '_go_home',
    },

    /**
     * @constructor
     */
    init: function () {
     console.log("*****************cart checkout")
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    _go_home: function (ev) {
        window.location.href='/';
    },
    });

});