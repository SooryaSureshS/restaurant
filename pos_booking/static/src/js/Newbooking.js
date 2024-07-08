odoo.define('pos_booking.Newbooking', function(require) {
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
    class TableNewBooking extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        constructor() {
            super(...arguments);
            this.table_info = this.props.table
            $('#select_person').val(10);
            this.merge_request = false;
//            useExternalListener(window, 'focusout', this._giftCardScan);

        }
        mounted() {
            var self = this;
            $('#select_person').val(this.table_info.seats);
//            $('#select_person').val(10);
            console.log("tab seat",this.table_info.seats,$('#select_person'));
        }
//        getPayload() {
//            const selected = this.props.list.find((item) => this.state.selectedId === item.id);
//            return selected && selected.item;
//        }
        async confirmed(){
            var self = this;
            console.log("book table",self.table_info)
            var booking_selected_table = $('#booking_selected_table').val();
            var booking_selected_floor = $('#booking_selected_floor').val();
            var select_person = $('#select_person').val();
            var booking_date = $('#booking_date').val();
            var select_time = $('#select_time').val();
            var selected_merge_table = $('#select_merge').val();

            var booking_selected_table = $('#booking_selected_table').val();
            var booking_selected_floor = $('#booking_selected_floor').val();
            var select_person = $('#select_person').val();
            var booking_date = $('#booking_date').val();
            var select_time = $('#select_time').val();
             console.log("res megege  ",select_time)
            ajax.jsonRpc('/get/table/available/booking', 'call', {
                        "time_gap": self.env.pos.config.minimize_booking_gape,
                        "selected_merge_table": selected_merge_table,
                        "selected_table": self.table_info.id,
                        "select_time": select_time,
                        "booking_date": booking_date,
                        "merge_request":  self.merge_request
                    }).then(function(res) {
                        console.log("res megege  ",res);
                        if (res == 0){
//                            book
                              if (booking_selected_table && select_person && booking_date && select_time){
                                    var counts = 0;
                                    ajax.jsonRpc('/get/pos/table/booking/id', 'call', {
                                            "booking_selected_table": booking_selected_table,
                                            "minimize_booking_gape": self.env.pos.config.minimize_booking_gape,
                                            "booking_date": booking_date,
                                            "select_time": select_time,
                                            "merge_table": selected_merge_table,
                                        }).then(function(res) {
                                            if(!res){
                                                  const { confirmedd } =  Gui.showPopup('TableBookingInfoWidget',{
                                                        booking_selected_table: booking_selected_table,
                                                        booking_selected_floor: booking_selected_floor,
                                                        select_person: select_person,
                                                        booking_date: booking_date,
                                                        select_time: select_time,
                                                        merge_table: selected_merge_table,

                                                });
                                            }else{
                                                Gui.showPopup('ErrorPopup', {
                                                    title: 'Table Not Booked',
                                                    body: 'The Time is already booked',
                                                });
                                            }
                                    });
                                }
                        }else if(res == 1 || res == 2){
                            alert("Table is already booked at this time")
                        }else if(res == 3){
                            alert("Table is already booked at this time")
                        }else if(res == 4){
//                            book
                            if (booking_selected_table && select_person && booking_date && select_time){
                                var counts = 0;
                                ajax.jsonRpc('/get/pos/table/booking/id', 'call', {
                                        "booking_selected_table": booking_selected_table,
                                        "minimize_booking_gape": self.env.pos.config.minimize_booking_gape,
                                        "booking_date": booking_date,
                                        "select_time": select_time,
                                        "merge_table": selected_merge_table,
                                    }).then(function(res) {
                                        if(!res){
                                              const { confirmedd } =  Gui.showPopup('TableBookingInfoWidget',{
                                                    booking_selected_table: booking_selected_table,
                                                    booking_selected_floor: booking_selected_floor,
                                                    select_person: select_person,
                                                    booking_date: booking_date,
                                                    select_time: select_time,
                                                    merge_table: selected_merge_table,

                                            });
                                        }else{
                                            Gui.showPopup('ErrorPopup', {
                                                title: 'Table Not Booked',
                                                body: 'The Time is already booked',
                                            });
                                        }
                                });
                            }
                        }else{
                            alert("Table is already booked at this time")
                        }
            });


//            var booking_selected_table = $('#booking_selected_table').val();
//            var booking_selected_floor = $('#booking_selected_floor').val();
//            var select_person = $('#select_person').val();
//            var booking_date = $('#booking_date').val();
//            var select_time = $('#select_time').val();
//            console.log("informtiona",booking_selected_table,select_person,booking_date,select_time);
//            console.log("informtiona",self);
//            if (booking_selected_table && select_person && booking_date && select_time){
//                var counts = 0;
//                ajax.jsonRpc('/get/pos/table/booking/id', 'call', {
//                        "booking_selected_table": booking_selected_table,
//                        "minimize_booking_gape": this.env.pos.config.minimize_booking_gape,
//                        "booking_date": booking_date,
//                        "select_time": select_time,
//                    }).then(function(res) {
//                        if(!res){
//                              const { confirmedd } =  Gui.showPopup('TableBookingInfoWidget',{
//                                    booking_selected_table: booking_selected_table,
//                                    booking_selected_floor: booking_selected_floor,
//                                    select_person: select_person,
//                                    booking_date: booking_date,
//                                    select_time: select_time,
//
//                            });
//                        }else{
//                            Gui.showPopup('ErrorPopup', {
//                                title: 'Table Not Booked',
//                                body: 'The Time is already booked',
//                            });
//                        }
//                });
//            }
        }
        async ChangeSeatCapacity() {
            var self = this;
            console.log("selctet seat capacity",self);
            var selected = $('#select_person').val();
            if (selected <= this.table_info.seats){
                this.merge_request = false;
                 $('#merge_tr').hide('swing');
            }else{
                this.merge_request = true;
                $('#merge_tr').show('swing');
                $('#select_merge').empty();
                _.each(self.env.pos.tables_by_id, function(table) {
                    var diff = parseInt(selected) - parseInt(self.table_info.seats);
                    if (diff <= table.seats && table.id != self.table_info.id){
                        if (table.floor_id[0] == self.table_info.floor_id[0]){
                             $('#select_merge').append('<option value='+table.id+'>'+table.name+'</option>');
                        }
                    }

                })

            }
        }
        ChangeMergeTable () {
            var self = this;
            var selected_merge_table = $('#select_merge').val();
             ajax.jsonRpc('/get/table/available/booking', 'call', {
                        "selected_merge_table": selected_merge_table,
                        "selected_table": self.table_info.table.id,
                    }).then(function(res) {
                        console.log("res megege  ",res);
                    });
        }
        BookingDate(){
            var self = this;
            $('#select_time').empty();
            var pickup_date = '';
            try{
                pickup_date = document.getElementById("booking_date").value;
            }
            catch(err){
                console.log();
            }
            if (pickup_date==''){
            pickup_date = "Today";
                          }
            ajax.jsonRpc('/get/time/booking1', 'call', {"ready": 1,"picking_date":pickup_date}).then(function(res) {
            var cooking_time = 0;
            cooking_time = res;
                try{
            var pickup_date = res.picking_date;
            var after_date = res.after_date;
            var output = res.today_date;
            var strtDt  = new Date(pickup_date);
            var endDt  = new Date(output);


            console.log(pickup_date, "==", after_date)
            console.log(strtDt, "< >", endDt)
            if((pickup_date==after_date)|| (strtDt>endDt)){
                console.log("klajsdlkajdkl")
                var from_time_2 =res.from_time_2;
                var now_time = res.time_now;
                var time30 = res.from_time_1;
                var time15 = time30;
                if(time30>from_time_2)
                {
                    end_time = '2359';
                    from_time_2 = '23:59';
                }
                if((pickup_date==output)&&(now_time>time30))
                {
                    if (now_time<from_time_2){
                        time30=now_time;
                    }
                }
                var start_time = time30.replace(":","");
                var end_time = from_time_2.replace(":","");
                var start_hour = start_time.slice(0, -2);
                var start_minutes = start_time.slice(-2);
                var end_hour = end_time.slice(0, -2);
                var end_minutes = end_time.slice(-2);
                var startDate = new Date(0,0,0, start_hour, start_minutes);
                var endDate = new Date(0,0,0, end_hour, end_minutes);
                var millis = endDate - startDate;
                var minutes = millis/1000/60;
                var loop_no=minutes/30;
                console.log("WRETYUIOHGFDHJ")
                if (loop_no>0){

                console.log(now_time, "< >", from_time_2)
                console.log(pickup_date, "< >", output)

                if((now_time<from_time_2)||(pickup_date!=output))
                {
                    var count = 0;
                    console.log("DFGHJKLKJHGFD")
                    for(var i=1;i<=loop_no;i++)
                        {
                             if(pickup_date==output)
                               {
                                    console.log("YTYTYTYTTYYT",time30,count)
                                    if(time30<=from_time_2)
                                        {

                                        if (count == 0){
                                            console.log("VVVVVVVVVVjj",time30)
                                            var tm = moment.utc(time30,'HH:mm').add(self.env.pos.config.booking_time_out,'minutes').format('HH:mm');
                                            $('#select_time').append('<option value='+tm+'>'+tm+'</option>');
                                            time30 = tm;
                                        }
                                        else{
                                            console.log("VVVVVVVVVV",tm)
                                            var tm = moment.utc(time30,'HH:mm').add(30,'minutes').format('HH:mm');
                                            $('#select_time').append('<option value='+tm+'>'+tm+'</option>');
                                            time30 = tm;
                                        }

                                        }
                                        count = count+1;
                                }
                            else
                                {
                                    console.log("WWWWWWWWW")
                                    var tm = moment(time15,'HH:mm').add(30,'minutes').format('HH:mm');
                                    $('#select_time').append('<option value='+tm+'>'+tm+'</option>');
                                    time15 = tm;
                                }
                        }
                    }
                    clock = $('#table_booking_counter').FlipClock(self.env.pos.config.booking_time_out * 60,{
                                    clockFace: 'MinuteCounter',
                                    autoStart: true,
                                    countdown: true,
                                    callbacks: {
                                        stop: function() {
                                            self.cancel();
                                        }
                                    }
                                });
//                                clock.setTime(5);
//                                clock.setCountdown(true);
//                                clock.start();
                }

                }
                else{
                    $('#select_time').empty();
                }

                }
                catch(err){
                console.log(err)
                }
                });


        }


    }
    TableNewBooking.template = 'TableNewBooking';
    TableNewBooking.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',

    };

    Registries.Component.add(TableNewBooking);

    return TableNewBooking;

});
