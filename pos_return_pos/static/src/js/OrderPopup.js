odoo.define('pos_return_pos.OrderPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
      const { useExternalListener } = owl.hooks;
    // formerly TextAreaPopupWidget
    // IMPROVEMENT: This code is very similar to TextInputPopup.
    //      Combining them would reduce the code.
    class ReturnPopupsWidget extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        constructor() {
            super(...arguments);
//            useExternalListener(window, 'keyup', this._jsBarcode);
//               this.partner_id = useState({ partner_id: this.props.partner_id.id });
//               this.partner_name = useState({ partner_id: this.props.partner_id.name });
               this.ref = useState(this.props.ref);
               this.client = useState(this.props.client);
//               this.card_type = this.env.pos.card_type;
        }


        mounted() {
//            this.inputRef.el.focus();
        }
        async filteredOrdersListLine(ref){
            this.pos_reference = ref
            var params = {
                        model: 'pos.order',
                        method: 'get_lines',
                        args: [ref],
                    }
                    this.rpc(params, {async: false}).then(function(result){
                        return result[0]
                    }).catch(function () {
                        alert("NO DATA")
                    });;

        }
        async confirm_return() {
            var self = this;
            var count  = 0;
             $('#props_return_popup tr').each(function() {
                if ($(this).find('input').data('qty') < $(this).find('input').val()){
                    count +=1
                }
             });
             if(count > 0){
                 alert('Please check the Returned Quantity,it is higher than purchased')
             }
             else{
                 $('#props_return_popup tr').each(function() {
                        var pro_obj = $(this).find('input').data('product_id');
                        var return_qty = $(this).find('input').val();
                        var product   = self.env.pos.db.get_product_by_id(pro_obj);
                        if (!product) {
                            return;
                        }
                        if (return_qty > 0){
                            self.env.pos.get_order().add_product(product, {
                            price: $(this).find('input').data('price_unit'),
                            quantity: -($(this).find('input').val()),
                            discount:$(this).find('input').data('discount'),
                            merge: false,
                            extras: {return_ref: self.ref,
                                    label:$(this).find('input').data('line_id')},
                            });
                            var selected_orderline = self.env.pos.get_order().get_selected_orderline();
                            selected_orderline.set_line_id($(this).find('input').data('line_id'));
                        }
                 });
                 if (self.client){
                    self.env.pos.get_order().set_client(self.env.pos.db.get_partner_by_id(self.client));
                 }
             }
             if (self.ref){
                self.env.pos.get_order().set_return_product(self.ref);
             }
             self.confirm();
             self.showScreen('ProductScreen');



        }
        }

    ReturnPopupsWidget.template = 'ReturnPopupsWidget';
    ReturnPopupsWidget.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',

    };

    Registries.Component.add(ReturnPopupsWidget);

    return ReturnPopupsWidget;






});
