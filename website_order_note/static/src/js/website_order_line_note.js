odoo.define('website_order_note.website_order_line_note', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;
var ajax = require('web.ajax');
var qweb = core.qweb;

publicWidget.registry.website_order_line_note = publicWidget.Widget.extend({
    selector: '#cart_products',
    xmlDependencies: ['/website_order_note/static/src/xml/checkout_popup.xml'],
    events: {
        'click tbody td .order_line_note': '_order_line_note_update',
        'click .onit_note_confirm': '_onit_note_confirm',
        'click .onit_note_cancel': '_onit_note_confirm',
    },
//    /**
//     * @constructor
//     */
    init: function () {
        this._super.apply(this, arguments);
    },
    _order_line_note_update: function (events){
        var self = this;
        var order_id = $(events.currentTarget).attr('data_order_id');
        if (order_id) {
            console.log("target",order_id);
//            $('#guest_checkout_page').load(window.location.href + " #guest_checkout_page" );
//            self.$el.prepend(qweb.render('website_extented.size_popup', {'validation_topic': 'You have a message','product':data}));

            ajax.jsonRpc('/sale/line/note', 'call', {'order_id':  order_id})
                .then(function (result) {
                    console.log("odoo data from sale",result);
                    if (result){
                        self.$el.prepend(qweb.render('website_order_note.popup_view', {'info':result}));
                    }else{
                        self.$el.prepend(qweb.render('website_order_note.popup_view', {'info':result}));
                    }
            });

        }
    },
    _onit_note_confirm: function (events){
          var self = this;
          var order_id = $(events.currentTarget).attr('data-order_id');
          var text = $('#checkout_text_update').val();
          console.log("order onfo",order_id,text)
          ajax.jsonRpc('/sale/line/note/create', 'call', {'order_id':  order_id,'text':text})
                .then(function (result) {
                    $('.lis-modal').hide();
          });

    },
});
});