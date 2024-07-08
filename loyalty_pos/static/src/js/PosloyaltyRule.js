odoo.define('pos_optional_products.PosloyaltyRule', function(require) {
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

    class PosloyaltyRule extends AbstractAwaitablePopup {
    constructor() {
    super(...arguments);
    }
    get OrderDetails(){
        var self=this;
         return self.env.pos.loyaltyrule;

    }
    get CurrentPoint(){
    var self=this;
         return self.env.pos.current_point;

    }


}

   PosloyaltyRule.template = 'PosloyaltyRule';
   PosloyaltyRule.defaultProps = {
       confirmText: 'Ok',
       cancelText: 'Cancel',
       body: '',
   };
   Registries.Component.add(PosloyaltyRule);
   return PosloyaltyRule;
});
