odoo.define('pos_mcd_open_order.addQty', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
     const { useExternalListener } = owl.hooks;
     var rpc = require('web.rpc');
     const addQty = require('pos_ui_changes.addQty');


     const addQtyNew = (addQty) =>
        class extends addQty {
               constructor() {
                    super(...arguments);
               }
                async confirm_remove(){
                    var self = this;
                    let order = this.env.pos.get_order();
                    let selectedLine = this.env.pos.get_order().get_selected_orderline();
                    order.set_change_product(true);
                    order.set_change_list(selectedLine);
                    let currentQuantity = selectedLine.set_quantity(0);
                    self.confirm();
                    try {
                         const result = await this.rpc({
                            model: 'pos.order',
                            method: 'get_tables_remove_change',
                            args: [selectedLine.product.id,selectedLine.quantity,order.name],
                        });
                         if (result) {
                                console.log("REmoved")
                         }
                    } catch (error) {
                        if (error.message.code < 0) {
                            await this.showPopup('ErrorPopup', {
                                title: this.env._t('Offline'),
                                body: this.env._t('Unable to create table because you are offline.'),
                            });
                            return;
                        } else {
                            throw error;
                        }
                    }
                }

        };
    Registries.Component.extend(addQty, addQtyNew);

    return addQty;
});
