odoo.define('pos_booking.booking', function(require) {
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
    const ajax = require('web.ajax');
    /* Loading Extra Fields */
    models.load_fields("hr.employee", ['work_phone']);

    const PosBookingFloorScreenn = (FloorScreen) =>
        class extends FloorScreen {
            async _onSelectTable(event) {
                    var self = this;
                    const table = event.detail;
                    console.log("_onSelectTable 2", event)

                    if (this.state.isEditMode) {
                        this.state.selectedTableId = table.id;
                    } else {
                        if(this.env.pos.config.iface_floorplan){
                            if(this.env.pos.config.enable_table_booking){
                               const table_rev =  await this.rpc({
                                    model: 'pos.config',
                                    method: 'get_tables_reservation_available',
                                    args: [this.env.pos.config.id, this.env.pos.config.minimize_booking_gape],
                                }).then(function (result) {
//                                     console.log("login reservation hhhhhh",result);
//                                     if (result[0].length > 0){
//                                        _.each(result[0], function(booking) {
//                                           if (booking.table_id == table.id){
//                                             console.log("kinder find vbbvbv",booking);
////                                             const { confirmed } =  await Gui.showPopup('TableConfirmPopupWidget')
//                                             const { confirmed } = self.showPopup('TableEditingBooking', {
//                                                reservation: booking
//                                            });
//
//                                           }
//                                        });
//                                     }
                                });

                                const { confirmed, payload } =  await Gui.showPopup('TableConfirmPopupWidget',{'table': table})
                                if (confirmed) {
                                      console.log("table confirmed",table);
                                        ajax.jsonRpc('/get/future/booking', 'call', {'table': table.id}).then(function (data) {
                                        console.log("_onSelectTable 232323",data)
                                        self.showScreen('TableBookingLayout',{'table': table, 'future_booking': data});
                                        });
                                }
                                else{
                                     console.log("cancel table confirmed",confirmed);
                                     if (payload && payload._just_close_popup == false) {
                                        this.env.pos.set_table(table);
                                        var $target = $('.floor-map #' + self.env.pos.tables_by_id[table.id]['id']);
                                        var values = $target.find('#counter_timer_div_reservation').val();
                                        setTimeout(function () {
                                           if (values){
                                                self.env.pos.get_order().set_reservation(values);

                                            }
                                        }, 5000);
                                     }

                                }
                            }else{
                                this.env.pos.set_table(table);
                            }
                        }
                    }
            }
            async askPin(employee) {
                const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
                    isPassword: true,
                    title: this.env._t('Password ?'),
                    startingValue: null,
                });

                if (!confirmed) return false;

                if (employee.pin === Sha1.hash(inputPin)) {
                    return employee;
                } else {
                    await this.showPopup('ErrorPopup', {
                        title: this.env._t('Incorrect Password'),
                    });
                    return false;
                }
            }
        };

    Registries.Component.extend(FloorScreen, PosBookingFloorScreenn);

    return FloorScreen;

});