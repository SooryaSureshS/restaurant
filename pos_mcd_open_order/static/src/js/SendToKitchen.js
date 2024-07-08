odoo.define('kitchen_order.sequencepopup', function(require) {
    'use strict';

    const { useState } = owl;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class SendtoKitchenPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.order_id = useState(this.props.order_id);
            this.printers = useState(this.props.printers);
        }
        async confirm_send() {
            console.log("\n ____this.props.order_id_____",this.props.order_id)
            var order_id = this.props.order_id;
            var printers = this.props.printers;
            var self = this;
            console.log("\n ________order_id_______",order_id)
            console.log("\n -----printers______",printers)
            var list_orders = [];
            console.log("\n ____printers.length____",printers.length)
            for(var i = 0; i < printers.length; i++){
                console.log("\n _______i_______",i)
                var changes = order_id.computeChangesPrinter(printers[i].config.product_categories_ids,printers[i].config.name);
                list_orders.push(changes);
            }

        }
    }
    SendtoKitchenPopup.template = 'SendtoKitchenPopup';
    SendtoKitchenPopup.defaultProps = {
        confirmText: 'Ok',
//        cancelText: 'Cancel',
        title: 'Send To Kitchen',
        body: '',
    };

    Registries.Component.add(SendtoKitchenPopup);

    return SendtoKitchenPopup;

});