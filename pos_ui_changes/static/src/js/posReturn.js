odoo.define('pos_ui_changes.productDiscount', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const PosReturns = require('pos_return_pos.pos_return');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { useState } = owl.hooks;
      const { Gui } = require('point_of_sale.Gui');

        const PosReturnsInherit = (PosReturns) =>
        class extends PosReturns {
               constructor() {
                    super(...arguments);
//                   useListener('click-discount', this._clickDiscount);
               }
               async onClick() {
                    var order = this.env.pos.get_order();
                    if (order){
                         var lines = order.get_orderlines();
                            while(lines.length > 0) {
                                order.remove_orderline(lines[0]);
                        }
                        this.showScreen('OrderListReturn');
                    }else{
                    console.log("clickedsss",this)
                    console.log("clickedsss",this.env.pos.get_order())
                         await this.showPopup('ErrorPopup', {
                                title: 'Order Not Defined ',
                                body: 'Please select order'
                         });
                    }

                }
                get order_info (){
                     var self = this;
                     return self.env.pos.get_order();
                }
        };
    Registries.Component.extend(PosReturns, PosReturnsInherit);

    return PosReturns;

});