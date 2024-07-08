odoo.define('pos_mcd_open_order.posOpenOrders', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
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

    /* Return Order button for view the kitchen screen for managers */
    class PosMcdChanges extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
            var self = this;
            var selectedOrder = this.env.pos.get_order();
//            selectedOrder.set_change_product(true);

//            console.log("mcd sss",selectedOrder)
            selectedOrder.initialize_validation_date();
            var currentOrderLines = selectedOrder.get_orderlines();
            var orderLines = [];
            _.each(currentOrderLines,function(item) {
                return orderLines.push(item.export_as_JSON());
            });
            if (selectedOrder.get_client()){
               _.each(currentOrderLines,function(item) {
                    item.set_customer(selectedOrder.get_client()['id']);
                });
            }
            if (orderLines.length === 0) {
                return alert ('Please select product !');
            } else {
                this.env.pos.push_orders(selectedOrder);

                const order = this.env.pos.get_order();
                console.log("\n __-order____",order)
                var printers = this.env.pos.printers;
                var list_orders = [];
                for(var i = 0; i < printers.length; i++){
                    var changes = order.computeChangesPrinter(printers[i].config.product_categories_ids,printers[i].config.name);
                    console.log("has changes dfd",printers[i].config.name);
                    list_orders.push(changes);
                }
                const { confirmed: confirmedPopup } = this.showPopup('SendtoKitchenPopup', {
                    title: 'Send to Kitchen',
                    body: 'Order has been send to kitchen',
                    order_id:order,
                    printers:printers
                });
                console.log("\n _____-confirmedPopup______",confirmedPopup)
//                console.log("ingof",list_orders);
//                setTimeout(function(){
//                    this.showScreen('ReceiptScreenOpenMcd', {'order': list_orders, 'printers': printers,'widget': self});
//                    }, 4000);




//                if (order.hasChangesToPrint()) {
//                    const isPrintSuccessful = await order.printChanges();
//                    if (isPrintSuccessful) {
//                        order.saveChanges();
//                    } else {
//                        await this.showPopup('ErrorPopup', {
//                            title: 'Printing failed',
//                            body: 'Failed in printing the changes in the order',
//                        });
//                    }
//                }



//                    console.log("changeorder list",change_order_list);
//                    setTimeout(function(){
//                        self.rpc({
//                            model: 'pos.order',
//                            method: 'get_pos_orders_send',
//                            args: [selectedOrder.name,selectedOrder.updated_order,change_order_list],
//                        }).then(function (orders) {
//                            console.log("ordersssssssssssss",orders)
//                            self.showScreen('ReceiptScreenOpenMcd', {'order': orders, 'widget': self, 'change_order': selectedOrder.updated_order, 'change_list': selectedOrder.change_product_list});
//
//                        if (self.env.pos.proxy.printer) {
//                            var receipt = QWeb.render('OrderReceiptMcd',{'order': orders, 'widget': self, 'change_order': selectedOrder.updated_order, 'change_list': selectedOrder.change_product_list});
//                            const printResult =  self.env.pos.proxy.printer.print_receipt(receipt);
//                            if (printResult.successful) {
//                                return true;
//                            }
//                            }
//                        });
//                    }, 4000);

            }
        }
        async receiptPrintWebMCd(receipt){
                    if (this.env.pos.proxy.printer) {
                        const printResult = await this.env.pos.proxy.printer.print_receipt(receipt);
                       }
    }
    }



    PosMcdChanges.template = 'ProductMcdButton';

    ProductScreen.addControlButton({
        component: PosMcdChanges,
        condition: function() {
            return this.env.pos.config.return_order;
        },
    });

    Registries.Component.add(PosMcdChanges);

    return PosMcdChanges;


});