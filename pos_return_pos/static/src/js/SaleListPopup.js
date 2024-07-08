odoo.define('pos_return_pos.SaleListPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
      const { useExternalListener } = owl.hooks;

    var core = require('web.core');

    var _t = core._t;
    // formerly TextAreaPopupWidget
    // IMPROVEMENT: This code is very similar to TextInputPopup.
    //      Combining them would reduce the code.
    class ReturnSaleListPopupsWidget extends AbstractAwaitablePopup {
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
                this.results_payment = null
        }


        mounted() {
//            this.inputRef.el.focus();
        }
        async filteredSaleOrdersListLine(ref){
            this.pos_reference = ref
            var params = {
                        model: 'pos.order',
                        method: 'get_lines',
                        args: [ref],
                    }
                    this.rpc(params, {async: false}).then(function(result){
                        return result[0]
                    }).catch(function () {
                         const { confirmed: confirmedPopup } = this.showPopup('ConfirmPopup', {
                            title: 'Error',
                            body: 'Sorry Product Not found',
                        });
                        if (!confirmedPopup) return;
                    });

        }
        getPayload() {
            return this.results_payment;
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
                  const { confirmed: confirmedPopup } = this.showPopup('ConfirmPopup', {
                    title: 'Error',
                    body: 'Please check the Returned Quantity,it is higher than purchased',
                });

                if (!confirmedPopup) return;
             }
             else{
                self.displayLoading();
                 var list = []
                setTimeout(function () {
                 $('#props_return_popup tr').each(function() {
                        var pro_obj = $(this).find('input').data('product_id');
                        var line_id = $(this).find('input').data('line_id');
                        var return_qty = $(this).find('input').val();
                        var product   = self.env.pos.db.get_product_by_id(pro_obj);
//                        if (!product) {
//                            return;
//                        }
                        console.log("looops",return_qty)
                        if (return_qty > 0){
                              var return_list = {
                                    'product_id': pro_obj,
                                    'line_id': line_id,
                                    'return_qty': return_qty,
                              }
                              list.push(return_list)
                        }
                 });
                  var params = {
                        model: 'sale.order',
                        method: 'set_return_product',
                        args: [list],
                    }
                    self.rpc(params, {async: false}).then(function(result){
                          if (result){
                           self.results_payment = result[0].status
                           self.confirm();
//                           setTimeout(function () {
//                              const { confirmed: confirmedPopup } = self.showPopup('ConfirmPopup', {
//                                title: 'Refund',
//                                body: result[0].status,
//                            });
//                             }, 2000);
                          $.unblockUI();
//                        if (!confirmedPopup) return;
                          }


                    }).catch(function () {
                        const { confirmed: confirmedPopup } = self.showPopup('ConfirmPopup', {
                            title: 'Error',
                            body: 'Sorry Return Failed',
                        });
                          $.unblockUI();
                        if (!confirmedPopup) return;
                    });
                     }, 2000);

             }

        }
        async displayLoading () {
            var msg = _t("We are processing your payment, please wait ...");
            $.blockUI({
                'message': '<h2 class="text-white" style="color: white;"><img src="/web/static/src/img/spin.png" class="fa-pulse"/>' +
                    '    <br />' + msg +
                    '</h2>'
            });
        }
        }

    ReturnSaleListPopupsWidget.template = 'ReturnSaleListPopupsWidget';
    ReturnSaleListPopupsWidget.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',

    };

    Registries.Component.add(ReturnSaleListPopupsWidget);

    return ReturnSaleListPopupsWidget;


});
