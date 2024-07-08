odoo.define('pos_return_pos.pos_return', function(require) {
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
    class ReturnButtons extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {

            var order = this.env.pos.get_order();
                var lines = order.get_orderlines();
                while(lines.length > 0) {
                    order.remove_orderline(lines[0]);
            }

            this.showScreen('OrderListReturn');
        }
    }

    ReturnButtons.template = 'ProductReturnButton';

    ProductScreen.addControlButton({
        component: ReturnButtons,
        condition: function() {
            return this.env.pos.config.return_order;
        },
    });

    Registries.Component.add(ReturnButtons);

    return ReturnButtons;


});