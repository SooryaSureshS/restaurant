odoo.define('pos_mcd_bill.OrderReceiptDuplicate', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class OrderReceiptDuplicate extends PosComponent {
        constructor() {
            super(...arguments);
            this._receiptEnv = this.props.order.getOrderReceiptEnv();
        }
        willUpdateProps(nextProps) {
            this._receiptEnv = nextProps.order.getOrderReceiptEnv();
        }
        get receipt() {
            console.log("log company fffffffffffff",this._receiptEnv);
            return this.receiptEnv.receipt;
//            return this.pos.env.get_order().getOrderReceiptEnv();
        }
        get orderlines() {
            return this.receiptEnv.orderlines;
        }
        get paymentlines() {
            return this.receiptEnv.paymentlines;
        }
        get isTaxIncluded() {
            return Math.abs(this.receipt.subtotal - this.receipt.total_with_tax) <= 0.000001;
        }
        get receiptEnv () {
          return this._receiptEnv;
        }
        isSimple(line) {
            return (
                line.discount === 0 &&
                line.unit_name === 'Units' &&
                line.quantity === 1 &&
                !(
                    line.display_discount_policy == 'without_discount' &&
                    line.price != line.price_lst
                )
            );
        }
    }
    OrderReceiptDuplicate.template = 'OrderReceiptDuplicate';

    Registries.Component.add(OrderReceiptDuplicate);

    return OrderReceiptDuplicate;
});
