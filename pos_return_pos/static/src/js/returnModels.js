odoo.define('pos_return_pos.returnModels', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
    const { useExternalListener } = owl.hooks;


    var _super_orderline = models.Orderline;
    models.Orderline = models.Orderline.extend({

        set_line_id: function(line_id){
            this.line_id = line_id;
        },
        export_as_JSON: function(){
            var json = _super_orderline.prototype.export_as_JSON.apply(this,arguments);
            json.line_id = this.line_id;
            return json;
        },
        init_from_JSON: function(json){
            _super_orderline.prototype.init_from_JSON.apply(this,arguments);
            this.line_id = json.line_id;
        },
    });


    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr,options) {
            _super_order.initialize.apply(this,arguments);
           this.return_ref = '';
        },
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.return_ref = this.return_ref;
            return json;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.return_ref = json.return_ref;
        },
        export_for_printing: function() {
            var json = _super_order.export_for_printing.apply(this,arguments);
            json.return_ref = this.get_return_product();
            return json;
        },
        get_return_product: function(){
            return this.return_ref;
        },
        set_return_product: function(return_ref) {
            this.return_ref = return_ref;
        },
    });


});
