odoo.define('pos_booking.availableTable', function(require) {
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
    const TableWidget = require('pos_restaurant.TableWidget');
    /* Loading Extra Fields */
    models.load_fields("hr.employee", ['work_phone']);
    models.load_fields("restaurant.table", ['background_color']);

    const PosAvailableTables = (TableWidget) =>
        class extends TableWidget {
            mounted() {
            const table = this.props.table;
            console.log(this);
            function unit(val) {
                return `${val}px`;
            }

            const style = {
                width: unit(table.width),
                height: unit(table.height),
                'line-height': unit(table.height),
                top: unit(table.position_v),
                left: unit(table.position_h),
                'border-radius': table.shape === 'round' ? unit(1000) : '3px',
            };
            if (table.color) {
                style.background = table.color;
            }
            if (table.height >= 150 && table.width >= 150) {
                style['font-size'] = '32px';
            }
            if (table.background_color){
                 style.background = table.background_color;
            }
            Object.assign(this.el.style, style);

            const tableCover = this.el.querySelector('.table-cover');
            Object.assign(tableCover.style, { height: `${Math.ceil(this.fill * 100)}%` });
        }
             get reservationCheck() {
                var self = this;
                const table = this.props.table;
                var self = this;
                try {
                    this.rpc({
                        model: 'pos.config',
                        method: 'get_tables_reservation_available',
                        args: [this.env.pos.config.id, this.env.pos.config.minimize_booking_gape],
                    }).then(function (result) {
                         console.log("login reservation",result);
                         $('.floor-map .table').css('background',self.env.pos.config.table_available_color);
                         var $ctarget = $('.floor-map .table')
                         $ctarget.find('#counter_timer_div').timer('remove');
                         $ctarget.find('#counter_timer_div').html('')
                         $ctarget.find('#merge_qr_code_functionality').html('')
                         result[0].forEach((table) => {
                                if (table.table_id){
                                    var $target = $('.floor-map #' +self.env.pos.tables_by_id[table.table_id]['id']);
                                    $target.find('#counter_timer_div_reservation').val(table.id);
//                                    $target.find('#counter_timer_div').timer('remove');
                                    const table_obj = self.env.pos.tables_by_id[table.table_id];
                                    $('.floor-map #' +self.env.pos.tables_by_id[table.table_id]['id']).css('background',self.env.pos.config.table_unavailable_color);
//                                     $target.css('border', '4px solid white !important;');
//                                    $('.floor-map #' +self.env.pos.tables_by_id[table.table_id]['id']).css('border-top','4px solid white !important;');
//                                    css('border-top','4px solid white !important;');

                                     if (table.started_order[0]){
                                        if (table.started_order[0].length >0){
                                            table.started_order[0].forEach((counter) => {

                                              if (counter.perparation_elapse){
                                                 $target.find('#counter_timer_div').timer('remove');
                                                 $target.find('#counter_timer_div').timer({
                                                        countdown: true,
                                                        duration: counter.perparation_elapse,   	// This will start the countdown from 3 mins 40 seconds
                                                        callback: function() {	// This will execute after the duration has elapsed
                                                            console.log('Time up!');
                                                            $target.find('#counter_timer_div').stop().css("background-color", "#FF003A").animate({ backgroundColor: "#FFAA02"}, 700);

                                                        }
                                                 });
                                             }else{
                                                 $target.find('#counter_timer_div').timer('remove');
                                                 $target.find('#counter_timer_div').html('Delivery Delay')
                                                 $target.find('#counter_timer_div').stop().css("background-color", "#FF003A").animate({ backgroundColor: "#FFAA02"}, 700);
                                             }
                                             if (counter.state != "preparing"){
                                                     $target.find('#counter_timer_div').timer('remove');
                                                     $target.find('#counter_timer_div').html(counter.state)
                                             }
                                        });
                                        }else{

                                            $target.find('#counter_timer_div').show('swing');
                                            $target.find('#counter_timer_div').timer('remove');
                                             $target.find('#counter_timer_div').timer({
                                                    countdown: true,
                                                    duration: table.end_time_lapse,   	// This will start the countdown from 3 mins 40 seconds
                                                    callback: function() {	// This will execute after the duration has elapsed
                                                        console.log('Time up!');
                                                        $target.find('#counter_timer_div').hide('swing');
                                                        $target.find('#counter_timer_div').timer('remove');

                                                    }
                                             });
                                             $target.find('#counter_timer_div').stop().css("background-color", "#FFAA02").animate({ backgroundColor: "#FF003A"}, 700);
                                        }

                                    }
//                                    move functionality
                                    if(table.merged_table){
                                        var $target = $('.floor-map #' +self.env.pos.tables_by_id[table.table_id]['id']);
                                        $target.find('#merge_qr_code_functionality').html("M with "+self.env.pos.tables_by_id[table.merged_table]['name'] );
//                                        $target.animate({ left: self.env.pos.tables_by_id[table.merged_table].position_h + self.env.pos.tables_by_id[table.merged_table].width,
//                                                     top: self.env.pos.tables_by_id[table.merged_table].position_v,
//                                         }, 10000);
                                         $target.css('left',self.env.pos.tables_by_id[table.merged_table].position_h + self.env.pos.tables_by_id[table.merged_table].width)
                                         $target.css('top',self.env.pos.tables_by_id[table.merged_table].position_v)

                                    }else{
                                        var $target = $('.floor-map #' +self.env.pos.tables_by_id[table.table_id]['id']);
                                        $target.find('#merge_qr_code_functionality').html("");
                                    }
//                                    $target.stop().css("border-color", "#"+table.border_color).animate({ backgroundColor: "#FF003A"}, 700);
                                        console.log("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm",table);


                                }



                         });
                         result[1].forEach((table) => {
                          if (table.table_id){
                             $('.floor-map #' +self.env.pos.tables_by_id[table.table_id]['id']).css('background',self.env.pos.config.table_unavailable_soon_color);
                             }
                         });
                         result[2].forEach((table) => {
                          if (table.table_id){
                             $('.floor-map #' +self.env.pos.tables_by_id[table.table_id]['id']).css('background',self.env.pos.config.table_available_soon_color);
                             }
                         });

                    });

                } catch (error) {
                    if (error.message.code < 0) {

                    } else {
                        throw error;
                    }
                }

            }



//            async _onSelectTable(event) {
//            var self = this;
//                    const table = event.detail;
//                    console.log("_onSelectTable 2")
//
//                    if (this.state.isEditMode) {
//                        this.state.selectedTableId = table.id;
//                    } else {
//                        if(this.env.pos.config.iface_floorplan){
//                            if(this.env.pos.config.enable_table_booking){
//                                const { confirmed } =  await Gui.showPopup('TableConfirmPopupWidget')
//                                if (confirmed) {
//                                      console.log("table confirmed",table);
//                                        ajax.jsonRpc('/get/future/booking', 'call', {'table': table.id}).then(function (data) {
//                                        console.log("_onSelectTable 232323",data)
//                                        self.showScreen('TableBookingLayout',{'table': table, 'future_booking': data});
//                                        });
//                                }
//                                else{
//                                     console.log("cancel table confirmed",confirmed);
//                                     this.env.pos.set_table(table);
//                                }
//                            }else{
//                                this.env.pos.set_table(table);
//                            }
//                        }
//                    }
//            }
        };

    Registries.Component.extend(TableWidget, PosAvailableTables);

    return TableWidget;

});