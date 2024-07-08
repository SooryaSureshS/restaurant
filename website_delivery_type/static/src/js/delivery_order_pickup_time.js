odoo.define('delivery_order_pickup_time.js', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;
    var ajax = require('web.ajax');


publicWidget.registry.store_management = publicWidget.Widget.extend({
    selector: '#wrap',
    events: {
        'click .check_product_delivery': '_is_a_future_order',
        'change #pickup_date_delivery': '_is_a_future_order',
        'click .save-delivery-time': '_save_delivery_time',
    },
    init: function () {

        var self = this;
        this._super.apply(this, arguments);


    },
    _is_a_future_order: function(ev) {
        var self = this;
        console.log($(".check_product_delivery").prop('checked'))

            if($(".check_product_delivery").prop('checked') == true){
                    $('#pickup_time_delivery').show();
                     // date calculation pickup
                    var pickup_date = '';
                    try{
                        pickup_date = document.getElementById("pickup_date_delivery").value;

                    }
                    catch(err){
                        console.log();
                    }

                    if (pickup_date==''){
                    pickup_date = "Today";
                                  }

                    ajax.jsonRpc('/get/time/cooking/delivery', 'call', {"ready": 1,"picking_date":pickup_date}).then(function(res) {
                    var cooking_time = 0;
                    cooking_time = res;
                    console.log(res);
                        try{

                    var pickup_date = res.picking_date;
                    var after_date = res.after_date;
                    var output = res.today_date;
                //    if(pickup_date=='Today'){
                //    pickup_date = output
                //    }
                    var strtDt  = new Date(pickup_date);
                    var endDt  = new Date(output);
                    if((pickup_date==after_date)|| (strtDt>endDt)){

                //        var end_time = '';
                        var from_time_2 =res.from_time_2;
                        var now_time = res.time_now;
                        var time30 = res.from_time_1;
                        var time15 = time30;


                //        finding minutes between start and end time

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
                        var loop_no=minutes/5;
                        if (loop_no>0){
                        if((now_time<from_time_2)||(pickup_date!=output))
                        {
                //        $("#pickup_time").show();
                            for(var i=1;i<=loop_no;i++)

                            {
                             if(pickup_date==output)
                               {
                                if(time30<=from_time_2)
                                {
                                var tm = moment.utc(time30,'HH:mm').add(5,'minutes').format('HH:mm');
                                $('#pickup_time_delivery_selection').append('<option value='+tm+'>'+tm+'</option>');
                                time30 = tm;
                                }
                                }
                                else
                                {
                                var tm = moment(time15,'HH:mm').add(5,'minutes').format('HH:mm');
                                $('#pickup_time_delivery_selection').append('<option value='+tm+'>'+tm+'</option>');
                                time15 = tm;
                                }
                                }
                                $("#pickup_time_delivery_selection").show();
                                }
                            else{
                                $("#pickup_time_delivery_selection").hide();
                             }
                        }
                        else{
                            $("#pickup_time_delivery_selection").hide();
                        }
                        }
                        else{
                        $("#pickup_time_delivery_selection").hide();
                        }
                        }
                        catch(err){
                        console.log(err)
                        }
                        });
//                    $('#pickup_time_delivery').show();

            }
            else{
                    $('#pickup_time_delivery').hide();
            }


    },
    _save_delivery_time : function(ev){
    if($(".check_product_delivery").prop('checked') == true){
    var pickup_date = document.getElementById("pickup_date_delivery").value;
    var pickup_time = document.getElementById("pickup_time_delivery_selection").value;
        ajax.jsonRpc('/save/time/cooking/delivery', 'call', {"ready": 1,"pickup_date":pickup_date,'pickup_time':pickup_time}).then(function(res) {
    });

    }

    }

    });
});