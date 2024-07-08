odoo.define('pos_mcd_open_order.models', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
    const { useExternalListener } = owl.hooks;


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

    models.load_models({
        model: 'pos.config',
        fields: ['docket_category_break'],
        loaded: function(self, config){
            self.pos_config_db = config;
        }
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr,options) {
            _super_order.initialize.apply(this,arguments);
           this.updated_order = '';
           this.change_product_list = [];
        },
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.updated_order = this.updated_order;
            json.change_product_list = this.change_product_list;
            return json;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.updated_order = json.updated_order;
            this.change_product_list = json.change_product_list || []; // 1
        },
        export_for_printing: function() {
            var json = _super_order.export_for_printing.apply(this,arguments);
            json.updated_order = this.get_change_product();
            json.change_product_list = this.get_change_list();
            return json;
        },
        get_change_product: function(){
            return this.updated_order;
        },
        set_change_product: function(updated_order) {
            this.updated_order = updated_order;
        },
        get_change_list: function(){
            return this.change_product_list;
        },
        set_change_list: function(list) {
            this.change_product_list.push(list)
//            this.gift_cards = gift_cards;
            this.trigger('change');
        },
        get_orderlines_new: function(){
            return this.orderlines.models;
        },
        getOrderReceiptEnv: function() {
        // Formerly get_receipt_render_env defined in ScreenWidget.
        console.log("parent category",this);

            return {
                order: this,
                receipt: this.export_for_printing(),
                orderlines: this.get_orderlines(),
                paymentlines: this.get_paymentlines(),
            };
        },
    });



var _super_orderline = models.Orderline.prototype;
models.Orderline = models.Orderline.extend({
    export_for_printing: function() {
        var line = _super_orderline.export_for_printing.apply(this,arguments);
        line.pos_categ_id = this.get_product().pos_categ_id;
        line.is_optional_product = this.get_product().is_optional_product;
        return line;
    },
});


});
