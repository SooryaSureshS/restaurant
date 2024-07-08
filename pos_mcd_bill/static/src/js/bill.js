odoo.define('pos_mcd_bill.bill', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const core = require('web.core');
    const QWeb = core.qweb;
    const { useRef, useContext } = owl.hooks;
    const { nextFrame } = require('point_of_sale.utils');


    class BillScreens extends PosComponent {
        constructor() {
            super(...arguments);
//            const client = order.get_client();

            this.widget = this.props.widget
            this.order = this.props.order
            this.type = this.props.type
//            this._receiptEnv = this.props.order.getOrderReceiptEnv();
//            var order = this.env.pos.get_order();
            this.orderReceipts = useRef('order-receipts');
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
            this.showScreen('PaymentScreen');
        }
        async printReceipt() {
          console.log("this valyesssss",this.orderReceipts)
          console.log("this valyesssss",this.orderReceipts.el.outerHTML)
        }
        async _printReceipt() {

            if (this.env.pos.proxy.printer) {
                const printResult = await this.env.pos.proxy.printer.print_receipt(this.orderReceipts.el.outerHTML);
                if (printResult.successful) {
                    return true;
                } else {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: printResult.message.title,
                        body: 'Do you want to print using the web printer?',
                    });
                    if (confirmed) {
                        // We want to call the _printWeb when the popup is fully gone
                        // from the screen which happens after the next animation frame.
//                        await nextFrame();
                        return await this._printWeb();
                    }
                    return false;
                }
            } else {
                return await this._printWeb();
            }
        }
        /**
         * https://stackoverflow.com/questions/21285902/printing-a-part-of-webpage-with-javascript
         */
        async _printWeb() {
            try {
                const isPrinted = document.execCommand('print', false, null);
                if (!isPrinted) window.print();
                return true;
            } catch (err) {
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Printing is not supported on some browsers'),
                    body: this.env._t(
                        'Printing is not supported on some browsers due to no default printing protocol ' +
                            'is available. It is possible to print your tickets by making use of an IoT Box.'
                    ),
                });
                return false;
            }
        }

//    async _printReceipt() {
//        if (this.env.pos.proxy.printer) {
//            var receipt = QWeb.render('OrderReceiptRecall',{'order_info': this.order, 'widget_info': this.widget});
//            const printResult = await this.env.pos.proxy.printer.print_receipt(receipt);
////            const printResult = await this.env.pos.proxy.printer.print_receipt(this.orderReceipt.el.outerHTML);
//            if (printResult.successful) {
//                return true;
//            } else {
//                const { confirmed } = await this.showPopup('ConfirmPopup', {
//                    title: printResult.message.title,
//                    body: 'Do you want to print using the web printer?',
//                });
//                if (confirmed) {
//                    // We want to call the _printWeb when the popup is fully gone
//                    // from the screen which happens after the next animation frame.
////                    await nextFrame();
//                    return await this._printWeb();
//                }
//                return false;
//            }
//        } else {
//            return await this._printWeb();
//        }
//    }
//    async _printWeb(receipt) {
//            try {
//                $(this.el).find('.pos-receipt-container').html(receipt);
//                const isPrinted = document.execCommand('print', false, null);
//                if (!isPrinted) window.print();
//            } catch (err) {
//                await this.showPopup('ErrorPopup', {
//                    title: this.env._t('Printing is not supported on some browsers'),
//                    body: this.env._t(
//                        'Printing is not supported on some browsers due to no default printing protocol ' +
//                            'is available. It is possible to print your tickets by making use of an IoT Box.'
//                    ),
//                });
//            }
//        }
    }

    BillScreens.template = 'BillScreens';

    Registries.Component.add(BillScreens);

    return BillScreens;
});
