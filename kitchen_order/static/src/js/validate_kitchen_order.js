odoo.define('kitchen_order.validate_kitchen_order', function(require) {
    'use strict';

const PaymentScreen = require('point_of_sale.PaymentScreen');
const Registries = require('point_of_sale.Registries');
    const  KitchenPayment= (PaymentScreen) =>
    class  extends PaymentScreen {

    constructor() {
            super(...arguments);
        }
        async KitchenPaymentOrder() {
        var status= await this.validateOrderKitchen()
        if(status.status=='ok'){

         var self = this;
        var selectedOrder = this.env.pos.get_order();
        var currentOrderLines = selectedOrder.get_orderlines();
        var orderLines = [];
        _.each(currentOrderLines,function(item) {
            return orderLines.push(item.export_as_JSON());
        });
        if (orderLines.length === 0) {
            return alert ('Please select product !');
        }
        else{
             $( ".send-to-kitchen" ).hide();
//             await this.showPopup('ErrorPopup', {
//                        title: this.env._t('Confirmed'),
//                        body: this.env._t(
//                            'Hai, your Order is Validated.'
//                        ),
//                    });
            }
            $( ".send-to-kitchen-hide" ).show();

        }}
        async SendToKitchen() {
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
//                    await this.showPopup('ErrorPopup', {
//                        title: this.env._t('Confirmed'),
//                        body: this.env._t(
//                            'Order sent successfully'
//                        ),
//                    });
                    $( ".send-to-kitchen-hide" ).hide();
                    $( ".payment-hide" ).show();

            }
        }
        }
Registries.Component.extend(PaymentScreen, KitchenPayment);
return PaymentScreen;

});
