odoo.define('delivery_type', function (require) {
    "use strict";

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;
    $(document).ready(function() {

        $("#country" ).hide();
        $("#state" ).hide();
        //	Time calculation pickup start ******************
        //crub order time calculation
        PickUpTimeCurb();
        //crub order time calculation change function
        $("#pickup_date_curb").change(function(){
        $('#pickup_time_curb').empty();
        PickUpTimeCurb();
        $('#pickup_time_curb').change();
        $('#pickup_time_curb').show();

        });

        // date calculation pickup
        PickUpTime();
        //  change date function pickup
        $("#pickup_date").change(function(){

        $('#pickup_time').empty();
        PickUpTime();
        $('#pickup_time').change();
        $('#pickup_time').show();

        });

        //	date calculation pickup end ******************

        ajax.jsonRpc('/max/date', 'call', {"ready": 1}).then(function(res) {
            if(res === false){
                $("#pickup_date" ).attr('disabled','disabled');
                $("#pickup_date_delivery" ).attr('disabled','disabled');
                $("#pickup_date_curb" ).attr('disabled','disabled');
            }
            else{
                var max_day = parseInt(res)
                $("#pickup_date" ).datepicker({minDate: 0, maxDate: max_day});
                $("#pickup_date_delivery" ).datepicker({minDate: 0, maxDate: max_day});
                $("#pickup_date_curb" ).datepicker({minDate: 0, maxDate: max_day});
            }
        });

        ajax.jsonRpc('/delivery/date', 'call', {"ready": 1}).then(function(res) {
            if(res['status'] === false){
                $("#valid_time_delivery_mode" ).css("display", "block !important");
                $("#pro_delivery").click();
                $("#open_time").text(res['open_time']);
                $("#address_confirm" ).css("display", "none");
                $(".all_shipping" ).css("display", "none");
                $("#order_delivery .col-lg-12" ).css("display", "none");
                $("#invalid_location" ).hide();
                $("#custom_your_address" ).hide();
                $("#custom_your_address" ).css("display", "none !important");
                $("#pickup" ).hide();
                $("#pickup" ).css("display", "none !important");
                $("#invalid_time_range").css("display", "none");
                $("#invalid_picking_time").css("display", "none");
                $("#invalid_products").css("display", "none");

            }
            else{
                $("#custom_your_address" ).hide();
                $("#custom_your_address" ).css("display", "none !important");
                $("#valid_time_delivery_mode" ).css("display", "none");
                $("#address_confirm" ).css("display", "block");
                $("#invalid_time_range").css("display", "none");
                $("#invalid_picking_time").css("display", "none");
                $("#invalid_products").css("display", "none");

            }
        });


        ajax.jsonRpc('/delivery/autofill', 'call', {"ready": 1}).then(function(res) {
            if(res === false){

            }
            else{
//               console.log(res);
               if (res['name']) {
                    $("#partner_name").val(res['name']);
                    $("#partner_name_curb").val(res['name']);

               }

                if (res['mobile']) {
                    $("#partner_phone").val(res['mobile']);
                    $("#partner_phone_curb").val(res['mobile']);

               }

               if (res['email']) {
                    $("#partner_email").val(res['email']);
                    $("#partner_email_curb").val(res['email']);

               }

//               if (res['vcolor']) {
//                    $("#v_colour").val(res['vcolor']);
//
//               }
//
//               if (res['plate_no']) {
//                    $("#license_plate_no").val(res['plate_no']);
//
//               }
            }
        });

        ajax.jsonRpc('/pickup/type', 'call', {"ready": 1}).then(function(res) {
            if(res === false){
                $("#curb_disabled" ).css("display", "block");
                $("#curb_enabled" ).css("display", "none");
                $("#pro_delivery_dis" ).css("width", "100% !important");
            }
            else{
                $("#curb_enabled" ).css("display", "block");
                $("#curb_disabled" ).css("display", "none");
            }
        });

        ajax.jsonRpc('/pickup/type/delivery', 'call', {"ready": 1}).then(function(res) {
            if(res === false){
                $("#pro_delivery" ).css("display", "none");
                $("#pro_delivery_dis" ).css("display", "none");
                $(".tab" ).css("border", "none");
            }
            else{
                if ($('#quick_pickup').attr('data-qr') == 'True'){
                    }
                    else{
                        $("#pro_delivery" ).css("display", "block");
                        $("#custom_your_address" ).css("display", "block");
                        $("#order_delivery" ).css("display", "none");
                        $("#pickup" ).css("display", "block");
                        var location =  window.location.href;
                        var is_address = location.includes('shop/address');
                        if (is_address === true){
                            ajax.jsonRpc('/delivery/date', 'call', {"ready": 1}).then(function(res) {
                                if(res['status'] === false){
                                    console.log("YYY", res)
                                    $("#valid_time_delivery_mode" ).css("display", "block !important");
                                    $("#pro_delivery").click();
                                    $("#open_time").text(res['open_time']);
                                    $("#address_confirm" ).css("display", "none");
                                    $(".all_shipping" ).css("display", "none");
                                    $("#order_delivery .col-lg-12" ).css("display", "none");
                                    $("#invalid_location" ).hide();
                                    $("#custom_your_address" ).hide();
                                    $("#pickup" ).hide();
                                }
                                else{
                                    $("#valid_time_delivery_mode" ).css("display", "none");
                                    $("#address_confirm" ).css("display", "block");
                                    $("#custom_your_address" ).hide();
                                    $("#pickup" ).show();
                                    initMap()
                                }
                        });
                            $("#pickup").css("display", "block")
                            initMap()
                        }

                    }
            }
        });
//        var type_vehicle = [];
        ajax.jsonRpc('/get/vehicle/details', 'call', {"ready": 1}).then(function(res) {
            if (res){
                var type_vehicle = res['type'];
                var v_make = res['make'];
                var v_location = res['location'];


                for(var i=0;i<type_vehicle.length;i++){
                    $('#vehicle_type_ids').append('<option value='+type_vehicle[i]+'>'+type_vehicle[i]+'</option>');
                }
                for(var j=0;j<v_make.length;j++){
                    $('#vehicle_make_ids').append('<option value='+v_make[j]+'>'+v_make[j]+'</option>');
                }
                for(var k=0;k<v_location.length;k++){
                    $('#vehicle_location_ids').append('<option value='+v_location[k]+'>'+v_location[k]+'</option>');
                }
                $('#vehicle_location_ids').append('<option value='+'others'+'>'+'Others'+'</option>');
            }
        });

//        $('#pickup_time').timepicker({
////            timeFormat: 'h:mm p',
//            interval: '15',
//            minTime: '11:00am',
//            maxTime: '2:00pm',
//            defaultTime: '11',
//            startTime: '11:00',
//            dynamic: true,
//            dropdown: true,
//            scrollbar: true
//        });

//        $('#pickup_time_curb').timepicker({
//        //timeFormat: 'h:mm p',
//            interval: 60,
//            minTime: '10',
//            maxTime: '6:00pm',
//            defaultTime: '11:00am',
//            startTime: '10:00am',
//            dynamic: true,
//            dropdown: true,
//            scrollbar: true
//        });


        $("#curb_side_pickup").on('click', function() {
            $("#curb_order").css("display", "block");
            $("#pickup").css("display", "none");
            $("div #order_delivery").css("display", "none");
            $("#checkout_footer").css("display", "none");
            $("#delivery_type").val("curb");
            $("#valid_time_delivery_mode" ).css("display", "none");
            var location =  window.location.href;
            var is_address = location.includes('shop/address');

            if (is_address === true){
                $("#custom_your_address").css("display", "none")
            }


            $(".button #pro_pickup").css("border", "1px solid dd2904 !important");
            $(".button #pro_pickup").css("background-color", " #e8d3d2 !important");
            $(".button #pro_delivery").css("border", "1px solid #black !important");
            $(".button #pro_delivery").css("background-color", "#ccc !important");

            $("#invalid_time_curb").css("display", "none");
            $("#less_time_curb").css("display", "none");
            $("#invalid_name_curb").css("display", "none");
            $("#invalid_phone_curb").css("display", "none");
            $("#invalid_email_curb").css("display", "none");
            $("#invalid_time_range_curb").css("display", "none");
            $("#invalid_picking_time_curb").css("display", "none");
            $("#invalid_products").css("display", "none");
            $("#invalid_products_curb").css("display", "none");

            var order_id = document.getElementById("order_id").value;
            var order_name = document.getElementById("order_name").value;
            var delivery_type = "curb"

            var self = this;
            ajax.jsonRpc('/order/delivery', 'call', {"order_id": order_id, "delivery_type":delivery_type})

            $("#order_delivery").css("display", "none");
            $("#pickup").css("display", "none");

        }),


        $("#pro_delivery").on('click', function() {

            $("#curb_order").css("display", "none");
            $(".o_payment_form_pay").removeClass('btn-disabled');
            $("#order_delivery").css("display", "block");
            $("#checkout_footer").css("display", "block");
            $("#pickup").css("display", "none");

            var location =  window.location.href;
            var is_address = location.includes('shop/address');

            if (is_address === true){
                ajax.jsonRpc('/delivery/date', 'call', {"ready": 1}).then(function(res) {
                    if(res['status'] === false){
                        console.log("QQQ", res)
                        $("#valid_time_delivery_mode" ).css("display", "block");
                        $("#open_time").text(res['open_time']);
                        $("#address_confirm" ).css("display", "none");
                        $(".all_shipping" ).css("display", "none");
                        $("#order_delivery .col-lg-12" ).css("display", "none");
                        $("#invalid_location" ).hide();
                        $("#custom_your_address" ).hide();
                    }
                    else{
                        $("#valid_time_delivery_mode" ).css("display", "none");
                        $("#address_confirm" ).css("display", "block");
                        $("#custom_your_address" ).show();
                        initMap()
                    }
                });
            }
            else{
                ajax.jsonRpc('/delivery/date', 'call', {"ready": 1}).then(function(res) {
                    if(res['status'] === false){
                        console.log("VVV", res)
                        $("#valid_time_delivery_mode" ).css("display", "block");
                        $("#open_time").text(res['open_time']);
                        $("#address_confirm" ).css("display", "none");
                        $(".all_shipping" ).css("display", "none");
                        $("#order_delivery .col-lg-12" ).css("display", "none");
                        $("#invalid_location" ).hide();
                        $("#custom_your_address" ).hide();
                    }
                    else{
                        $("#valid_time_delivery_mode" ).css("display", "none");
                        $("#address_confirm" ).css("display", "block");
                        $("#custom_your_address" ).show();
//                        initMap()
                    }
                });
            }
            $(".button #pro_delivery").css("border", "1px solid #dd2904 !important");
            $(".button #pro_delivery").css("background-color", "#e8d3d2 !important");
            $(".button #pro_pickup").css("border", "1px solid black !important");
            $(".button #pro_pickup").css("background-color", " #ccc !important");

            $("div #order_delivery").css("display", "block");
            $("#delivery_type").val("delivery");
            $("#checkout_footer").css("display", "block");
            var order_id = document.getElementById("order_id").value
            var order_name = document.getElementById("order_name").value
            var delivery_type = "delivery"

            ajax.jsonRpc('/order/delivery', 'call', {"order_id": order_id, "delivery_type":delivery_type})
        }),

        $("#pro_pickup").on('click', function() {
            $("#curb_order").css("display", "none");
            $("#pickup").css("display", "block");
            $("div #order_delivery").css("display", "none");
            $("#checkout_footer").css("display", "none");
            $("#delivery_type").val("pickup");
            $("#valid_time_delivery_mode" ).css("display", "none");

            PickUpTime();


            var location =  window.location.href;
            var is_address = location.includes('shop/address');

            if (is_address === true){
                $("#custom_your_address").css("display", "none")
            }


            $(".button #pro_pickup").css("border", "1px solid dd2904 !important");
            $(".button #pro_pickup").css("background-color", " #e8d3d2 !important");
            $(".button #pro_delivery").css("border", "1px solid #black !important");
            $(".button #pro_delivery").css("background-color", "#ccc !important");

            $("#invalid_time").css("display", "none");
            $("#less_time").css("display", "none");
            $("#invalid_name").css("display", "none");
            $("#invalid_phone").css("display", "none");
            $("#invalid_email").css("display", "none");
            $("#invalid_time_range").css("display", "none");
            $("#invalid_picking_time").css("display", "none");
            $("#invalid_products").css("display", "none");
            $("#invalid_products_curb").css("display", "none");

            var order_id = document.getElementById("order_id").value;
            var order_name = document.getElementById("order_name").value;
            var delivery_type = "pickup"

            var self = this;
            ajax.jsonRpc('/order/delivery', 'call', {"order_id": order_id, "delivery_type":delivery_type})

            $("#order_delivery").css("display", "none");
            $("#curb_order").css("display", "none");

        }),
        $("#pro_delivery_dis").on('click', function() {

            $("#curb_order").css("display", "none");
            $(".o_payment_form_pay").removeClass('btn-disabled');
            $("#order_delivery").css("display", "block");
            $("#checkout_footer").css("display", "block");
            $("#pickup").css("display", "none");

            var location =  window.location.href;
            var is_address = location.includes('shop/address');

            if (is_address === true){
                ajax.jsonRpc('/delivery/date', 'call', {"ready": 1}).then(function(res) {
                    if(res['status'] === false){
                        console.log("PPP", res)
                        $("#valid_time_delivery_mode" ).css("display", "block");
                        $("#open_time").text(res['open_time']);
                        $("#address_confirm" ).css("display", "none");
                        $(".all_shipping" ).css("display", "none");
                        $("#order_delivery .col-lg-12" ).css("display", "none");
                        $("#invalid_location" ).hide();
                        $("#custom_your_address" ).hide();
                    }
                    else{
                        $("#valid_time_delivery_mode" ).css("display", "none");
                        $("#address_confirm" ).css("display", "block");
                        $("#custom_your_address" ).show();
                        initMap()
                    }
                });
            }

            $(".button #pro_delivery").css("border", "1px solid #dd2904 !important");
            $(".button #pro_delivery").css("background-color", "#e8d3d2 !important");
            $(".button #pro_pickup").css("border", "1px solid black !important");
            $(".button #pro_pickup").css("background-color", " #ccc !important");

            $("div #order_delivery").css("display", "block");
            $("#delivery_type").val("delivery");
            $("#checkout_footer").css("display", "block");
            var order_id = document.getElementById("order_id").value
            var order_name = document.getElementById("order_name").value
            var delivery_type = "delivery"

            ajax.jsonRpc('/order/delivery', 'call', {"order_id": order_id, "delivery_type":delivery_type})
        }),

        $("#pro_pickup_dis").on('click', function() {
            $("#curb_order").css("display", "none");
            $("#pickup").css("display", "block");
            $("div #order_delivery").css("display", "none");
            $("#checkout_footer").css("display", "none");
            $("#delivery_type").val("pickup");
            $("#valid_time_delivery_mode" ).css("display", "none");

            var location =  window.location.href;
            var is_address = location.includes('shop/address');

            if (is_address === true){
                $("#custom_your_address").css("display", "none")
            }


            $(".button #pro_pickup").css("border", "1px solid dd2904 !important");
            $(".button #pro_pickup").css("background-color", " #e8d3d2 !important");
            $(".button #pro_delivery").css("border", "1px solid #black !important");
            $(".button #pro_delivery").css("background-color", "#ccc !important");

            $("#invalid_time").css("display", "none");
            $("#less_time").css("display", "none");
            $("#invalid_name").css("display", "none");
            $("#invalid_phone").css("display", "none");
            $("#invalid_email").css("display", "none");
            $("#invalid_time_range").css("display", "none");
            $("#invalid_picking_time").css("display", "none");
            $("#invalid_products").css("display", "none");
            $("#invalid_products_curb").css("display", "none");

            var order_id = document.getElementById("order_id").value;
            var order_name = document.getElementById("order_name").value;
            var delivery_type = "pickup"

            var self = this;
            ajax.jsonRpc('/order/delivery', 'call', {"order_id": order_id, "delivery_type":delivery_type})

            $("#order_delivery").css("display", "none");
            $("#curb_order").css("display", "none");

        }),
        $("#continue_button").on('click', function() {
            $("#order_delivery").css("display", "none");
            $("#less_time").css("display", "none");
            $("#invalid_name").css("display", "none");
            $("#invalid_phone").css("display", "none");
            $("#invalid_email").css("display", "none");
            $("#invalid_time_range").css("display", "none");
            $("#invalid_picking_time").css("display", "none");
            $("#invalid_products").css("display", "none");
            $("#invalid_products_curb").css("display", "none");

            var order_id = document.getElementById("order_id").value;
            var order_name = document.getElementById("order_name").value;
            var pickup_date = document.getElementById("pickup_date").value;
            var pickup_time = document.getElementById("pickup_time").value;
            var partner_name = document.getElementById("partner_name").value;
            var partner_phone = document.getElementById("partner_phone").value;
            var partner_email = document.getElementById("partner_email").value;
            var phone_regex =   /^\d+$/;
            var phone_valid =  phone_regex.test(partner_phone);
            var email_regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
            var email_valid =  email_regex.test(partner_email);
            var v_time = true
            var v_name = true
            var v_phone = true
            var v_email = true

            var vehicle_color = "";
            var license_plate_no = "";
            var v_type = "";
            var v_make = "";
            var v_location = "";
            var location_note = ''

            var method = "pickup"
            if(!pickup_time){
                v_time = false
            }
            if(!partner_name){
                v_name = false
                $("#invalid_name").css("display", "block");
            }
            if (phone_valid === false){
                var v_phone = false
                $("#invalid_phone").css("display", "block");
            }
            if (email_valid === false){
                var v_email = false
                $("#invalid_email").css("display", "block");
            }

            var location =  window.location.href;
            var is_address = location.includes('shop/address');
            var is_checkout = location.includes('shop/checkout');
            var d_type = ""
            if (is_address === true){
                d_type = "public"
            }
            if (is_checkout === true){
                d_type = "user"
            }
            var time_ok = true
            ajax.jsonRpc('/order/time/range', 'call', {"pickup_date": pickup_date, "pickup_time":pickup_time, "order_id":order_id, "delivery_type": d_type, "method": method, "vehicle_color": vehicle_color, "license_plate_no": license_plate_no, "v_type": v_type,"v_make": v_make, "v_location":v_location, "location_note":location_note}).then(function(res) {
                    console.log("333", res);
                    if(res.time_ok === false){
                        console.log("444")
                        time_ok = false
                        $("#invalid_time_range").css("display", "block");

                         if (res.next_date){
                            $("#open_day").text(res.next_date);
                            $("#opening_time").text(res.opening_time);
                        }

                    }
                    else if(res.time_ok === true){
                        if ((v_time === true) && (v_name === true) && (v_phone === true) && (v_email === true)){
                            $("#order_delivery").css("display", "none");
                            $("#continue_div").css("display", "none");
                            console.log(" PICKUP")
                            ajax.jsonRpc('/order/pickup/time', 'call', {"pickup_date": pickup_date, "pickup_time":pickup_time, "order_id":order_id, "partner_name":partner_name, "partner_phone": partner_phone, "partner_email": partner_email, "delivery_type": d_type}).then(function(res) {
                                if(res === true){
                                    console.log("TRUE PICKUP")
                                    window.location.href = "/shop/payment"
                                }
                                else{
                                    console.log("FALSE PICKUP")
                                    window.location.href = "/shop/payment"
                                }
                            });

                        }
                    }
                    else if(res['status'] == 'none'){
                        print("ttt")
                        $("#invalid_time_range").css("display", "block");
                         if (res.next_date){
                            print("lll")
                            $("#open_day").text(res.next_date);
                            $("#opening_time").text(res.opening_time);
                        }
                    }
                    else if(res['status'] == 'invalid_products'){
                        $("#invalid_products").css("display", "block");
                    }
                    else if(res['status'] == 'invalid_pickup'){
                        $("#invalid_pick").text(res['warning']);
                        $("#invalid_picking_time").css("display", "block");
                    }
                    else if(res['status'] == 'invalid'){
                        $("#less_time").css("display", "block");

                        if (res['time_hr'] != '00'){
                            $("#min_hr").text(res['time_hr']);
                        }
                        if (res['time_hr'] == '00'){
                            $("#min_hr").text(res['time_hr']);
                        }
                        if(res['time_minute'] != '00'){
                            $("#min_time").text(res['time_minute']);
                        }
                        else if(res['time_minute'] == '00'){
                            $("#min_time").text(res['time_minute']);
                        }
                    }
                    else{

                    }
                });
        }),

        $("#continue_button_curb").on('click', function() {
            $("#order_delivery").css("display", "none");
            $("#less_time_curb").css("display", "none");
            $("#invalid_name_curb").css("display", "none");
            $("#invalid_phone_curb").css("display", "none");
            $("#invalid_email_curb").css("display", "none");
            $("#invalid_time_range_curb").css("display", "none");
            $("#invalid_picking_time_curb").css("display", "none");
            $("#invalid_products").css("display", "none");
            $("#invalid_products_curb").css("display", "none");
            var order_id = document.getElementById("order_id").value;
            var order_name = document.getElementById("order_name").value;
            var pickup_date = document.getElementById("pickup_date_curb").value;
            var pickup_time = document.getElementById("pickup_time_curb").value;
            var partner_name = document.getElementById("partner_name_curb").value;
            var partner_phone = document.getElementById("partner_phone_curb").value;
            var partner_email = document.getElementById("partner_email_curb").value;

            var v_type = $('#vehicle_type_ids').find(":selected").text();
            var v_make = $('#vehicle_make_ids').find(":selected").text();
            var v_location = $('#vehicle_location_ids').find(":selected").text();

            var vehicle_color = document.getElementById("v_colour").value;
            var license_plate_no = document.getElementById("license_plate_no").value;
            var location_note = document.getElementById("location_note").value;

            var phone_regex =   /^\d+$/;
            var phone_valid =  phone_regex.test(partner_phone);
            var email_regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
            var email_valid =  email_regex.test(partner_email);
            var v_time = true
            var v_name = true
            var v_phone = true
            var v_email = true
            var v_color = true
            var v_license = true
            var method = "curb"
            if(!pickup_time){
                v_time = false
            }
            if(!partner_name){
                v_name = false
                $("#invalid_name_curb").css("display", "block");
            }
            if (phone_valid === false){
                var v_phone = false
                $("#invalid_phone_curb").css("display", "block");
            }
            if (email_valid === false){
                var v_email = false
                $("#invalid_email_curb").css("display", "block");
            }
            if(!vehicle_color){
                v_color = false
                $("#invalid_vehicle_color_curb").css("display", "block");
            }
            if(!license_plate_no){
                v_license = false
                $("#invalid_license_plate_no_curb").css("display", "block");
            }

            var location =  window.location.href;
            var is_address = location.includes('shop/address');
            var is_checkout = location.includes('shop/checkout');
            var d_type = ""
            if (is_address === true){
                d_type = "public"
            }
            if (is_checkout === true){
                d_type = "user"
            }
            var time_ok = true
            ajax.jsonRpc('/order/time/range', 'call', {"pickup_date": pickup_date, "pickup_time":pickup_time, "order_id":order_id, "delivery_type": d_type, "method": method, "v_type": v_type,"v_make": v_make, "v_location":v_location, "vehicle_color": vehicle_color, "license_plate_no": license_plate_no, "location_note":location_note}).then(function(res) {
                    if(res.time_ok === false){
                        console.log("t", res.next_date)
                        time_ok = false
                        $("#invalid_time_range_curb").css("display", "block");

                        if (res.next_date){
                            $("#open_day_curb").text(res.next_date);
                            $("#opening_time_curb").text(res.opening_time);
                        }
                    }
                    else if(res.time_ok === true){
                        if ((v_time === true) && (v_name === true) && (v_phone === true) && (v_email === true) && (v_color === true) && (v_license === true)){
                            $("#order_delivery").css("display", "none");
                            $("#pickup").css("display", "none");
                            $("#continue_div_curb").css("display", "none");
                            console.log(" CURB")
                            ajax.jsonRpc('/order/pickup/time', 'call', {"pickup_date": pickup_date, "pickup_time":pickup_time, "order_id":order_id, "partner_name":partner_name, "partner_phone": partner_phone, "partner_email": partner_email, "delivery_type": d_type}).then(function(res) {
                                if(res === true){
                                    console.log("TRUE CURB")
                                    window.location.href = "/shop/payment"
                                }
                                else{
                                    console.log("FALSE CURB")
                                    window.location.href = "/shop/payment"
                                }
                            });

                        }
                    }
                    else if(res['status'] == 'none'){
                        $("#invalid_time_range_curb").css("display", "block");

                        if (res.next_date){
                            $("#open_day_curb").text(res.next_date);
                            $("#opening_time_curb").text(res.opening_time);
                        }
                    }
                    else if(res['status'] == 'invalid_products'){
                        $("#invalid_products_curb").css("display", "block");
                    }
                    else if(res['status'] == 'invalid_pickup'){
                        $("#invalid_pick_curb").text(res['warning']);
                        $("#invalid_picking_time_curb").css("display", "block");
                    }
                    else if(res['status'] == 'invalid'){
                        $("#less_time_curb").css("display", "block");

                        if (res['time_hr'] != '00'){
                            $("#min_hr_curb").text(res['time_hr']);
                        }
                        if (res['time_hr'] == '00'){
                            $("#min_hr_curb").text(res['time_hr']);
                        }
                        if(res['time_minute'] != '00'){
                            $("#min_time_curb").text(res['time_minute']);
                        }
                        else if(res['time_minute'] == '00'){
                            $("#min_time_curb").text(res['time_minute']);
                        }
                    }
                    else{

                    }
                });
        })
    })


function PickUpTime()
{
    // date calculation pickup
    var pickup_date = '';
    try{
        pickup_date = document.getElementById("pickup_date").value;

    }
    catch(err){
        console.log();
    }

    if (pickup_date==''){
    pickup_date = "Today";
                  }

    ajax.jsonRpc('/get/time/cooking', 'call', {"ready": 1,"picking_date":pickup_date}).then(function(res) {
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
                $('#pickup_time').append('<option value='+tm+'>'+tm+'</option>');
                time30 = tm;
                }
                }
                else
                {
                var tm = moment(time15,'HH:mm').add(5,'minutes').format('HH:mm');
                $('#pickup_time').append('<option value='+tm+'>'+tm+'</option>');
                time15 = tm;
                }
                }
                }
            else{
                $("#pickup_time").hide();
             }
        }
        else{
            $("#pickup_time").hide();
        }
        }
        else{
        $("#pickup_time").hide();
        }
        }
        catch(err){
        console.log(err)
        }
		});
}



function PickUpTimeCurb()
{
    // date calculation pickup
    var pickup_date = '';
    try{
        pickup_date = document.getElementById("pickup_date_curb").value;

    }
    catch(err){
        console.log();
    }

    if (pickup_date==''){
    pickup_date = "Today";
                  }

     ajax.jsonRpc('/get/time/cooking/curb', 'call', {"ready": 1,"picking_date":pickup_date}).then(function(res) {
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
                $('#pickup_time_curb').append('<option value='+tm+'>'+tm+'</option>');
                time30 = tm;
                }
                }
                else
                {
                var tm = moment(time15,'HH:mm').add(5,'minutes').format('HH:mm');
                $('#pickup_time_curb').append('<option value='+tm+'>'+tm+'</option>');
                time15 = tm;
                }
                }
                }
            else{
                $("#pickup_time_curb").hide();
             }
        }
        else{
            $("#pickup_time_curb").hide();
        }
        }
        else{
        $("#pickup_time_curb").hide();
        }
        }
        catch(err){
        console.log(err)
        }

		});
}
});