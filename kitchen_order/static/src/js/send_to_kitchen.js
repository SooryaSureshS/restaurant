odoo.define('kitchen_order.send_to_kitchen', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const Chrome = require('point_of_sale.Chrome');
    const { bus, serviceRegistry } = require('web.core');
    var models = require('point_of_sale.models');
    const BusService = require('bus.BusService');
    const PaymentScreen = require('point_of_sale.PaymentScreen');



    /*Button Action for Send to kitchen screen*/
    class SendToKitchen extends PaymentScreen {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
	        var self = this;
            var selectedOrder = this.env.pos.get_order();
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
                      await this.rpc(
                        {
                            model: 'pos.order',
                            method: 'broadcast_order_data',
                            args: [selectedOrder],
                            kwargs: { context: this.env.session.user_context },
                        },
                        {
                            timeout: 30000,
                            shadow: true,
                        }
                    );
                     $( ".send-to-kitchen-mouse-click" ).css('pointer-events', 'none');
                    alert("Order sent successfully")

            }
        }

    }

    SendToKitchen.template = 'SendToKitchen';


    Registries.Component.add(SendToKitchen);

    return SendToKitchen;


    Registries.Component.extend(Chrome, PosBusChrome);

    return Chrome;

});