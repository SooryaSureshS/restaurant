odoo.define('pos_ui_changes.OrderWidgets', function(require) {
    'use strict';

    const { useState, useRef, onPatched } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const { onChangeOrder } = require('point_of_sale.custom_hooks');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const OrderWidget = require('point_of_sale.OrderWidget');

    const OrderWidgetSelection = (OrderWidget) =>
        class extends OrderWidget {
            _selectLine(event) {
                var self = this;
                this.order.select_orderline(event.detail.orderline);
                let order = this.env.pos.get_order();
                let selectedLine = this.env.pos.get_order().get_selected_orderline();
                let currentQuantity = selectedLine.get_quantity()
                const { confirmed: confirmedPopup } = this.showPopup('AddQtyPopup', {
                    title: 'Add Quantity',
                    confirmText: 'Add Quantity',
                    qty: currentQuantity,
                });

            }

        };

    Registries.Component.extend(OrderWidget, OrderWidgetSelection);

    return OrderWidget;

});