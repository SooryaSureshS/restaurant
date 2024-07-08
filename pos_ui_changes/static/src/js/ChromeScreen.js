odoo.define('pos_ui_changes.productDiscount', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Chrome = require('point_of_sale.Chrome');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { useState } = owl.hooks;
      const { Gui } = require('point_of_sale.Gui');

        const ChromeNew = (Chrome) =>
        class extends Chrome {
               constructor() {
                    super(...arguments);
//                   useListener('click-discount', this._clickDiscount);
               }
              get order_info (){
                     var self = this;
                     console.log("insssssssssss",self)
                     return self.env.pos.get_order();
                }


        };
    Registries.Component.extend(Chrome, ChromeNew);

    return Chrome;

    });