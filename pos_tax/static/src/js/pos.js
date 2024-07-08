odoo.define("pos_tax.pos_tax", function(require) {
"use strict";

const { useState, useRef, onPatched } = owl.hooks;
const PosComponent = require('point_of_sale.PosComponent');
const ProductScreen = require('point_of_sale.ProductScreen');
const OrderWidget = require('point_of_sale.OrderWidget');
const { useListener } = require('web.custom_hooks');
const Registries = require('point_of_sale.Registries');
const PopupControllerMixin = require('point_of_sale.PopupControllerMixin')
const Chrome = require('point_of_sale.Chrome');
const models = require('point_of_sale.models');

models.load_fields('account.tax', ['charge_type']);

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    initialize: function(attributes, options) {
        var result = _super_order.initialize.apply(this, arguments);
        this.skip_service_charge = false;
        this.skip_gst_vat_charge = false;
        return result;
    },
    init_from_JSON: function(json) {
        _super_order.init_from_JSON.apply(this, arguments);
        this.skip_service_charge = json.skip_service_charge;
        this.skip_gst_vat_charge = json.skip_gst_vat_charge;
    },
    export_as_JSON: function() {
        var json = _super_order.export_as_JSON.apply(this, arguments);
        json.skip_service_charge = this.skip_service_charge;
        json.skip_gst_vat_charge = this.skip_gst_vat_charge;
        return json;
    },
    export_for_printing: function() {
        var receipt = _super_order.export_for_printing.apply(this, arguments);
        receipt.skip_service_charge = this.skip_service_charge;
        receipt.skip_gst_vat_charge = this.skip_gst_vat_charge;
        return receipt;
    },
    get_tax_details: function() {
        var fulldetails = _super_order.get_tax_details.apply(this, arguments);
        fulldetails = _.sortBy(fulldetails, t => t.tax.charge_type == 'service_charge'? 1: 2);
        return fulldetails;
    }
});

var _super_orderline = models.Orderline.prototype;
models.Orderline = models.Orderline.extend({
    compute_all: function(taxes, price_unit, quantity, currency_rounding, handle_price_include=true) {
        var self = this;
        var order = this.order;
        var new_taxes = _.filter(taxes, function(t) {
            if (order.skip_service_charge && t.charge_type == 'service_charge') {
                return false
            }
            else if (order.skip_gst_vat_charge && t.charge_type == 'gst_vat_charge') {
                return false
            }
            return true
        });
        return _super_orderline.compute_all.call(this, new_taxes, price_unit, quantity, currency_rounding, handle_price_include);
    },
});

class OrderChargeMode extends PosComponent {
    constructor() {
        super(...arguments);
        useListener('click', this.onClick);
    }
    async onClick() {
        let self = this;
        let selectedOrder = this.env.pos.get_order();

        let current_charge_mode = 0;
        if (selectedOrder.skip_service_charge) { current_charge_mode += 1; }
        if (selectedOrder.skip_gst_vat_charge) { current_charge_mode += 2; }
        if (!current_charge_mode) { current_charge_mode = 4; }

        const chargeList = [
            {
                id: 1, label: 'No Service Charge', isSelected: current_charge_mode == 1,
                item: {'id': 1, 'name': 'No Service Charge'}},
            // {
            //     id: 2, label: 'No GST/VAT', isSelected: current_charge_mode == 2,
            //     item: {'id': 2, 'name': 'No GST/VAT'}},
            // {
            //     id: 3, label: 'No Service Charge/GST/VAT', isSelected: current_charge_mode == 3,
            //     item: {'id': 3, 'name': 'No Service Charge/GST/VAT'}},
            {
                id: 4, label: 'All Charges', isSelected: current_charge_mode == 4,
                item: {'id': 4, 'name': 'All Charges'}
            }
        ];

        const { confirmed, payload: selectCharge } = await this.showPopup('SelectionPopup',
            {
                title: this.env._t('Please Charge Mode'),
                list: chargeList
            });

        if (confirmed) {
            let selectChargeId = selectCharge.id;
            if (selectChargeId == 1) {
                selectedOrder.skip_service_charge = true;
                selectedOrder.skip_gst_vat_charge = false;
            } 
            else if (selectChargeId == 2) {
                selectedOrder.skip_service_charge = false;
                selectedOrder.skip_gst_vat_charge = true;
            }
            else if (selectChargeId == 3) {
                selectedOrder.skip_service_charge = true;
                selectedOrder.skip_gst_vat_charge = true;
            }
            else if (selectChargeId == 4) {
                selectedOrder.skip_service_charge = false;
                selectedOrder.skip_gst_vat_charge = false;
            }

            let lines_to_recompute = _.filter(selectedOrder.get_orderlines(), function (line) {
                return ! line.price_manually_set;
            });
            _.each(lines_to_recompute, function (line) {
                line.set_unit_price(line.product.get_price(selectedOrder.pricelist, line.get_quantity(), line.get_price_extra()));
                selectedOrder.fix_tax_included_price(line);
            });
            selectedOrder.trigger('change');
        }
    }
}

OrderChargeMode.template = 'OrderChargeModeButton';

ProductScreen.addControlButton({
    component: OrderChargeMode,
    condition: function() {
        return true;
    }
});

Registries.Component.add(OrderChargeMode);


const OrderWidgetExtended = (OrderWidget) =>
    class extends OrderWidget {
        constructor() {
            super(...arguments);
            this.state['taxes'] = {};
            this.state = useState(this.state);
        }
        _updateSummary() {
            var self = this;
            var all_taxes = this.order ? this.order.get_tax_details() : 0;
//            var all_taxes = this.order.get_tax_details();
            _.each(all_taxes, function(t) {
                t.amount = self.env.pos.format_currency(t.amount)
            });
            var all_taxes = _.sortBy(all_taxes, t => t.tax.charge_type == 'service_charge'? 1: 2);
            this.state.taxes = all_taxes;
            super._updateSummary();
        }
    }

Registries.Component.extend(OrderWidget, OrderWidgetExtended);


return OrderChargeMode;

});