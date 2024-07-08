odoo.define('pos_return_pos.SaleListAmountPopup', function(require) {
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
    class ReturnSaleListAmountWidget extends AbstractAwaitablePopup {
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
        async confirm_return(order) {
            var self = this;
            var total_amount=$('#return_amount').val();
            var total_amount2=$('#amount').val();
             if(parseInt(total_amount) > parseInt(total_amount2)){
                  const { confirmed: confirmedPopup } = this.showPopup('ConfirmPopup', {
                    title: 'Error',
                    body: 'Please check the Returned Amount,it is higher than purchased',
                });

                if (!confirmedPopup) return;
             }
             else{
                self.displayLoading();
                 var list = []
                setTimeout(function () {
                  var params = {
                        model: 'sale.order',
                        method: 'set_amount_product',
                        args: [order['id'],total_amount],
                    }
                    self.rpc(params, {async: false}).then(function(result){
                          if (result){
                           self.results_payment = result[0].status
                           self.confirm();
                          $.unblockUI();
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

    ReturnSaleListAmountWidget.template = 'ReturnSaleListAmountWidget';
    ReturnSaleListAmountWidget.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',

    };

    Registries.Component.add(ReturnSaleListAmountWidget);

    return ReturnSaleListAmountWidget;


});
