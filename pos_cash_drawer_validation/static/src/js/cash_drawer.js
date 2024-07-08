odoo.define('pos_cash_drawer_validation.cash_drawer', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const CashDrawer = (PaymentScreen) =>
    class  extends PaymentScreen {
         async validateOrder(isForceValidate) {
                await super.validateOrder(isForceValidate);
                if (this.selectedPaymentLine){
                         if (this.selectedPaymentLine.name == "Cash"){
                            this.env.pos.proxy.printer.open_cashbox();
                        }
                        }
         }
    };
    Registries.Component.extend(PaymentScreen, CashDrawer);
    return PaymentScreen;


});
