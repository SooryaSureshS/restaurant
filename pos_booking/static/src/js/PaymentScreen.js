odoo.define('pos_booking.payment_screen', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');

    const CashDrawer = (PaymentScreen) =>
    class  extends PaymentScreen {
         async validateOrder(isForceValidate) {
                await super.validateOrder(isForceValidate);
                rpc.query({
                        model: 'pos.order',
                        method: 'set_people_number',
                        args: [0, this.currentOrder.name, this.env.table_people_number],
                    });

         }
    };
    Registries.Component.extend(PaymentScreen, CashDrawer);
    return PaymentScreen;


});
