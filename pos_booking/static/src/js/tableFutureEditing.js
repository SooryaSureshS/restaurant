odoo.define('pos_booking.tableFutureEditing', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
      const { useExternalListener } = owl.hooks;
      const ajax = require('web.ajax');
    // formerly TextAreaPopupWidget
    // IMPROVEMENT: This code is very similar to TextInputPopup.
    //      Combining them would reduce the code.
    class TableFutureBooking extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        constructor() {
            super(...arguments);
            this.reservation = this.props.booking;
            this.date_reserved = this.props.booking.date_reserved.replace(" ", "T");
            this.date_reserved_end = this.props.booking.date_reserved_end.replace(" ", "T");
//            $('#occasion').val(this.booking.occasion);
            console.log("reservation s",this);
        }
        mounted() {
            $('#occasion').val(this.reservation.occasion);
        }
        async edit_booking(){
            var self = this;
//            if ($('#edit_table_enable').hasClass('edit_table')){
//                $('#edit_table_enable').removeClass('edit_table');
//                $('#reservation_start').addClass('edit_mode_off');
//                $('#reservation_ends').addClass('edit_mode_off');
//                $('#special_request').addClass('edit_mode_off');
//                $('#occasion').addClass('edit_mode_off');
//                 $('#save_details_info').hide('swing');
//                 $('#table_available_info').show('swing');
//            }else{
//                $('#edit_table_enable').addClass('edit_table');
//                $('#reservation_start').removeClass('edit_mode_off');
//                $('#reservation_ends').removeClass('edit_mode_off');
//                $('#special_request').removeClass('edit_mode_off');
//                $('#occasion').removeClass('edit_mode_off');
//                $('#save_details_info').show('swing');
//                $('#table_available_info').hide('swing');
//            }

        }
        async save_details() {
            var self = this;
             var reservation_start = $('#reservation_start').val()
             var reservation_ends = $('#reservation_ends').val()
             var special_request = $('#special_request').val()
             var occasion = $('#occasion').val()
             var party_size = $('#party_size').val()
             var reservation_id = $('#reservation_id').val()
//             console.log("save details information",reservation_start,reservation_ends,special_request,occasion,)
             ajax.jsonRpc('/get/update/booking', 'call', {
                'reservation_start': reservation_start,
                'reservation_ends': reservation_ends,
                'special_request': special_request,
                'occasion': occasion,
                'party_size': party_size,
                'reservation_id': reservation_id,
                }).then(function (data) {
                    if(data){
                         Gui.showPopup('ConfirmPopup', {
                                title: 'Edit Info',
                                body: data,
                         });
                    }

             });
        }
        async available(){
            var self = this;
            var reservation_id = $('#reservation_id').val()
            ajax.jsonRpc('/get/booking/cancel', 'call', {
                'reservation_id': reservation_id,
                }).then(function (data) {
                 self.showScreen('FloorScreen');
                 self.confirm();
             });
        }
        async confirmed(){
            var self = this;
            this.confirm()
        }
        async select_table(){
            var self = this;
            this.confirm()
        }


    }
    TableFutureBooking.template = 'TableFutureBooking';
    TableFutureBooking.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',

    };

    Registries.Component.add(TableFutureBooking);

    return TableFutureBooking;

});
