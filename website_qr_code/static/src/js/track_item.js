odoo.define('website_qr_code.track_item', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;
var ajax = require('web.ajax');
//ajax.loadJS("/website_qr_code/static/src/counters/kinetic.js");
//ajax.loadJS("/website_qr_code/static/src/counters/jquery.final-countdown.js");
//ajax.loadCSS("/website_qr_code/static/src/counters/bootstrap.min.css");
//ajax.loadCSS("/website_qr_code/static/src/counters/demo.css");


publicWidget.registry.quick_pickup_track_item = publicWidget.Widget.extend({
    selector: '#calculate_tarck_item_new',
    events: {
//        'click #top_menu a[href="/shop"]': '_onshop_click',
//        'mouseover .tip_class_category': 'hover_tip_class_category',
//        'click .tip_class_category': '__tip_class_category',
//        'click #continue_button_quick': '_continue_button_quick',
//        'click #dine_in': '_dine_in',
//        'click #take_away': '_take_away',
    },
//    /**
//     * @constructor
//     */
    init: function () {
        var self = this;
        var sale_id = $('#flipper_timer').attr('data-id')
        if(sale_id){
            self.ajax_long_pooling();
        }

//        if (sale_id){
//            ajax.jsonRpc('/shop/order/number', 'call', { 'data': sale_id}).then(function(data) {
//                if(data) {
//                    console.log("data",data)
//                    var time_rem = data['preparation_estimation'][0].match(/(?<=\s).*/g);
//                    var startDate = new Date();
//                    var endDate = new Date(data['preparation_estimation'][0]);
//                    var diff = endDate - startDate
//                    var minutes = Math.floor(diff/1000);
//                    var clock;
//                     console.log("success123",minutes);
//                    if (minutes >=0){
//                        clock = $('#flipper_timer').FlipClock({
//                                clockFace: 'MinuteCounter',
//                                autoStart: false,
//                                callbacks: {
//                                    stop: function() {
//                                            window.location.reload();
//                                    }
//                                }
//                            });
//                            clock.setTime(minutes);
//                            clock.setCountdown(true);
//                            clock.start();
//                    }
//                    else{
//                        if (data['state'] === 'waiting' || data['state'] === 'preparing' || data['state'] === 'ready' || data['state'] === 'delivering'){
//                            $('.contact_success').show();
//                             setTimeout(function () {
//                                   $('.contact_success').hide();
//                                    }, 6000);
//                        }
//
//                    }
//                }else{
//                    if (data['state'] === 'waiting' || data['state'] === 'preparing' || data['state'] === 'ready' || data['state'] === 'delivering'){
//                        $('.contact_success_tech').show();
//                          setTimeout(function () {
//                                   $('.contact_success_tech').hide();
//                                    }, 6000);
//                    }
//                }
//            });
//        }
        this._super.apply(this, arguments);
    },
    ajax_long_pooling() {
            var self = this;
            var sale_id = $('#flipper_timer').attr('data-id')
                var dataToLog = {'data': sale_id};
                 $.ajax({
                        type: 'POST',
                        url: '/shop/order/number',
                        async: true,
                        processData: true,
                        beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                        data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),

                        success: function(data) {
                            if (data.result) {

                                var startDate = new Date();
                                var endDate = new Date(data.result['preparation_estimation']);
                                var diff = endDate - startDate
                                var minutes = Math.floor(diff/1000);
                                var clock;
                                if (data.result['state'] === 'done' || data.result['state'] === 'cancel' || data.result['state'] === 'return'){
                                    if(self.clock){
                                        self.clock.stop();
                                    }
                                    if(data.result['state'] === 'done'){
                                        $('.contact_success_waiting').show();
                                        setTimeout(function () {
                                                   $('.contact_success_waiting').hide();
                                                    }, 6000);
                                    }

                                }
                                if (minutes >=0 && data.result['state'] != 'done' && data.result['state'] != 'cancel' && data.result['state'] != 'return'){
                                    self.clock = $('#flipper_timer').FlipClock({
                                            clockFace: 'MinuteCounter',
                                            autoStart: false,
                                            callbacks: {
                                                stop: function() {
                                                        window.location.reload();
                                                }
                                            }
                                     });

                                    self.clock.setTime(minutes);
                                    self.clock.setCountdown(true);
                                    self.clock.start();
                                }else{
                                    if (data['state'] === 'waiting' || data['state'] === 'preparing' || data['state'] === 'ready' || data['state'] === 'delivering'){
                                            $('.contact_success').show();
                                             setTimeout(function () {
                                                   $('.contact_success').hide();
                                                    }, 6000);
                                        }
                                }
                            $('#cart_products').load(window.location.href + " #cart_products" );
//                            $('#flipper_timer').load(window.location.href + " #flipper_timer" );

                            }
                             setTimeout(function(){
                                   self.ajax_long_pooling();
                                }, 90* 1000);

                        },

                        error: function (jqXHR, status, err) {
                            setTimeout(function(){
                               self.ajax_long_pooling();
                            }, 80000);
                        },

                        timeout: 40000,
                    })
    }

    });
});