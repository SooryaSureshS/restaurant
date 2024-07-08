odoo.define('pos_open_orders.leftContainerPanel', function(require) {
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
    class SetContainerLeft extends PosComponent {
        constructor() {
            super(...arguments);
//            useListener('click-customer', this._onClickCustomer);
//            useListener('click-discount', this._clickDiscount);
        }
        selectPosButton (){
//            $('.right_container .floor-screen')
                if (this.env.pos.config.iface_floorplan) {
                    if (this.env.pos.get_order()) {
                        $('#hide_div_collapse').show();
                        this.showScreen('ProductScreen');
                    } else {
                        this.showPopup('ConfirmPopup', {
                            title: 'Unable to create order',
                            body: 'Orders cannot be created when there is no active table in restaurant mode',
                        });
                        return undefined;
                    }
                } else {
                    $('#hide_div_collapse').show();
                    this.showScreen('ProductScreen');
                }
        }
        selectPosOrderButton (){
//             this.showScreen('OpenOrderScreen');
             this.fetch_new_data();
        }
        async _fetchOrders(ids) {
        console.log("ssssssssssssss",this.rpc({
                model: 'pos.order',
                method: 'export_for_ui',
                args: [ids],
            }));
            return await this.rpc({
                model: 'pos.order',
                method: 'export_for_ui',
                args: [ids],
                context: [],
            });
        }
        fetch_new_data(){
            var self = this;


//            var fetchedOrders = this._fetchOrders([999,999]);
//            fetchedOrders.forEach((order) => {
//                console.log("aaaaa",fetchedOrders.json());
//            });
//            console.log("aaaaa",this._fetchOrders([999]));
            var params = {
                model: 'pos.order',
                method: 'get_pos_open_order',
                args: [self.env.pos.pos_session.id],
            }
            self.rpc(params, {async: false}).then(function(result){
                  self.env.pos.orders_open = [];
                  self.env.pos.orders_open = result;
//                  self.render();
                  self.showScreen('OpenOrderScreen');

            }).catch(function () {
                const { confirmed: confirmedPopup } = this.showPopup('ConfirmPopup', {
                    title: 'Network Error',
                    body: 'No Order Found Please Check Network',
                });
                if (!confirmedPopup) return;
            });
        }
    }

    SetContainerLeft.template = 'SetContainerLeft';

    Registries.Component.add(SetContainerLeft);

    return SetContainerLeft;


});