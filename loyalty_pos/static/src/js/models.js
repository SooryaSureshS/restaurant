odoo.define('loyalty_pos.models.js', function (require) {
"use strict";

var models = require('point_of_sale.models');
var core = require('web.core');
var utils = require('web.utils');

var round_pr = utils.round_precision;

var _t = core._t;

models.load_fields('res.partner','wk_website_loyalty_points');

var _super_orderline = models.Orderline;
models.Orderline = models.Orderline.extend({

    export_as_JSON: function(){
        var json = _super_orderline.prototype.export_as_JSON.apply(this,arguments);
        json.wk_loyalty=this.wk_loyalty;
        json.points_used=this.points_used;
        return json;
    },
     init_from_JSON: function(json){
        _super_orderline.prototype.init_from_JSON.apply(this,arguments);
        this.wk_loyalty = json.wk_loyalty;
          json.points_used=this.points_used;
    },

});




models.load_models([
    {
        model: 'website.loyalty.management',
        fields: ['purchase','min_purchase','points','product_id'],
        loaded: function(self,loyalties){
            self.wk_loyalty = loyalties;
        },
}],{'after': 'product.product'});

    var _super = models.Order;
    models.Order = models.Order.extend({

    get_remove_product: function(){

    var self=this;
            this.get_orderlines().forEach(function (orderline) {
            if (orderline.wk_loyalty==true && orderline.price>0){
            self.remove_orderline(orderline);
            }
            });
            return true;
    },
    set_client: function(client){
        this.assert_editable();
        this.set('client',client);
        var self=this;
        self.get_orderlines().forEach(function (orderline) {
            if (orderline.wk_loyalty==true){
            self.remove_orderline(orderline);
        }
        });
    },

   get_new_total_points: function() {
    if (!this.get_client()) {
        return 0;
    } else {
//            var self=this;
//            this.get_orderlines().forEach(function (orderline) {
//                           if (orderline.wk_loyalty==true && orderline.price>0){
//                                self.remove_orderline(orderline);
//            }
//            });

        if(this.state != 'paid'){


         return round_pr(this.get_client().wk_website_loyalty_points-this.get_spent_points());
//                return round_pr(this.get_client().wk_website_loyalty_points + this.get_new_points(), 1);
        }
        else{

            return round_pr(this.get_client().wk_website_loyalty_points-this.get_spent_points());
        }
    }

    },
    get_spent_points: function(){
        var total_points = 0;
        for (var line of this.get_orderlines()){
            if (line.wk_loyalty==true && line.price==0){
             // Reward products are ignored
               total_points+=parseInt(line.points_used);
            }
            else{
            line.wk_loyalty==false;
            }
            }

            return total_points;

    },
   get_new_points: function() {
   var self= this;
    if (!this.get_client()) {
        return 0;
    } else {
    if (this.get_won_points()){
        return this.get_won_points();
    }
    else{
    return this.get_points_loose();
    }

    }
    },
    get_won_points: function(){
        if (!this.pos.config.pos_loyalty || !this.get_client()) {
            return 0;
        }
        var total = 0;
        var min_purchase = 0;
        var points = 0;
        var purchase = 0;
        var amount= this.get_total_with_tax();
        for (var line of this.pos.wk_loyalty){
                if(line.id==this.pos.config.wk_loyalty_program_id[0]) {
                    min_purchase += line.min_purchase;
                    points += line.points;
                    purchase += line.purchase;
                    }
        }
        var total_loyal_points =0;
        if (purchase > 0 && amount >= min_purchase){
            var offer_ratio = points / purchase;
            total_loyal_points=amount * offer_ratio;
        }
        return total_loyal_points;
    },
    get_points_loose: function(){
        if (!this.pos.config.pos_loyalty || !this.get_client()) {
            return 0;
        }
        var total = 0;
        var min_purchase = 0;
        var points = 0;
        var purchase = 0;
        var amount= this.get_total_with_tax();
        for (var line of this.pos.wk_loyalty){
                if(line.id==this.pos.config.wk_loyalty_program_id[0]) {
                    min_purchase += line.min_purchase;
                    points += line.points;
                    purchase += line.purchase;
                    }
        }
        var total_loyal_points =0;
        if (purchase > 0){
            var offer_ratio = points / purchase;
            total_loyal_points=amount * offer_ratio;
        }
        return total_loyal_points;
    },

//        export_for_printing: function(){
//        var json = _super.prototype.export_for_printing.apply(this,arguments);
//        if (this.pos.config.pos_loyalty && this.get_client()) {
//            json.loyalty = {
//                name:         this.pos.loyalty.name,
//                client:       this.get_client().name,
//                points_won  : this.get_won_points(),
//                points_spent: this.get_spent_points(),
//                points_total: this.get_new_total_points(),
//            };
//        }
//        return json;
//    },

    export_as_JSON: function(){
        var json = _super.prototype.export_as_JSON.apply(this,arguments);
         if (this.pos.config.pos_loyalty && this.get_client()) {
         if (this.get_spent_points()!=0) {
            json.reward_redeem = true;
            json.reward_redeem_amount = this.get_spent_points();
        }
        json.loyalty_points = this.get_new_points();
        json.wk_loyalty_program_id = this.pos.config.wk_loyalty_program_id[0];
        }

        return json;

    },

    });
});