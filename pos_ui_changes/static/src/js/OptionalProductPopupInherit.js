odoo.define('pos_ui_changes.OptionalProductPopupInherit', function(require) {
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
    var OptionalProductsPopup = require('pos_optional_products.OptionalProductsPopup');


        const OptionalProductsPopupInherits = (OptionalProductsPopup) =>
        class extends OptionalProductsPopup {

            async prepend_qty(){
                var qty = parseInt($('#parent_qty').val());
                if(typeof qty==='number' && (qty%1)===0) {
                    qty = qty - 1;
                    if (qty > 0){
                        $('#parent_qty').val(qty);
                    }
                }
            }
            async append_qty(){
                var qty = parseInt($('#parent_qty').val());
                if(typeof qty==='number' && (qty%1)===0) {
                    qty = qty + 1;
                    if (qty > 0){
                        $('#parent_qty').val(qty);
                    }
                }
            }

        };

    Registries.Component.extend(OptionalProductsPopup, OptionalProductsPopupInherits);

    return OptionalProductsPopup;

});