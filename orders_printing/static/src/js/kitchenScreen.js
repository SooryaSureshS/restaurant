odoo.define('orders_printing.kitchenScreen', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const kitchenScreenWidget = require('kitchen_order.kitchenscreen_template');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PopupControllerMixin = require('point_of_sale.PopupControllerMixin')
    const Chrome = require('point_of_sale.Chrome');
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;
    const ajax = require('web.ajax');
    var utils = require('web.utils');
    var session = require('web.session');
    var utils = require('web.utils');

    const kitchenScreenOpenOrder = kitchenScreenWidget => class extends kitchenScreenWidget {
        constructor() {
            super(...arguments);
            this.order_print_data = [];
            this.printedOrders = [];
            this.printedOrders.push(1);
            this.printer_status = false;
        }
        mounted() {
            super.mounted();
            console.log("Starting long polling ***************************************************");
            if(this.env.pos.config.is_order_printer) {
                if(this.env.pos.config.trigger_screen == 'kvs') {
                    var printResult =  this.ajax_long_polling_order_print();
                }
            }
        }

        async ajax_long_polling_order_print() {
            console.log("Long polling ***************************************************printing");
            var self = this;
            self.pool_count = self.pool_count + 1;
            var limit_reload = this.env.pos.config.limit_reload;
            var time_out = this.env.pos.config.time_out_screens;
            var long_pooling_port = this.env.pos.config.long_pooling_port;
            var ipaddress = this.env.pos.config.ipaddress;
            if (this.env.pos.config.is_order_printer) {
                console.log("IS ORDER PRINTER");
                console.log("prin orderssssssss",self.printedOrders);
                var dataToLog = {'session_id':this.env.pos.pos_session.id};
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/longpolling/pollings/order/fetch',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),

                    success: function(data) {
                        if (data.result) {
                            var order = null;
                            self.order_print_data = data.result;
                            self.fetch_each_order();
                            console.log("TO PRINT INFO",self.order_print_data);
                        }

                        setTimeout(function(){
                            self.ajax_long_polling_order_print();
                        }, time_out * 1000);

                    },

                    error: function (jqXHR, status, err) {
                        setTimeout(function(){
                            self.ajax_long_polling_order_print();
                        }, 10000);
                    },

                    timeout: 80000,
                });
            }

        }

        async fetch_each_order(){
            var self = this;
            var limit_reload = this.env.pos.config.limit_reload;
            var time_out = this.env.pos.config.time_out_screens;
            var long_pooling_port = this.env.pos.config.long_pooling_port;
            var ipaddress = this.env.pos.config.ipaddress;
             if (self.order_print_data.length>0){
                if (self.order_print_data[0]){
                    for (let i = 0; i <= self.order_print_data[0].length; i++) {
                        var order=self.order_print_data[0][i];
                        if (order){
                                const printResult = await self.printChanges(order);
                                if (printResult) {
                                    console.log("PRINT SUCCESS",order);
                                    this.printer_status = false;
                                }
                                else{
                                    console.log("NOT PRINTED",order);
                                    this.printer_status = false;
                                }
                        }
                    }
                }
            }
        }
        async status_change_pos(values){
            let p_print = false;
            var ipaddress = this.env.pos.config.ipaddress;
            var data = {'order':Object.values(values),'types': 'pos'};
            console.log("statss changes possss",data);
            $.ajax({
                type: 'POST',
                url: ipaddress+'/order/print/update',
                async: true,
                processData: true,
                contentType: "application/json; charset=ytf-8",
                beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                data: JSON.stringify({'params': data, jsonrpc: '2.0'}),

                success: function(data) {
                     p_print = true;
                    console.log("UPDATED ORDER ***************************************************,",data);
                },
            });
            return p_print
        }
        async status_change_sale(values){
            let p_print = false;
            var ipaddress = this.env.pos.config.ipaddress;
            var data = {'order':Object.values(values),'types': 'sale'};
            console.log("statss changes saleeee",data);
            $.ajax({
                type: 'POST',
                url: ipaddress+'/order/print/update',
                async: true,
                processData: true,
                contentType: "application/json; charset=ytf-8",
                beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                data: JSON.stringify({'params': data, jsonrpc: '2.0'}),

                success: function(data) {
                    console.log("UPDATED ORDER ***************************************************",data);
                    p_print = true;
                },
            });
            return p_print
        }

        async printChanges(order){
            var printers = this.env.pos.printers;
            let isPrintSuccessful = true;
            for(var i = 0; i < printers.length; i++){
                if (printers[i].config.id == Object.keys(order)[0]){
                    var values=Object.values(order)[0];
                    if (values.type == 'pos'){
                        if (this.printedOrders.length >0){
                             _.each(self.printedOrders,function(printedOrders) {
                                if(printedOrders != values.name){
                                    this.printedOrders.push({'id':values.name})
                                }
                             });
                        }else{
                            this.printedOrders.push({'id':values.name})
                        }
                        console.log("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",this.printer_status,values.name);
                       if (!this.printer_status){
                            this.printer_status = true;
                            var receipt = QWeb.render('OrderPrintReceiptPos',{printObj:values, widget:this});
                            const result = await printers[i].print_receipt(receipt);
                            if (!result.successful) {
                                isPrintSuccessful = false;
                                 this.printedOrders = _.without(this.printedOrders, _.findWhere(this.printedOrders, {
                                          id: values.name
                                     }));
                                     this.printer_status = false;
                            }else{
                                 const p_status = await this.status_change_pos(values['order_line']);
                                 if (p_status) {
                                    this.printedOrders = _.without(this.printedOrders, _.findWhere(this.printedOrders, {
                                          id: values.name
                                     }));
                                     this.printer_status = false;
                                      console.log("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",this.printer_status,values.name);
                                 }
                            }
                             console.log("**********^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",this.printer_status,values.name);
                       }
                    }
                     if (values.type == 'sale'){
                        if (this.printedOrders.length >0){
                             _.each(self.printedOrders,function(printedOrders) {
                                if(printedOrders != values.name){
                                        this.printedOrders.push({'id':values.name})
                                    }
                                });
                        }else{
                            this.printedOrders.push({'id':values.name})
                        }
                        if (!this.printer_status){
                            this.printer_status = true;
                            var receipt = QWeb.render('OrderPrintReceiptSale',{printObj:values, widget:this});
                            const result = await printers[i].print_receipt(receipt);
                            if (!result.successful) {
                                isPrintSuccessful = false;
                                 this.printedOrders = _.without(this.printedOrders, _.findWhere(this.printedOrders, {
                                          id: values.name
                                     }));
                                 this.printer_status = false;
                            }else{
                                const p_status = await this.status_change_sale(values['order_line']);
                                if (p_status) {
                                     this.printedOrders = _.without(this.printedOrders, _.findWhere(this.printedOrders, {
                                      id: values.name
                                    }));
                                    this.printer_status = false;
                                    console.log("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",this.printer_status,values.name);
                                }
                            }
                        }
                    }
                }
            }
            return isPrintSuccessful;
        }
    }
    Registries.Component.extend(kitchenScreenWidget, kitchenScreenOpenOrder);
    return kitchenScreenWidget;
});