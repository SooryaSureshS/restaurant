odoo.define('pos_ui_changes.PosComponents', function(require) {
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
    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');

        const ChromeNewUpdate = (Chrome) =>
        class extends Chrome {
               constructor() {
                    super(...arguments);
//                   useListener('click-discount', this._clickDiscount);
               }
               __showScreen({ detail: { name, props = {} } }) {
                    if (name == 'ProductScreen'){
                        $('.pos-rightheader .filters').show();
                        $('.pos-rightheader .kitchen_order').show();
                        $('.pos-rightheader .Product_return__order').show();
                        $('.pos-rightheader .set-customer').show();
                        $('.pos-rightheader .orders_recall').show();
                    }else{
                        $('.pos-rightheader .filters').hide();
                        $('.pos-rightheader .kitchen_order').hide();
                        $('.pos-rightheader .Product_return__order').hide();
                        $('.pos-rightheader .set-customer').hide();
                        $('.pos-rightheader .orders_recall').hide();
                    }
                    const component = this.constructor.components[name];
                    // 1. Set the information of the screen to display.
                    this.mainScreen.name = name;
                    this.mainScreen.component = component;
                    this.mainScreenProps = props;

                    // 2. Set some options
                    this.chromeContext.showOrderSelector = !component.hideOrderSelector;

                    // 3. Save the screen to the order.
                    //  - This screen is shown when the order is selected.
                    if (!(component.prototype instanceof IndependentToOrderScreen)) {
                        this._setScreenData(name, props);
                    }
                }


        };
    Registries.Component.extend(Chrome, ChromeNewUpdate);

    return Chrome;

});