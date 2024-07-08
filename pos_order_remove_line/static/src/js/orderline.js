odoo.define("pos_order_remove_line.Orderline", function (require) {
    "use strict";
var models = require('point_of_sale.models');
var core = require('web.core');
var utils = require('web.utils');

var round_pr = utils.round_precision;
var field_utils = require('web.field_utils');

var _t = core._t;
var exports = {};

var _super_orderline = models.Orderline;
models.Orderline = models.Orderline.extend({
 set_quantity: function(quantity, keep_price){
        this.order.assert_editable();
        if(quantity === 'remove'){
            this.order.remove_orderline(this);
            return;
        }else{
            var quant = typeof(quantity) === 'number' ? quantity : (field_utils.parse.float('' + quantity) || 0);
            if (quant==0){
            this.order.remove_orderline(this);
            return;
            }
            var unit = this.get_unit();
            if(unit){
                if (unit.rounding) {
                    var decimals = this.pos.dp['Product Unit of Measure'];
                    var rounding = Math.max(unit.rounding, Math.pow(10, -decimals));
                    this.quantity    = round_pr(quant, rounding);
                    this.quantityStr = field_utils.format.float(this.quantity, {digits: [69, decimals]});
                } else {
                    this.quantity    = round_pr(quant, 1);
                    this.quantityStr = this.quantity.toFixed(0);
                }
            }else{
                this.quantity    = quant;
                this.quantityStr = '' + this.quantity;
            }
        }

        // just like in sale.order changing the quantity will recompute the unit price
        if(! keep_price && ! this.price_manually_set){
            this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity(), this.get_price_extra()));
            this.order.fix_tax_included_price(this);
        }
        this.trigger('change', this);
    }

});
});
