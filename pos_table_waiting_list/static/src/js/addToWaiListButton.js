odoo.define('pos_table_waiting_list.addToWaiListButton', function(require) {
    'use strict';
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { useState } = owl.hooks;
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    class AddToWaitListPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
        }
        async add_customer() {
            var self = this;
            var wait_list_name = $('#wait_list_name').val();
            var wait_list_phone = $('#wait_list_phone').val();
            var wait_list_email = $('#wait_list_email').val();
            var wait_list_party_size = $('#wait_list_party_size').val();
            var phone_regex =   /^\d+$/;
            var phone_valid =  phone_regex.test(wait_list_phone);
            var size_valid =  phone_regex.test(wait_list_party_size);

            var w_name = true
            var w_phone = true
            var w_party_size = true
            if(!wait_list_name){
                w_name = false
            }
            if(phone_valid === false){
                w_phone = false
            }
            if(size_valid === false){
                w_party_size = false
            }
            if ((w_name === true) && (w_party_size === true) && (w_phone === true)){
                rpc.query({
                    model: 'table.waiting.line',
                    method: 'saveWaitListData',
                    args: [wait_list_name, wait_list_phone, wait_list_email, wait_list_party_size],
                }).then(function (result) {
                    if(result === false){
                        self.showPopup('ErrorPopup', {
                            title: _t('Failed'),
                            body: _t(
                            'Some Error Occurred. Please try again later'
                            ),
                        });
                    }
                    else{
                        self.showPopup('ConfirmPopup', {
                        title: _t('Success'),
                            body: _t(
                            'Waiting List Created'
                            ),
                        });
                        self.env.pos.WaitList = result['waiting_list'];
                        self.env.pos.WaitListAvailableTables = result['available_tables'];

                    }
                });
            }
            else{
                $('#warning_add_wait_list').show();
            }

        }
    }

   AddToWaitListPopup.template = 'AddToWaitListPopup';
   AddToWaitListPopup.defaultProps = {
       confirmText: 'Ok',
       cancelText: 'Cancel',
       title: 'Add to wait list',
       body: '',
   };
   Registries.Component.add(AddToWaitListPopup);
   return AddToWaitListPopup;
});
