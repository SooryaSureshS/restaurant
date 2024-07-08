odoo.define('pos_booking.TablePopupConfirm', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
      const { useExternalListener } = owl.hooks;
    // formerly TextAreaPopupWidget
    // IMPROVEMENT: This code is very similar to TextInputPopup.
    //      Combining them would reduce the code.
    class TableConfirmPopupWidget extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        constructor() {
            super(...arguments);
            this.table = this.props.table;
            this.booking = null;
            var new_table = this.props.table;
            var self = this;
            this.blocked = false;
             const table_rev = this.rpc({
                        model: 'pos.config',
                        method: 'get_tables_reservation_available',
                        args: [this.env.pos.config.id, this.env.pos.config.minimize_booking_gape],
                    }).then(function (result) {
                         console.log("login reservation weeeeeeeeeeeeee",result);
                         if (result[0].length > 0){
                            _.each(result[0], function(booking) {
                            console.log("kinder find vbbvbv",booking.table_id,new_table);
                               if (booking.table_id == new_table.id){
                                 console.log("kinder find vbbvbv",booking);
//                                             const { confirmed } =  await Gui.showPopup('TableConfirmPopupWidget')
//                                 const { confirmed } = self.showPopup('TableEditingBooking', {
//                                    reservation: booking
//                                });
                                 self.booking = booking;
                                 $('.edit_booking_info').show();
                                 self.blocked = true;

                               }
                            });
                         }else if(result[1].length > 0){
                             _.each(result[1], function(booking) {
                                console.log("kinder find vbbvbv",booking.table_id,new_table);
                               if (booking.table_id == new_table.id){
                                self.booking = booking;
                                 $('.edit_booking_info').show();
                                 self.blocked = true;
                               }
                               });
                         }
                         else{
                          $('.edit_booking_info').hide();
                         }
                    });
        }
        mount() {
            var self = this;

        }
        async selected(){
            var self = this;
            var people_number = $("#people_number").val()
            if (people_number != "" && people_number > 0) {
                this.env.table_people_number = people_number;
                this.props.table.input_no_of_people = people_number;
                this.props.resolve({ confirmed: false, payload: {'_just_close_popup': false} });
                this.trigger('close-popup');
                // self.cancel()
            }
        }
        async confirmed(){
            var self = this;
            var people_number = $("#people_number").val()
            if (people_number != "" && people_number > 0) {
                this.env.table_people_number = people_number;
                this.props.table.input_no_of_people = people_number;
            }
            if (self.blocked){
                const { confirmed } = await this.showPopup('ConfirmPopup', {
                    title: 'The Table Is Already Booked',
                    body: 'Do you want to book another booking',
                });
                if (confirmed) {
                    self.confirm()
                }
            }else{
                 self.confirm()
            }

        }
        async select_table(){
            var self = this;
//            this.confirm()
        }
        async edit_table_booking(){
            var self = this;
//            console.log("events",this.booking);
//             const { confirmed } =  await Gui.showPopup('TableConfirmPopupWidget')
             const { confirmed } = self.showPopup('TableEditingBooking', {
                reservation: this.booking
            });
        }


    }
    TableConfirmPopupWidget.template = 'TableConfirmPopupWidget';
    TableConfirmPopupWidget.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',

    };

    Registries.Component.add(TableConfirmPopupWidget);

    return TableConfirmPopupWidget;

});
