odoo.define('pos_booking.FloorEditMode', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
    const { useExternalListener } = owl.hooks;
    const FloorScreen = require('pos_restaurant.FloorScreen');
    const useSelectEmployee = require('pos_hr.useSelectEmployee');
    /* Loading Extra Fields */
    models.load_fields("hr.employee", ['work_phone']);

    const PosBookingEditModeFloorScreen = (FloorScreen) =>
        class extends FloorScreen {
            get activeTablesEditMode() {
                var self = this;
               setTimeout(function () {
                    self.new_toggleEditMode();
                }, 1000);
            }
            new_toggleEditMode() {
                if (this.env.pos.iseditLayout) {
                    $('.floor-screen .floor-map .edit-button').trigger('click');
                    this.env.pos.iseditLayout = false;
//                    this.state.isEditMode = true;
//                    this.state.selectedTableId = null;
                }
            }
//            async _tableLongpolling() {
//                console.log("floor screen long pooling",this)
//                if (this.state.isEditMode) {
//                    return;
//                }
//                try {
//                    const result = await this.rpc({
//                        model: 'pos.config',
//                        method: 'get_tables_order_count',
//                        args: [this.env.pos.config.id],
//                    });
//                    result.forEach((table) => {
//                        const table_obj = this.env.pos.tables_by_id[table.id];
//                        const unsynced_orders = this.env.pos
//                            .get_table_orders(table_obj)
//                            .filter(
//                                (o) =>
//                                    o.server_id === undefined &&
//                                    (o.orderlines.length !== 0 || o.paymentlines.length !== 0) &&
//                                    // do not count the orders that are already finalized
//                                    !o.finalized
//                            ).length;
//                        table_obj.order_count = table.orders + unsynced_orders;
//                    });
//                    this.render();
//                } catch (error) {
//                    if (error.message.code < 0) {
//                        await this.showPopup('OfflineErrorPopup', {
//                            title: 'Offline',
//                            body: 'Unable to get orders count',
//                        });
//                    } else {
//                        throw error;
//                    }
//            }
//        }

        };

    Registries.Component.extend(FloorScreen, PosBookingEditModeFloorScreen);

    return FloorScreen;
});