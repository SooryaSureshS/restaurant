odoo.define('pos_optional_products.models', function(require) {
    'use strict';

    const { Context } = owl;
    var BarcodeParser = require('barcodes.BarcodeParser');
    var BarcodeReader = require('point_of_sale.BarcodeReader');
    var PosDB = require('point_of_sale.DB');
    var devices = require('point_of_sale.devices');
    var concurrency = require('web.concurrency');
    var config = require('web.config');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var time = require('web.time');
    var utils = require('web.utils');
    var models = require('point_of_sale.models');

    var QWeb = core.qweb;
    var _t = core._t;
    var Mutex = concurrency.Mutex;
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;

    var exports = {};
    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
    /* Disable Order Line Merge*/
        add_product: function(product, options){
            console.log("HHHH")
            if(this._printed){
                this.destroy();
                console.log("sanjkdbf", this.pos.get_order())
                return this.pos.get_order().add_product(product, options);

            }
            this.assert_editable();
            options = options || {};
            var line = new models.Orderline({}, {pos: this.pos, order: this, product: product});
            this.fix_tax_included_price(line);

            if(options.quantity !== undefined){
                line.set_quantity(options.quantity);
            }

            if(options.price !== undefined){
                line.set_unit_price(options.price);
                this.fix_tax_included_price(line);
            }

            if (options.price_extra !== undefined){
                line.price_extra = options.price_extra;
                line.set_unit_price(line.product.get_price(this.pricelist, line.get_quantity(), options.price_extra));
                this.fix_tax_included_price(line);
            }

            if(options.lst_price !== undefined){
                line.set_lst_price(options.lst_price);
            }

            if(options.discount !== undefined){
                line.set_discount(options.discount);
            }

            if (options.description !== undefined){
                line.description += options.description;
            }

            if(options.extras !== undefined){
                for (var prop in options.extras) {
                    line[prop] = options.extras[prop];
                }
            }
            if (options.is_tip) {
                this.is_tipped = true;
                this.tip_amount = options.price;
            }

            var to_merge_orderline;
            for (var i = 0; i < this.orderlines.length; i++) {
                if(this.orderlines.at(i).can_be_merged_with(line) && options.merge !== false){
                    to_merge_orderline = this.orderlines.at(i);
                }
            }
            if (to_merge_orderline){
                console.log("to merge")
                console.log("lililijomx", line)
                this.orderlines.add(line);
                this.select_orderline(this.get_last_orderline());
//               to_merge_orderline.merge(line);
//               this.select_orderline(to_merge_orderline);
            } else {
                this.orderlines.add(line);
                this.select_orderline(this.get_last_orderline());
            }

            if (options.draftPackLotLines) {
                this.selected_orderline.setPackLotLines(options.draftPackLotLines);
            }
            if (this.pos.config.iface_customer_facing_display) {
                this.pos.send_current_order_to_customer_facing_display();
            }
        },
    });

   });
//
//
//
//   models.Order = models.Order.extend({
//
//        add_product: function(product, options){
//        if(this._printed){
//            this.destroy();
//            return this.pos.get_order().add_product(product, options);
//        }
//        console.log("sdsdsdsd",product,options);
////        this.pos.get_order().add_product(3724);
//        this.assert_editable();
//        options = options || {};
//        var attr = JSON.parse(JSON.stringify(product));
//        attr.pos = this.pos;
//        attr.order = this;
//        var line = new models.Orderline({}, {pos: this.pos, order: this, product: product});
//
//        if(options.quantity !== undefined){
//            line.set_quantity(options.quantity);
//        }
//
//        if(options.price !== undefined){
//            line.set_unit_price(options.price);
//        }
//
//        //To substract from the unit price the included taxes mapped by the fiscal position
//        this.fix_tax_included_price(line);
//
//        if(options.discount !== undefined){
//            line.set_discount(options.discount);
//        }
//
//        if(options.extras !== undefined){
//            for (var prop in options.extras) {
//                line[prop] = options.extras[prop];
//            }
//        }
//
//        var to_merge_orderline;
//
//
//        for (var i = 0; i < this.orderlines.length; i++) {
//            if(this.orderlines.at(i).can_be_merged_with(line) && options.merge !== false){
//                to_merge_orderline = this.orderlines.at(i);
////                console.log("to merge",to_merge_orderline);
//            }
//        }
//        if (to_merge_orderline){
////            to_merge_orderline.merge(line);
//            this.orderlines.add(line);
//        } else {
//            this.orderlines.add(line);
//        }
//        this.select_orderline(this.get_last_orderline());
//
//        if(line.has_product_lot){
//            this.display_lot_popup();
//        }
//    },
//
//
//});