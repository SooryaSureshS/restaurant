odoo.define('mask_cutomization.shop_address', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');

var qweb = core.qweb;

publicWidget.registry.shop_address_container = publicWidget.Widget.extend({
    selector: '#shop_address_container',
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
             'click .apply_address_both_billing_delivery': '_shipping_and_billing_address',
             'click .next_button_submit': '_next_button_submit',
    },

    /**
     * @constructor
     */
    init: function () {
     console.log("*****************cart address")
        this._super.apply(this, arguments);
    },
    _next_button_submit: function (ev) {
        var self = this;
         $( "input" ).each(function() {
          console.log("*****************cart address",$(this).val())
          $(this).val($(this).val()).trigger('change');
        });
        $(ev.currentTarget).closest('form').submit();
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
   _onClickChangeShipping: function (ev) {
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
    },
    _onClickEditAddress: function (ev) {
        ev.preventDefault();
        console.log("********** ssssssssss*******cart checkout",$(ev.currentTarget).attr('label'))

        $(ev.currentTarget).closest('div.one_kanban').find('form.d-none').attr('action', '/shop/address?type="billing"').submit();
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
    _shipping_and_billing_address: function (ev) {
        var self = this;
        console.log("shipping address for both",$(ev.currentTarget).is(':checked'))
        if($(ev.currentTarget).is(':checked')) {
               $('#billing_address_info').show('swing');
               self._fill_billing_address();
        }else{
               $('#billing_address_info').hide('swing');
        }

    },
    _fill_billing_address: function () {
        var self = this;
        $('#d_street').val($('#b_street').val()).trigger('change');
        $('#d_street2').val( $('#b_street2').val()).trigger('change');
        $('#d_city').val( $('#b_city').val()).trigger('change');
        $('#d_state_id').val( $('#b_state_id').val()).trigger('change');
        $('#d_zip').val( $('#b_zip').val()).trigger('change');
        $('#d_country_id').val( $('#b_country_id').val()).trigger('change');
        $('#d_company_name').val( $('#b_company_name').val()).trigger('change');
        $('#d_name').val( $('#b_name').val()).trigger('change');
        $('#d_email').val( $('#b_email').val()).trigger('change');
        $('#d_phone_code').val( $('#b_phone_code').val()).trigger('change');
        $('#d_phone').val( $('#b_phone').val()).trigger('change');
    },

    });
});