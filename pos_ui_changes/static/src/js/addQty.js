odoo.define('pos_ui_changes.addQty', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
     const { useExternalListener } = owl.hooks;

    class AddQtyPopup extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        constructor() {
            super(...arguments);
//               this.ref = useState(this.props.ref);
//               this.client = useState(this.props.client);
        }

        mounted() {
//            this.inputRef.el.focus();
        }
        async prepend_qty(){
            var qty = parseInt($('#quantity_add').val());
            if(typeof qty==='number' && (qty%1)===0) {
                qty = qty - 1;
                if (qty > 0){
                    $('#quantity_add').val(qty);
                }
            }
        }
        async append_qty(){
            var qty = parseInt($('#quantity_add').val());
            if(typeof qty==='number' && (qty%1)===0) {
                qty = qty + 1;
                if (qty > 0){
                    $('#quantity_add').val(qty);
                }
            }
        }
        async confirm_addqty() {
            var self = this;
            let order = this.env.pos.get_order();
            let selectedLine = this.env.pos.get_order().get_selected_orderline();
            var qty = parseInt($('#quantity_add').val());
            if(typeof qty==='number' && (qty%1)===0) {
                let currentQuantity = selectedLine.set_quantity(qty);
                self.confirm();
            }else{
                 await this.showPopup('ErrorPopup', {
                        title: 'Quantity Not acceptable ',
                        body: 'Please check the quantity entered'
                 });
            }
        }
        async confirm_remove(){
            var self = this;
            let order = this.env.pos.get_order();
            let selectedLine = this.env.pos.get_order().get_selected_orderline();
            let currentQuantity = selectedLine.set_quantity(0);
            self.confirm();
        }


         async add_discount_custom(){
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


        }

    AddQtyPopup.template = 'AddQtyPopup';
    AddQtyPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',

    };
    Registries.Component.add(AddQtyPopup);
    return AddQtyPopup;
});
