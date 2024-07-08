odoo.define('pos_mcd_open_order.receiptSendToKitchen', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const core = require('web.core');
    const QWeb = core.qweb;

    class ReceiptScreenOpenMcd extends PosComponent {
        constructor() {
            super(...arguments);
//            const client = order.get_client();

            this.widget = this.props.widget
            this.order = this.props.order
            this.type = this.props.type
//            this._receiptEnv = this.props.order.getOrderReceiptEnv();
//            var order = this.env.pos.get_order();
            useListener('close-screen', this.close);
            useListener('printReceipt', this._printReceipt);

        }
//        willUpdateProps(nextProps) {
//            this._receiptEnv = nextProps.order.getOrderReceiptEnv();
//        }
        get widget_info() {
            return this.widget
        }
        get order_info(){
            return this.order
        }
        get type_info() {
            return this.type
        }
        get isTaxIncluded1() {
            var self = this;
        }
        get receipt() {
            return this.receiptEnv.receipt;
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
        close() {
            this.showScreen('ProductScreen');
        }
    async _printReceipt() {
        if (this.env.pos.proxy.printer) {
//            var receipt = QWeb.render('OrderReceiptRecall',{'order_info': this.order, 'widget_info': this.widget});
//            var receipt = QWeb.render('OrderReceiptMcd',{});
//            receipt = '<div class="pos-receipt"><h2 class="pos-receipt-center-align">On It Burgers</h2><br><div class="pos-receipt-contact"><div>On It Burgers</div><div>Tel:0478 154 621</div><div>peter@onitburgers.com</div><div>https://www.wooshfood.com</div><div class="cashier"><div>--------------------------------</div><div>Served by Monika</div></div> at table tables<div>Guests: 1</div></div><br><br><div class="orderlines"><div>Coca Cola Classic 375ML<span class="price_display pos-receipt-right-align">3.85</span></div><span></span><div>Can 375mL<span class="price_display pos-receipt-right-align">0.00</span></div><span></span></div><div class="pos-receipt-right-align">--------</div><br><div class="pos-receipt-amount"> TOTAL <span class="pos-receipt-right-align">$ 3.85</span></div><br><br><div>Cash<span class="pos-receipt-right-align">3.85</span></div><br><div class="pos-receipt-amount receipt-change"> CHANGE <span class="pos-receipt-right-align">$ 0.00</span></div><br><div>Sales Tax 0% ES33<span class="pos-receipt-right-align">0.00</span></div><div> Total Taxes <span class="pos-receipt-right-align">$ 0.00</span></div><div class="before-footer"></div><div class="after-footer"></div><br><div class="pos-receipt-order-data"><div>Order 00846-005-0002</div><div>01/28/2022 08:58:04</div></div></div>'
//            const printResult = await this.env.pos.proxy.printer.print_receipt(receipt);
//            const printResult = await this.env.pos.proxy.printer.print_receipt(this.orderReceipt.el.outerHTML);
//            if (printResult.successful) {
//                return true;
//            } else {
//                const { confirmed } = await this.showPopup('ConfirmPopup', {
//                    title: printResult.message.title,
//                    body: 'Do you want to print using the web printer?',
//                });
//                if (confirmed) {
                    // We want to call the _printWeb when the popup is fully gone
                    // from the screen which happens after the next animation frame.
//                    await nextFrame();
                   this._printWeb();
//                }
//                return false;
//            }
//        } else {
//            return await this._printWeb();
        }
    }
    async _printWeb(receipt) {
            try {
                $(this.el).find('.pos-receipt-container').html(receipt);
                const isPrinted = document.execCommand('print', false, null);
                if (!isPrinted) window.print();
            } catch (err) {
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Printing is not supported on some browsers'),
                    body: this.env._t(
                        'Printing is not supported on some browsers due to no default printing protocol ' +
                            'is available. It is possible to print your tickets by making use of an IoT Box.'
                    ),
                });
            }
        }
    }

    ReceiptScreenOpenMcd.template = 'ReceiptScreenOpenMcd';

    Registries.Component.add(ReceiptScreenOpenMcd);

    return ReceiptScreenOpenMcd;
});
