odoo.define('pos_optional_products.PosloyaltyPopup', function(require) {
    'use strict';
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { useState } = owl.hooks;
    var models = require('point_of_sale.models');
    var core = require('web.core');

    class PosloyaltyPopup extends AbstractAwaitablePopup {
    constructor() {
    super(...arguments);
    }
    get OrderDetails(){
        var self=this;
         var order = self.env.pos.get_order();
         var client = order.get_client()
         var point = order.customerLoyaltyPoint+order.get_spent_points();
         var redeem_amount = 0;
         var all_rule = order.customerLoyaltydata;
         all_rule['name']=client.name;
         return all_rule;

    }

    async confirmOrder(OrderDetails){
    var self = this;
    if ($('input[name="product_loyalty"]:checked').val())
    {
    var id_product = $('input[name="product_loyalty"]:checked').val();
      var selected_line = $('input[name="product_loyalty"]:checked').attr('id');
      var points_end = $('input[name="product_loyalty"]:checked').attr('points_end');
     var product = this.env.pos.db.get_product_by_id(id_product);
            var order = this.env.pos.get_order();
            order.add_product(product, {
                price: 0,
                quantity: 1,
                merge: false,
                extras: { wk_loyalty: true,points_used:points_end},
            });
             return this.confirm();
    }
    else{
                        self.showPopup('ErrorPopup', {
                                        title: self.env._t('Error'),
                                        body: self.env._t("Please select a product"),});
    }


    }
}

   PosloyaltyPopup.template = 'PosloyaltyPopup';
   PosloyaltyPopup.defaultProps = {
       confirmText: 'Ok',
       cancelText: 'Cancel',
       body: '',
   };
   Registries.Component.add(PosloyaltyPopup);
   return PosloyaltyPopup;
});
