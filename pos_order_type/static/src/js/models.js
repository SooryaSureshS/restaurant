odoo.define('pos_order_type.models', function(require) {
    'use strict';

    var models = require('point_of_sale.models');
    var DB = require('point_of_sale.DB');
    var OrderReceipt = require('point_of_sale.OrderReceipt');
    var now = new Date()
    var rpc = require('web.rpc');


var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr,options) {
            $('#hide_div_collapse').hide();
            _super_order.initialize.apply(this,arguments);
           this.delivery_type = '';
           this.table_name = '';
           this.delivery_note = '';
           var pos_order_note_payment = $('#pos_order_note_payment').val();
           console.log("&&&&&&&", pos_order_note_payment)
           this.pos_order_note_payment = '';
        },
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.delivery_type = this.delivery_type;
            json.table_name = this.table_name;
            json.delivery_note = this.delivery_note;
            var pos_order_note_payment = $('#pos_order_note_payment').val();
            json.pos_order_note_payment = pos_order_note_payment;
            console.log("kjhg", pos_order_note_payment)
            return json;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.delivery_type = json.delivery_type;
            this.table_name = json.table_name;
            this.delivery_note = json.delivery_note;
            var pos_order_note_payment = $('#pos_order_note_payment').val();
            this.pos_order_note_payment = pos_order_note_payment;
            console.log("kkkkk", pos_order_note_payment)
        },

    });

});