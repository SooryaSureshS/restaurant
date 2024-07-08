odoo.define('pos_multi_user_session_sync.ProductOrderSync', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PopupControllerMixin = require('point_of_sale.PopupControllerMixin')
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;
    const ajax = require('web.ajax');
    var utils = require('web.utils');
    var session = require('web.session');
    const OrderWidget = require('point_of_sale.OrderWidget');
    const { useState, useRef, onPatched } = owl.hooks;


    const ProductScreenMultiSync = ProductScreen => class extends ProductScreen {
        constructor() {
            super(...arguments);
             self.lock_order = false
             self.lock_pool = false
             this.ajax_long_pooling_product();
        }
        async ajax_long_pooling_product() {
            var self = this;
            var time_out = self.env.pos.config.session_sync_timeout;
            var long_pooling_port = self.env.pos.config.long_pooling_port;
            var ipaddress = self.env.pos.config.ipaddress;
            var order = this.env.pos.get_order();
            if (!order){
                self.lock_pool = true
            }else{
                self.lock_pool = false
            }
            if (!self.lock_pool){
//                self.lock_pool = true
                var dataToLog = {'session_id':self.env.pos.pos_session.id, 'name': order.name };
                 $.ajax({
                        type: 'POST',
                        url: ipaddress+'/polling/userinfo',
                        async: true,
                        processData: true,
                        contentType: "application/json; charset=ytf-8",
                        beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                        data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),

                        success: function(data) {
                            if (data.result) {
                                self.lock_pool = false
                                if (!self.lock_order){
//                                        self.lock_order = true
                                        const currentOrder = self.env.pos.get_order();
                                        if (data.result['payment_proceed'] === true) {
                                               var cashier =  self.env.pos.get_cashier();
                                               if (cashier){
                                                    if(cashier.id != data.result['payment_initiation']){
                                                        const { confirmed } =  self.showPopup('ConfirmPopup', {
                                                            title: 'Payment Initiated',
                                                            body: 'Payment initiated for current order by another user '+ data.result['employee'],
                                                        });
                                                        self.env.pos.set_table(null);

                                                    }else{
//                                                        console.log("333333333333333333333333333333",order.get_screen_data() )
                                                        if (order.get_screen_data().name == 'ProductScreen') {
                                                            self.env.pos.set_table(currentOrder.table);
                                                        }
//                                                        self.lock_order = false
                                                    }
                                               }

                                        }else{
                                            if (order.get_screen_data().name == 'ProductScreen') {
                                                            self.env.pos.set_table(currentOrder.table);
                                            }
//                                            self.env.pos.set_table(currentOrder.table);
//                                            setTimeout(function(){
//                                               self.lock_order = false
//                                            }, 2000);
                                        }
//                                        console.log("((((((()))))))))))))))))))((((((((((longedddd()))))))",self.lock_order,currentOrder.get_payment_proceed())
//                                        console.log("((((((()))))))))))))))))))((((((((((longedddd()))))))",currentOrder)
                                }
                            }
                             setTimeout(function(){
                                   self.ajax_long_pooling_product();
                             }, time_out * 1000);
                        },

                        error: function (jqXHR, status, err) {
                            setTimeout(function(){
                               self.ajax_long_pooling_product();
                               self.lock_pool = false;
                            }, 40000);
                        },

                        timeout: 40000,
                    })
                }

        }
        _onClickPay() {
            super._onClickPay();
            var currentOrder = this.env.pos.get_order();
            var cashier =  this.env.pos.get_cashier();
            if (cashier){
                 var payment_initiation = currentOrder.set_payment_initiation(cashier.id);
                 var payment_proceed = currentOrder.set_payment_proceed(true);
                 this.env.pos.push_orders(currentOrder);
            }
        }
        }

    Registries.Component.extend(ProductScreen, ProductScreenMultiSync);

    const OrderWidgetExtendedPosTax = (OrderWidget) =>
    class extends OrderWidget {
        constructor() {
            super(...arguments);
            this.state['taxes'] = {};
            this.state = useState(this.state);
        }
        _updateSummary() {
            var self = this;
            var all_taxes = this.order ? this.order.get_tax_details() : 0;
//            var all_taxes = this.order.get_tax_details();
            _.each(all_taxes, function(t) {
                t.amount = self.env.pos.format_currency(t.amount)
            });
            var all_taxes = _.sortBy(all_taxes, t => t.tax.charge_type == 'service_charge'? 1: 2);
            this.state.taxes = all_taxes;
            super._updateSummary();
        }
    }

    Registries.Component.extend(OrderWidget, OrderWidgetExtendedPosTax);

    return ProductScreen;
});