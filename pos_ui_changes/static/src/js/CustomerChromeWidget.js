odoo.define('pos_ui_changes.CustomerChromeWidget', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PopupControllerMixin = require('point_of_sale.PopupControllerMixin')
    const Chrome = require('point_of_sale.Chrome');
    var models = require('point_of_sale.models');
    const { posbus } = require('point_of_sale.utils');

    /* Return Order button for view the kitchen screen for managers */
    class SetCustomersWidgets extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click-customer', this._onClickCustomer);
            useListener('click-discount', this._clickDiscount);
        }
//        mounted() {
//        }
//        willUnmount() {
//        }
        get isLongName() {
            return this.client && this.client.name.length > 10;
        }
        get client() {
            var self = this
            const order = self.env.pos
            if (order){
                return this.env.pos.get_client();
            }

        }
        async _onClickCustomer() {
            // IMPROVEMENT: This code snippet is very similar to selectClient of PaymentScreen.
            var self = this;
            const order = self.env.pos.get_order();
            if (order){
                const currentClient = order.get_client();
                const { confirmed, payload: newClient } = await self.showTempScreen(
                    'ClientListScreen',
                    { client: currentClient }
                );
                if (confirmed) {
                    order.set_client(newClient);
                    order.updatePricelist(newClient);
                }
            }else{
                 await this.showPopup('ErrorPopup', {
                        title: 'Order Not Defined ',
                        body: 'Please Go first page or set table'
                 });
            }

        }
        async _clickDiscount() {
            console.log("Discountedss");
        }

    }

    SetCustomersWidgets.template = 'SetCustomerWidgets';

    Registries.Component.add(SetCustomersWidgets);

    return SetCustomersWidgets;


});