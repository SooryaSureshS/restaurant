odoo.define('pos_ui_changes.kitchenScreen', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const ProductKitchenScreen = require('kitchen_order.kitchenscreen_template');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { useState } = owl.hooks;
      const { Gui } = require('point_of_sale.Gui');

        const ProductKitchenScreenInherit = (ProductKitchenScreen) =>
        class extends ProductKitchenScreen {
               constructor() {
                    super(...arguments);
//                   useListener('click-discount', this._clickDiscount);
               }
                back_click (){
                    var order = this.env.pos.get_order();
                    if (order){
                        this.kitchen_screen_name = false;
                        $('#hide_div_collapse').show();
                        this.showScreen('ProductScreen');
                    }else{
                          this.showPopup('ErrorPopup', {
                                title: 'Order Not Defined ',
                                body: 'Please select order'
                         });
                    }
                }

        };
    Registries.Component.extend(ProductKitchenScreen, ProductKitchenScreenInherit);

    return ProductKitchenScreen;

});