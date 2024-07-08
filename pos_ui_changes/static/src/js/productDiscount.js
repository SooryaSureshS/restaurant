odoo.define('pos_ui_changes.productDiscount', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { useState } = owl.hooks;
      const { Gui } = require('point_of_sale.Gui');

        const ProductsWidgetCategory = (ProductScreen) =>
        class extends ProductScreen {
               constructor() {
                    super(...arguments);
                   useListener('click-discount', this._clickDiscount);
               }
               async _clickDiscount() {
                    var self = this;
                    let selectedLine = this.env.pos.get_order().get_selected_orderline();
                    if (selectedLine){
                        const { confirmed, payload: inputPin } = await Gui.showPopup('NumberPopupUpdateTime', {
                                isPassword: false,
                                title: 'Discount ',
                                startingValue: null,

                         });
                         if (confirmed){
                                console.log("message",inputPin)
                                if (inputPin){
                                        selectedLine.set_discount(inputPin);
                                }

                     }
                    }else{
                         await this.showPopup('ErrorPopup', {
                                title: 'Order Not Defined ',
                                body: 'Please select order line'
                         });
                    }

                }


        };
    Registries.Component.extend(ProductScreen, ProductsWidgetCategory);

    return ProductScreen;

        });