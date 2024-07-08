odoo.define('website_delivery_type.kerbside_update_address', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;
var ajax = require('web.ajax');
var ServicesMixin = require('web.ServicesMixin');


publicWidget.registry.kerbside_update_address = publicWidget.Widget.extend({
    selector: '#order_address_update_new',
    events: {
        'click #update_button_curb_address_update': '_update_button_curb_address_update',
    },

    init: function () {
        var self = this;
        this._super.apply(this, arguments);
    },
    _update_button_curb_address_update: function (ev){
        var self = this;
        var $target = $(ev.currentTarget);
        var v_location = $('#vehicle_location_ids').find(":selected").text();
        var location_note = document.getElementById("location_note").value;
        var order_id = document.getElementById("order_id").value;

        var v_color = true
        var v_license = true

        console.log("Order: ", order_id)
        console.log("Location: ", v_location)
        console.log("Note: ", location_note)
        if((v_color === true) && (v_license === true)){
            this._rpc({
                    route: "/order/update/vehicle/details",
                    params: {
                        order_id: order_id,
                        v_location: v_location,
                        location_note: location_note,
                    },
                }).then(function (data) {
                    if(data === true){
                        alert("Success!\nLocation Updated")
//                        window.location.href = "/shop/confirmation"
                    }
                    else if(data == 'delivered'){
                        alert("Failed!\nDelivery already done for this order")
//                        window.location.href = "/shop/confirmation"
                    }
                    else if(data == 'no_order'){
                        alert("Failed!\nCould'nt find the order, Please try again later")
//                        window.location.href = "/shop/confirmation"
                    }
                    else{
                        alert("Failed!\nSome error occurred, Please try again later")
//                        window.location.href = "/shop/confirmation"
                    }
                });
            }
        },
    });
});