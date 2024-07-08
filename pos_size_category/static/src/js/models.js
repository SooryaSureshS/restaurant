odoo.define('pos_size_category.models', function(require) {
    'use strict';

   const { Gui } = require('point_of_sale.Gui');
   const PosComponent = require('point_of_sale.PosComponent');
   const { posbus } = require('point_of_sale.utils');
   const ProductScreen = require('point_of_sale.ProductScreen');
   const { useListener } = require('web.custom_hooks');
   const Registries = require('point_of_sale.Registries');
   const PaymentScreen = require('point_of_sale.PaymentScreen');

    var models = require('point_of_sale.models');
    var DB = require('point_of_sale.DB');
    var OrderReceipt = require('point_of_sale.OrderReceipt');

    var now = new Date()
    var rpc = require('web.rpc');

    models.load_models({
        model:  'pos.size.category',
        fields: [],
        loaded: function(self, category){
//            self.sale_orders_refund = orders;
//            self.fetch_new_data()
        self.product_size_category = category;
    },

   });
   models.load_fields("product.product", ['pos_size_categ_id']);

    DB.include({
        get_product_by_size: function(id){
            console.log("db",this.product_by_id)
            var size_list = []
            _.each(this.product_by_id, function (product) {
                if (product.pos_size_categ_id[0] == id){
                    size_list.push(product.id)
                }
            });
            return size_list;
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr,options) {
            _super_order.initialize.apply(this,arguments);
           this.size = '';
        },
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.size = this.size;
            return json;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.size = json.size;
        },
        export_for_printing: function() {
            var json = _super_order.export_for_printing.apply(this,arguments);
            json.size = this.get_size();
            return json;
        },
        get_size: function(){
            return this.size;
        },
        set_size: function(size) {
            this.size = size;
        },

    });

   });