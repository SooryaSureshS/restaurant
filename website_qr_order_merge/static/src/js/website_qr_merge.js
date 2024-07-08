odoo.define('website_qr_order_merge.website_qr_merge', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;
var ajax = require('web.ajax');


publicWidget.registry.quick_pickup.include({
    _continue_button_quick: function (ev){
        var self = this;
        var $target = $(ev.currentTarget);
        var name = $('#partner_name_quick').val();
        var phone = $('#partner_phone_quick').val();
        var email = $('#partner_email_quick').val();
        var table = $('#din_in_table_selection').val();
        var order_type = $('#dine_in_website_order').val();
        var count = 0;
        var mailformat = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/
        if(email.match(mailformat))
        {
            count = count + 1;
        }else{
            $('#partner_email_quick').val("")
            $('#partner_email_quick').focus();
            $('#invalid_time_range_data').show();
            $('#invalid_fields_qr').html("Email Is Not Correct")
             setTimeout(function () {
                $('#invalid_time_range_data').hide();
                }, 1000);
        }
        if(name.length>0){
            count = count + 1;
        }else{
            $('#partner_name_quick').val("")
            $('#partner_name_quick').focus();
            $('#invalid_time_range_data').show();
            $('#invalid_fields_qr').html("Please enter name")
             setTimeout(function () {
                $('#invalid_time_range_data').hide();
                }, 1000);
        }
        if(phone.length>0){
            count = count + 1;
        }else{
            $('#partner_phone_quick').val("")
            $('#partner_phone_quick').focus();
            $('#invalid_time_range_data').show();
            $('#invalid_fields_qr').html("Please enter valid phone number")
            setTimeout(function () {
                $('#invalid_time_range_data').hide();
            }, 1000);
        }
        if(count == 3){
            if (order_type == 'dine_in'){
                if (table == 'failed'){
                    $('#invalid_time_range_data').show();
                    $('#invalid_fields_qr').html("Please select a table")
                    setTimeout(function () {
                        $('#invalid_time_range_data').hide();
                    }, 2000);
                }
                else{


                        this._rpc({
                            route: "/shop/merge/check",
                            params: {
                                name: name,
                                phone: phone,
                                email: email,
                                table: table
                            },
                        }).then(function (data) {

                                console.log("events s s",data)
                                if (data['status'] == 'merge'){
                                    if (data['merge_order']){
                                        console.log("merge orders",data['merge_order']);
                                        console.log("merge orders",data['partner']);
                                        var dialog = bootbox.dialog({
                                                title: 'The Table '+data['table']+ ' Is Already Taken',
                                                message: "<p>HI " +name+ " do you want to merge the order with " +data['partner']+ "</p>",
                                                size: 'large',
                                                buttons: {
                                                    cancel: {
                                                        label: "Cancel Merge",
                                                        className: 'btn-danger',
                                                        callback: function(){
                                                               self._rpc({
                                                                    route: "/shop/cart/address/update",
                                                                    params: {
                                                                        name: name,
                                                                        phone: phone,
                                                                        email: email,
                                                                        table: table
                                                                    },
                                                                }).then(function (data) {
                                                                    if(data['status'] == 'invalid_products'){
                                                                        alert("Warning!\nSome of the products in the cart are not eligible for Take Away. Please remove it and try again")
                                                                    }
                                                                    else if (data){
                                                                        window.location.href = "/shop/payment"

                                                                    }

                                                                });
                                                        }
                                                    },
                                                    ok: {
                                                        label: "Merge Order",
                                                        className: 'btn-info',
                                                        callback: function(){
                                                                 self._rpc({
                                                                    route: "/shop/cart/address/merge",
                                                                    params: {
                                                                        name: name,
                                                                        phone: phone,
                                                                        email: email,
                                                                        table: table,
                                                                        parent_id:data['parent_id'],
                                                                    },
                                                                }).then(function (data) {
                                                                    if(data['status'] == 'invalid_products'){
                                                                        alert("Warning!\nSome of the products in the cart are not eligible for Take Away. Please remove it and try again")
                                                                    }
                                                                    else if (data){
                                                                        window.location.href = "/shop/payment"

                                                                    }

                                                                });
                                                        }
                                                    }
                                                }
                                            });
                                    }
                                }
//                            if(data['status'] == 'invalid_products'){
//                                alert("Warning!\nSome of the products in the cart are not eligible for Take Away. Please remove it and try again")
//                            }
//                            else if (data){
//                                window.location.href = "/shop/payment"
//
//                            }
                            if (data['status'] == 'ok'){
                                   console.log("qqqqqqqqqqqqqqqqqqqqqqeeeeeeeeeeeeeeee",data)
                                   self._rpc({
                                        route: "/shop/cart/address/update",
                                        params: {
                                            name: name,
                                            phone: phone,
                                            email: email,
                                            table: table
                                        },
                                    }).then(function (data) {
                                        if(data['status'] == 'invalid_products'){
                                            alert("Warning!\nSome of the products in the cart are not eligible for Take Away. Please remove it and try again")
                                        }
                                        else if (data){
                                            window.location.href = "/shop/payment"

                                        }

                                    });
                            }

                        });


                }
            }
            else{

            this._rpc({
                    route: "/shop/cart/address/update",
                    params: {
                        name: name,
                        phone: phone,
                        email: email,
                        table: false
                    },
                }).then(function (data) {
                    if(data['status'] == 'invalid_products'){
                        alert("Warning!\nSome of the products in the cart are not eligible for Take Away. Please remove it and try again")
                    }
                    else if (data){
                        window.location.href = "/shop/payment"

                    }

                });
            }
        }
    },
});
});