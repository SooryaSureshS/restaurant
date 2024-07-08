odoo.define('pos_offline_orders.offline_popup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
      const { useExternalListener } = owl.hooks;
       var framework = require('web.framework');
    // formerly TextAreaPopupWidget
    // IMPROVEMENT: This code is very similar to TextInputPopup.
    //      Combining them would reduce the code.
    class OfflinePopupConfirmPopupWidget extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        constructor() {
            super(...arguments);

        }
        mount() {
            var self = this;

        }
//        async confirmed(){
//            var self = this;
//            if (self.blocked){
//                const { confirmed } = await this.showPopup('ConfirmPopup', {
//                    title: 'The Table Is Already Booked',
//                    body: 'Do you want to book another booking',
//                });
//                if (confirmed) {
//                    self.confirm()
//                }
//            }else{
//                 self.confirm()
//            }
//
//        }
        async clearCache(){
            var self = this;
            framework.blockUI();
            var orders = self.env.pos.db.cache.orders
            var args = _.map(orders, function (order) {
                 self.env.pos.db.remove_order(order.id);

            });
            var unpaid_orders = self.env.pos.db.cache.unpaid_orders
            var args = _.map(unpaid_orders, function (order) {
                 self.env.pos.db.remove_unpaid_order(order.id);

            });
            self.env.pos.db.remove_all_unpaid_orders();
            setTimeout(function () {
               framework.unblockUI();
               framework.redirect('/pos/ui');
              }, 10000)

        }



    }
    OfflinePopupConfirmPopupWidget.template = 'OfflinePopupConfirmPopupWidget';
    OfflinePopupConfirmPopupWidget.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',

    };

    Registries.Component.add(OfflinePopupConfirmPopupWidget);

    return OfflinePopupConfirmPopupWidget;

});
