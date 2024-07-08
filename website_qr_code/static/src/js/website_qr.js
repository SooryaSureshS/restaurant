odoo.define('website_qr_code.website_qr', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;
var ajax = require('web.ajax');

publicWidget.registry.quick_pickup = publicWidget.Widget.extend({
    selector: '#quick_pickup',
    events: {
        'click #continue_button_quick': '_continue_button_quick',
        'click #dine_in': '_dine_in',
        'click #take_away': '_take_away',
    },
//    /**
//     * @constructor
//     */
    init: function () {
        var self = this;
        console.log("quick_pickup",self)
        console.log("quick_pickup",$('#quick_pickup').attr('data-qr'))
        if ($('#quick_pickup').attr('data-qr') == 'True'){
            $('.delivery_type').hide();
        }
//        $('#grumble2').grumble(
//				{
//				text: 'We have a different service model at On it Burgers <br/><br/> For all of your order,whether it is Dine in or Takeaway, please collect from;<br/><br/>Bar Area;all of your drinks <br/> Kitchen; all of your food',
//                angle: 180,
//                distance: 0,
//                showAfter: 2000,
//                type: 'alt-',
//                hideAfter: 2000
//				}
//			);$('#grumble2').grumble(
//				{
//				text: 'We have a different service model at On it Burgers <br/><br/> For all of your order,whether it is Dine in or Takeaway, please collect from;<br/><br/>Bar Area;all of your drinks <br/> Kitchen; all of your food',
//                angle: 180,
//                distance: 0,
//                showAfter: 2000,
//                type: 'alt-',
//                hideAfter: 2000
//				}
//			);
        this._super.apply(this, arguments);

    },
    _dine_in: function (ev){
        var self = this;
//        $('#dine_in_website_order').val('dine')
        var $target = $(ev.currentTarget);
//        $('#grumble2').grumble(
//				{
//				text: 'We have a different service model at On it Burgers <br/><br/> For all of your order,whether it is Dine in or Takeaway, please collect from;<br/><br/>Bar Area;all of your drinks <br/> Kitchen; all of your food',
//                angle: 180,
//                distance: 0,
//                showAfter: 2000,
//                type: 'alt-',
//                hideAfter: 2000
//				}
//			);
         $target.css('background-color','rgba(255, 0, 0, .2)');
         $target.css('border','2px solid rgba(255, 0, 0, 1)');
         $target.css('border-top','2px solid rgba(255, 0, 0, 1) !important');
         var order = $target.attr('data-order')
         console.log("orderd idf ",order);
         this._rpc({
                    route: "/shop/update/dine_in",
                    params: {
                        data: 'dine_in',

            },
        }).then(function (data) {

             $('#quick_pickup').load(window.location.href + " #quick_pickup" );
        });
    },
    _take_away: function (ev){
        var self = this;
//        $('#dine_in_website_order').val('take')
        var $target = $(ev.currentTarget);
//        $('#grumble2').grumble(
//				{
//				text: 'We have a different service model at On it Burgers <br/><br/> For all of your order,whether it is Dine in or Takeaway, please collect from;<br/><br/>Bar Area;all of your drinks <br/> Kitchen; all of your food',
//                angle: 180,
//                distance: 0,
//                showAfter: 2000,
//                type: 'alt-',
//                hideAfter: 2000
//				}
//			);

         $target.css('background-color','rgba(255, 0, 0, .2)');
         $target.css('border','2px solid rgba(255, 0, 0, 1)');
         $target.css('border-top','2px solid rgba(255, 0, 0, 1) !important');
         var order = $target.attr('data-order')
         console.log("orderd idf ",order);
         this._rpc({
                    route: "/shop/update/dine_in",
                    params: {
                        data: 'take_away',

                    },
                }).then(function (data) {
                       $('#quick_pickup').load(window.location.href + " #quick_pickup" );
                });
    },
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


publicWidget.registry.timeline_js_vals = publicWidget.Widget.extend({
    selector: '#timeline_js_vals',
    events: {
//        'click #top_menu a[href="/shop"]': '_onshop_click',
//        'mouseover .tip_class_category': 'hover_tip_class_category',
//        'click .tip_class_category': '__tip_class_category',
//        'click #continue_button_quick': '_continue_button_quick',
//        'click #dine_in': '_dine_in',
//        'click #take_away': '_take_away',
    },
      init: function () {
        var self = this;
        var data = [
	{
		time: '2016-01-20',
		body: [
		{
			tag: 'h6',
			content: 'Collect your food/drinks'
		},]
	},
	{
		time: '2016-01-21',
		body: [{
			tag: 'h6',
			content: 'Check your email inbox to track your order'
		},]
	},
	{
		time: '2016-01-22',
		body: [{
			tag: 'h6',
			content: 'Upon Payment Below'
		},]
	}
];

        var data1 = [
	{
		time: '2016-01-20',
		body: [
		{
			tag: 'h6',
			content: 'Your order will be delivered to your table'
		},]
	},
	{
		time: '2016-01-21',
		body: [{
			tag: 'h6',
			content: 'Check your email inbox to track your order'
		},]
	},
	{
		time: '2016-01-22',
		body: [{
			tag: 'h6',
			content: 'Upon Payment Below'
		},]
	}
];

        console.log("quick_pickup",self)

        var dine_in = $('#timeline_js_vals').attr('data-dine-in')
        if (dine_in == 'True'){
             $('#timeline_js_vals').albeTimeline(data1);
        }else{
             $('#timeline_js_vals').albeTimeline(data);

        }

//        console.log("quick_pickup",$('#quick_pickup').attr('data-qr'))
//        if ($('#quick_pickup').attr('data-qr') == 'True'){
//            $('.delivery_type').hide();
//        }
        this._super.apply(this, arguments);

    },
    });

});