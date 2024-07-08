odoo.define('busy_banner.busy_banner', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;
var ajax = require('web.ajax');
var ServicesMixin = require('web.ServicesMixin');

publicWidget.registry.busy_banners = publicWidget.Widget.extend({
    selector: '#bizople_header',
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
        self.popup_timing = 50
//        utils.set_cookie('qr_order', true,2)
        ajax.jsonRpc('/check/auth/banner', 'call', {}).then(function(data) {
            if(data.status){
                if(data.order){
                    utils.set_cookie('qr_order', data.order,7200)
//                    self.ajax_long_pooling()
                    if(data.popup_timing){
                        self.popup_timing = data.popup_timing
                    }

                }

            }
        });

        self.ajax_long_pooling()
        this._super.apply(this, arguments);

    },
    ajax_long_pooling() {
            var self = this;
            var current_qr_order = utils.get_cookie('qr_order')
            var dataToLog = {'data': current_qr_order};
            if(current_qr_order && current_qr_order != 'null'){
                 $.ajax({
                        type: 'POST',
                        url: '/check/banner',
                        async: true,
                        processData: true,
                        beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                        data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),

                        success: function(data) {
                            if (data.result) {
                                if(data.result.estimation){
//                                    var time_rem = data.result.estimation.match(/(?<=\s).*/g);
                                    var startDate = new Date();
                                    var endDate = new Date(data.result.estimation);
                                    var diff = endDate - startDate
                                    var minutes = Math.floor(diff/1000);
                                    if(minutes <0){
                                    if(data.result.status === 'sale'){
                                         Topper({
                                            title: data.result.banner_title,
                                            text: data.result.banner_body,
                                            style: 'danger',
                                            type: 'top',
                                            autoclose: true,
                                            autocloseAfter: 20000
                                        });
                                    }
                                    }

                                }
                                if(data.result.process_kill){
                                    utils.set_cookie('qr_order',null)
                                }
                            }
                             setTimeout(function(){
                                   self.ajax_long_pooling();
                                }, self.popup_timing * 1000);

                        },

                        error: function (jqXHR, status, err) {
                            setTimeout(function(){
                               self.ajax_long_pooling();
                            }, 80000);
                        },

                        timeout: 40000,
                    });
            }

    }
    });

});