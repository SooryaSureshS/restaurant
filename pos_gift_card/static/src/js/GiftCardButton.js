odoo.define('pos_gift_card.GiftCardButton', function(require) {
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
    class GiftCardButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
                this.showScreen('GiftScreenWidget');
        }
    }
    GiftCardButton.template = 'GiftCardButton';

    ProductScreen.addControlButton({
        component: GiftCardButton,
        condition: function() {
            return this.env.pos.config.enable_gift_card;
        },
    });

    Registries.Component.add(GiftCardButton);

    return GiftCardButton;


});