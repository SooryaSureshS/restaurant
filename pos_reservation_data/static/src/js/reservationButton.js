odoo.define('pos_reservation_data.reservationButton', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PopupControllerMixin = require('point_of_sale.PopupControllerMixin')
    const Chrome = require('point_of_sale.Chrome');
    var models = require('point_of_sale.models');

    class TableReservationButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
            this.showScreen('TableReservationList');
        }
    }

    TableReservationButton.template = 'TableReservationButton';

    ProductScreen.addControlButton({
        component: TableReservationButton,
        condition: function() {
           return this.env.pos;
        },
    });
    Registries.Component.add(TableReservationButton);
    return TableReservationButton;
});