odoo.define('kitchen_order.kitchen_screen_receipt', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PopupControllerMixin = require('point_of_sale.PopupControllerMixin')
    const Chrome = require('point_of_sale.Chrome');
    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');

    class ReceiptScreenCustom extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
            useListener('printReceipt', this._printReceipt);
        }
        close() {
            this.showScreen('kitchenScreenWidget');
        }
        async _printReceipt() {
            if (this.env.pos.proxy.printer) {
                const printResult = await this.env.pos.proxy.printer.print_receipt(this.orderReceipt.el.outerHTML);
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
                        await nextFrame();
                        return await this._printWeb();
                    }
                    return false;
                }
            } else {
                return await this._printWeb();
            }
        }
//        willUpdateProps(nextProps) {
//            this._receiptEnv = nextProps.order.getOrderReceiptEnv();
//        }
//        get receipt() {
//            return this.receiptEnv.receipt;
//        }
//        get orderlines() {
//            return this.receiptEnv.orderlines;
//        }
//        get paymentlines() {
//            return this.receiptEnv.paymentlines;
//        }
//        get isTaxIncluded() {
//            return Math.abs(this.receipt.subtotal - this.receipt.total_with_tax) <= 0.000001;
//        }
//        get receiptEnv () {
//          return this._receiptEnv;
//        }
//        isSimple(line) {
//            return (
//                line.discount === 0 &&
//                line.unit_name === 'Units' &&
//                line.quantity === 1 &&
//                !(
//                    line.display_discount_policy == 'without_discount' &&
//                    line.price != line.price_lst
//                )
//            );
//        }

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
    ReceiptScreenCustom.template = 'ReceiptScreenCustom';

    Registries.Component.add(ReceiptScreenCustom);

    return ReceiptScreenCustom;
});