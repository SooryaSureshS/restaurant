odoo.define('website_delivery_type.location_check_radius', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;
    var session = require('web.session');
    var utils = require('web.utils');
    var timeout;
        var ajax = require('web.ajax');


    publicWidget.registry.check_delivery_times = publicWidget.Widget.extend({
        selector: '#address_page_form',
        events: {
            'click #check_distance': '_check_distance',
            'click #check_distance_night': '_check_distance_night',
        },
        init: function () {

            var self = this;
            this._super.apply(this, arguments);
            console.log("daddadadad")

        },
        _check_distance: function(event){
            event.stopPropagation();
             var street1 = $("#street1").val();
               var street2 = $("#street2").val();
               var city = $("#city").val();
               var zip = $("#zip").val();
               var order_id_country_name = $("#order_id_country_name").val();
               var order_id_state = $("#order_id_state").val();
               var order_company_id = $("#order_company_id").val();
               if (street1 && street2 && city && zip){
                    $.ajax({
                          type: "POST",
                          url: window.location.origin+'/calculate/lat/lang',
                          data: {'street1':street1,'city':city,'zip':zip,'order_id_country_name':order_id_country_name,'order_id_state':order_id_state,'order_company_id':order_company_id},
                          success: function(data){
                            var info = JSON.parse(data);
                            if (info){
                                console.log("info",info)
                                if (info['flag'] == 1){
                                    swal(
                                        info['status'],
                                      'Your location is '+info['distance']+'km Away',
                                      'error'
                                    )
                                }
                                if (info['flag'] == 2){
                                    console.log("submitted for form")
//                                    $('#address_page_form')
                                     var $form = $(event.currentTarget).closest('form');
                                    $form.submit();
                                }
                            }else{
                                alert("Can't Process location please check the address")
                            }
                          }
                     });
               }else{
                     alert( "Sorry Please check the address fields.." );
               }
        },
        _check_distance_night: function(event){
            event.stopPropagation();
               var street1 = $("#street1").val();
               var street2 = $("#street2").val();
               var city = $("#city").val();
               var zip = $("#zip").val();
//               var order_id_country_name = $("#order_id_country_name").val();
//               var order_id_state = $("#order_id_state").val();
//               var order_company_id = $("#order_company_id").val();
               var name = $(".div_name input").val();
               var phone = $("#div_phone input").val();
               if (street1 && street2 && city && zip && name && phone){
                    var $form = $(event.currentTarget).closest('form');
                                    $form.submit();
               }else{
                    alert("Please fill the fields")
               }
        }

    });


});