odoo.define('loyalty_pos.PosLoyalty', function(require) {
'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const utils = require('web.utils');

    const round_pr = utils.round_precision;

    class PosLoyalty extends PosComponent {
        get_points_won() {
            return round_pr(this.env.pos.get_order().get_won_points(),1);
//            return 0;
        }
        get_remove_product() {
        var self=this;
           this.env.pos.get_order().get_orderlines().forEach(function (orderline) {
                           if (orderline.wk_loyalty==true && orderline.price>0){
                               orderline.wk_loyalty==false;
            }
            });
//            return this.env.pos.get_order().get_remove_product();
//            return 0;
        }
        get_points_loose() {
            return round_pr(this.env.pos.get_order().get_points_loose(),1);
//            return 0;
        }
        get_points_spent() {
            return round_pr(this.env.pos.get_order().get_spent_points());
//
        }

        get_points_total() {
            return round_pr(this.env.pos.get_order().get_new_total_points());
//             return 0;
        }
        get order() {
            return this.env.pos.get_order();

        }
    }
    PosLoyalty.template = 'PosLoyalty';

    Registries.Component.add(PosLoyalty);

    return PosLoyalty;
});