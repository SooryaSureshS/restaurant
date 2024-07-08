odoo.define('pos_public_holiday.models', function(require) {
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
            _super_order.initialize.apply(this,arguments);
           this.surcharge = '';
        },
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.surcharge = this.surcharge;
            return json;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.surcharge = json.surcharge;
        },
        export_for_printing: function() {
            var json = _super_order.export_for_printing.apply(this,arguments);
            json.surcharge = this.get_surcharge();
            return json;
        },
        get_surcharge: function(){
            return this.surcharge;
        },
        set_surcharge: function(surcharge) {
            this.surcharge = surcharge;
        },
        updatePricelist: function(newClient) {
            let newClientPricelist, newClientFiscalPosition;
            const defaultFiscalPosition = this.pos.fiscal_positions.find(
                (position) => position.id === this.pos.config.default_fiscal_position_id[0]
            );
            if (newClient) {
                newClientFiscalPosition = newClient.property_account_position_id
                    ? this.pos.fiscal_positions.find(
                          (position) => position.id === newClient.property_account_position_id[0]
                      )
                    : defaultFiscalPosition;
                newClientPricelist =
                    this.pos.pricelists.find(
                        (pricelist) => pricelist.id === newClient.property_product_pricelist[0]
                    ) || this.pos.default_pricelist;
            } else {
                newClientFiscalPosition = defaultFiscalPosition;
                newClientPricelist = this.pos.default_pricelist;
            }
            this.fiscal_position = newClientFiscalPosition;
            this.set_pricelist(newClientPricelist);
            if (this.pos.config.iface_holiday){
                if(this.pos.config.surcharge_product){
                    var surcharge = this.pos.db.get_product_by_id(this.pos.config.surcharge_product[0]);
                    var order = this.pos.get_order()
                    var surcharge_amount = order.get_surcharge();
                    if (order && surcharge) {
                        order.get_orderlines().forEach(function (orderline) {
                            var product = orderline.product;
                            if(product.id == surcharge.id){
                                orderline.set_unit_price(surcharge_amount);
                            }
                        });
                    }
                }
                }
        }

    });


});
