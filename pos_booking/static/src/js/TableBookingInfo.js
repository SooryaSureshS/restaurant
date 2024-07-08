odoo.define('pos_booking.TableBookingInfo', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
      const { useExternalListener } = owl.hooks;
      var ajax = require('web.ajax');
    // formerly TextAreaPopupWidget
    // IMPROVEMENT: This code is very similar to TextInputPopup.
    //      Combining them would reduce the code.
    class TableBookingInfoWidget extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        constructor() {
            super(...arguments);
            this.merge = this.props.merge_table
//            useExternalListener(window, 'focusout', this._giftCardScan);

        }
        async confirmed_booking(){
            var self = this;
            var booking_selected_table = $('#booking_selected_table').val();
            var booking_selected_floor = $('#booking_selected_floor').val();
            var select_person = $('#select_person').val();
            var booking_date = $('#booking_date').val();
            var select_time = $('#select_time').val();
            var name_person = $('#name_person').val();
            var occasion = $('#occasion').val();
            var note = $('#note').val();
            var email = $('#email').val();
            var phone = $('#phone').val();

            if (booking_selected_table && select_person && booking_date && select_time && name_person && phone && email){
//                const table_rev = this.rpc({
//                        model: 'pos.config',
//                        method: 'table_exits',
//                        args: [booking_selected_table,booking_date,select_time],
//                        }).then(function (result) {
//                            console.log("available or not",result)
//                        });

//                    ajax.jsonRpc('/get/pos/table/booking', 'call', {
//                        "booking_date": booking_date,
//                        "select_time": select_time,
//                    }).then(function(res) {
//                        console.log("result foundssssss",res);
//                        if(res){
//                        var counts=0;
//                           _.each(res, function(booking) {
//                                if(booking.table_id == booking_selected_table && counts ==0){
//                                     counts=1;
//                                     ajax.jsonRpc('/create/pos/user/Booking', 'call', {
//                                                "ready": 1,
//                                                'first_name':name_person,
//                                                'last_name': '',
//                                                'phone':phone,
//                                                'email':email,
//                                                'floor_id':booking_selected_floor,
//                                                'table_id':booking_selected_table,
//                                                'selected_time':select_time,
//                                                'booking_date': booking_date,
//                                                'select_person':select_person,
//                                                'occasion':occasion,
//                                                'note': note,
//                                        }).then(function(res) {
//                                                if(res){
//                                                     Gui.showPopup('ConfirmPopup', {
//                                                            title: 'Table Booked',
//                                                            body: 'The Table Booked',
//                                                     });
//                                                }
//                                        });
//                                }
//                           });
//
//                        }
//                    });


                ajax.jsonRpc('/create/pos/user/Booking', 'call', {
                        "ready": 1,
                        'first_name':name_person,
                        'last_name': '',
                        'phone':phone,
                        'email':email,
                        'floor_id':booking_selected_floor,
                        'table_id':booking_selected_table,
                        'selected_time':select_time,
                        'booking_date': booking_date,
                        'select_person':select_person,
                        'occasion':occasion,
                        'note': note,
                        'merge': self.merge,
                        'border_color': Math.floor(Math.random()*16777215).toString(16),
                }).then(function(res) {
                        if(res){
                             Gui.showPopup('ConfirmPopup', {
                                    title: 'Table Booked',
                                    body: 'The Table Booked',
                             });
                        }
                });
            }else{
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Booking Canceled'),
                    body: this.env._t('Please fill the required fields'),
                });
            }
            this.confirm()
        }
        async select_table(){
            var self = this;
              console.log("select table")
              this.confirm()
//              return false
        }


    }
    TableBookingInfoWidget.template = 'TableBookingInfoWidget';
    TableBookingInfoWidget.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',

    };

    Registries.Component.add(TableBookingInfoWidget);

    return TableBookingInfoWidget;

});
