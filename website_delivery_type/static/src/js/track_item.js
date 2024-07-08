odoo.define('website_delivery_type.track_item', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;
var ajax = require('web.ajax');


publicWidget.registry.delivery_track_item = publicWidget.Widget.extend({
    selector: '.delivery_timing',
    events: {
    },
//    /**
//     * @constructor
//     */
    init: function () {
        var self = this;
        var sale_id = $('#flipper_timer_delivery').attr('data-id')
        if(sale_id){
            self.ajax_long_pooling();
        }

        this._super.apply(this, arguments);
    },
    ajax_long_pooling() {
            var self = this;
            var sale_id = $('#flipper_timer_delivery').attr('data-id')
                var dataToLog = {'data': sale_id};
                 $.ajax({
                        type: 'POST',
                        url: '/shop/order/number/delivery',
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
                                    self.clock = $('#flipper_timer_delivery').FlipClock({
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