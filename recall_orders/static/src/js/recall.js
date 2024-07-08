odoo.define('recall_orders.recall', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PopupControllerMixin = require('point_of_sale.PopupControllerMixin')
    const Chrome = require('point_of_sale.Chrome');
    var models = require('point_of_sale.models');

    /* Return Order button for view the kitchen screen for managers */
    class RecallOrders extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
            this.showScreen('OrderTable');
        }
    }

    RecallOrders.template = 'OrderRecallOrders';

//    ProductScreen.addControlButton({
//        component: RecallOrders,
//        condition: function() {
//            return this.env.pos.config.recall_orders;
//        },
//    });

    Registries.Component.add(RecallOrders);

    return RecallOrders;


});