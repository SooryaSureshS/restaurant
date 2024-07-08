odoo.define('pos_open_orders.models', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
    const { useExternalListener } = owl.hooks;

//
//    var _super_orderline = models.Orderline;
//    models.Orderline = models.Orderline.extend({
//
//        set_line_id: function(line_id){
//            this.line_id = line_id;
//        },
//        export_as_JSON: function(){
//            var json = _super_orderline.prototype.export_as_JSON.apply(this,arguments);
//            json.line_id = this.line_id;
//            return json;
//        },
//        init_from_JSON: function(json){
//            _super_orderline.prototype.init_from_JSON.apply(this,arguments);
//            this.line_id = json.line_id;
//        },
//    });


    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr,options) {
            $('#hide_div_collapse').hide();
            _super_order.initialize.apply(this,arguments);
           this.open_order_ref = '';
           this.open_order_id = '';
           this.order_parse_json = '';
           this.open_order_table = '';
        },
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.open_order_ref = this.open_order_ref;
            json.open_order_id = this.open_order_id;
            json.order_parse_json = this.order_parse_json;
            json.open_order_table = this.open_order_table;
            json.delivery_type = this.delivery_type;
            return json;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.open_order_ref = json.open_order_ref;
            this.open_order_id = json.open_order_id;
            this.order_parse_json = json.order_parse_json;
            this.open_order_table = json.open_order_table;
            this.delivery_type = json.delivery_type;
        },
        export_for_printing: function() {
            var json = _super_order.export_for_printing.apply(this,arguments);
            json.open_order_ref = this.get_open_order_ref();
            json.open_order_id = this.get_open_order_id();
            json.order_parse_json = this.get_order_parse_json();
            json.open_order_table = this.get_order_parse_json();
            json.delivery_type = this.get_delivery_type();
            return json;
        },
        get_open_order_ref: function(){
            return this.open_order_ref;
        },
        set_open_order_ref: function(open_order_ref) {
            this.open_order_ref = open_order_ref;
        },

        get_open_order_id: function(){
            return this.open_order_id;
        },
        set_open_order_id: function(open_order_id) {
            this.open_order_id = open_order_id;
        },

        get_order_parse_json: function(){
            return this.order_parse_json;
        },
        set_order_parse_json: function(order_parse_json) {
            this.order_parse_json = order_parse_json;
        },


        get_open_order_table: function(){
            return this.open_order_table;
        },
        set_open_order_table: function(open_order_table) {
            this.open_order_table = open_order_table;
        },

         get_delivery_type: function(){
            return this.delivery_type;
        },
        set_delivery_type: function(delivery_type) {
            this.delivery_type = delivery_type;
        },

    });


    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
           open_order_up: function(options){
                var order = new models.Order({},{pos:this});
                this.get('orders').add(order);
                this.set('selectedOrder', order, options);
                return order;
            },
    });

});
