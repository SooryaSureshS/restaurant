odoo.define('kitchen_order.kitchecn_order_button', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PopupControllerMixin = require('point_of_sale.PopupControllerMixin')
    const Chrome = require('point_of_sale.Chrome');
    var models = require('point_of_sale.models');

    /*Kitchen order button for view the kitchen screen for managers*/
    class KitchenOrderButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
            this.showScreen('kitchenScreenWidget');
        }
    }
    KitchenOrderButton.template = 'KitchenOrderButton';

    ProductScreen.addControlButton({
        component: KitchenOrderButton,
        condition: function() {
            return this.env.pos.config.iface_kitchen_order;
        },
    });

    Registries.Component.add(KitchenOrderButton);

    return KitchenOrderButton;


});