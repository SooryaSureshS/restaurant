odoo.define('checkout_order_note.check_out', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;

publicWidget.registry.check_out = publicWidget.Widget.extend({
    selector: '#cart_products',
    events: {
        'keydown #checkout_note_id': 'checkout_note_id_change',
    },
//    /**
//     * @constructor
//     */
    init: function () {
        var self = this;
        this._super.apply(this, arguments);
        this._rpc({
                    route: "/checkout/order/note",
                    params: {
                    },
                }).then(function (data) {
                    console.log("draft orders",data)
                    if(data){
                        $('#checkout_note_id').val(data)
                    }
                });
    },
    checkout_note_id_change: function (ev){
        var self = this;
        var value = $(ev.currentTarget).val();
        setTimeout(function(){
            var value = $(ev.currentTarget).val();
            if (value){
                    self._rpc({
                            route: "/checkout/order/note/update",
                            params: {
                                value: value,
                            },
                        }).then(function (data) {
                            return
                        });
                }

         }, 1000);



    },

});
});