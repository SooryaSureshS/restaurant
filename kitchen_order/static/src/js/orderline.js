odoo.define('kitchen_order.orderline', function (require) {
"use strict";

var models = require('point_of_sale.models');

var _super_orderline = models.Orderline.prototype;
models.Orderline = models.Orderline.extend({
    initialize: function(attr, options) {
        _super_orderline.initialize.call(this,attr,options);
        this.customer = this.customer || "";
        this.order_line_state = "preparing";
    },
    set_customer: function(customer){
        this.customer = customer;
        this.trigger('change',this);
    },
    get_customer: function(customer){
        return this.customer;
    },
    can_be_merged_with: function(orderline) {
        if (orderline.get_customer() !== this.get_customer()) {
            return false;
        } else {
            return _super_orderline.can_be_merged_with.apply(this,arguments);
        }
    },
    clone: function(){
        var orderline = _super_orderline.clone.call(this);
        orderline.customer = this.customer;
        orderline.order_line_state = this.order_line_state;
        return orderline;
    },
    export_as_JSON: function(){
        var json = _super_orderline.export_as_JSON.call(this);
        json.customer = this.customer;
        json.order_line_state = this.order_line_state;
        return json;
    },
    init_from_JSON: function(json){
        _super_orderline.init_from_JSON.apply(this,arguments);
        this.customer = json.customer;
        this.order_line_state = json.order_line_state;
    },
});

});
