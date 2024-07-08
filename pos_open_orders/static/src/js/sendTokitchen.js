odoo.define('pos_open_orders.sendTokitchen', function(require) {
"use strict";
var models = require('point_of_sale.models');


const PaymentScreen = require('point_of_sale.PaymentScreen');
const Registries = require('point_of_sale.Registries');
const KitchenOrder = require('kitchen_order.validate_kitchen_order');
    const sendTokitchen = (KitchenOrder) =>
    class  extends KitchenOrder {

    constructor() {
            super(...arguments);
//            this.TypeSetting();
        }
         async SendToKitchen() {
	        var self = this;
	        console.log("weeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee");
            var selectedOrder = this.env.pos.get_order();
            selectedOrder.set_order_parse_json(selectedOrder);
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
                if(this.env.pos.get_order().get_delivery_type() == 'phone'){
                    if (this.env.pos.get_order().get_open_order_id()){
                        $( ".send-to-kitchen-mouse-click" ).css('pointer-events', 'none');
                        $( ".send-to-kitchen-hide" ).hide();
                        $( ".payment-hide" ).show();
                    }else{
                        if(this.env.pos.get_order().get_paymentlines().length > 0){
                            $( ".send-to-kitchen-hide" ).hide();
                            $( ".payment-hide" ).show();
                        }else{
                            selectedOrder.table = false;
                            console.log("o",selectedOrder)
                            this.env.pos.push_orders(selectedOrder);
                            this.env.pos.open_order_up();
                        }

                    }

                }else{
                    this.env.pos.push_orders(selectedOrder);
                }

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
                    $( ".send-to-kitchen-hide" ).hide();
                    $( ".payment-hide" ).show();

            }
        }

    }
    Registries.Component.extend(KitchenOrder, sendTokitchen);
    return KitchenOrder;

});