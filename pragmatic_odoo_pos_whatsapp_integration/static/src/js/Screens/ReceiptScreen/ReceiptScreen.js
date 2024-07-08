odoo.define('pragmatic_odoo_pos_whatsapp_integration.WhatsappReceiptScreen', function (require) {
    'use strict';

    const { Printer } = require('point_of_sale.Printer');
    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');


    const WhatsappReceiptScreen = (ReceiptScreen) =>
        class extends ReceiptScreen {
            constructor() {
                super(...arguments);
                useListener('click-whatsapp-receipt', (event) => this._sendWhatsappReceipt());
            }
            /* override
                to send auto print to customer
            */
            mounted() {
                // Here, we send a task to the event loop that handles
                // the printing of the receipt when the component is mounted.
                // We are doing this because we want the receipt screen to be
                // displayed regardless of what happen to the handleAutoPrint
                // call.
                setTimeout(async () => await this.handleAutoPrint(), 0);
                if(this.env.pos.config.iface_whatsapp_receipt_auto){
                    this.sendWhatsappReceiptToCustomer();
                }
            }
            async sendWhatsappReceiptToCustomer() {
                const printer = new Printer(null, this.env.pos);
                const receiptString = this.orderReceipt.comp.el.outerHTML;
                const ticketImage = await printer.htmlToImg(receiptString);

                const order = this.currentOrder;
                const client = order.get_client();

                if(client && (client.mobile || client.phone)){
                    const orderName = order.get_name();
                    const order_server_id = this.env.pos.validated_orders_name_server_id_map[orderName];
                    const result = await this.rpc({
                            model: 'pos.config',
                            method: 'action_send_whatsapp_receipt',
                            args: [order_server_id, ticketImage, client.mobile || client.phone,client.country_id[0]],
                        });
                       if (result) {
//                       alert("Send Whatsapp Receipt Sucessfully.")
                        if (result == 'Whatsapp Message send successfully'){
                        Gui.showPopup('ConfirmPopup', {
                            title: 'Message',
                            body: result,
                        });
                       }
                       else{
                        Gui.showPopup('ErrorPopup', {
                            title: 'Message',
                            body: result,
                        });
                       }
                       }


                }
                else{
                     alert("You have not selected customer for this transaction")
                }
            }

            async _sendWhatsappReceipt() {
                await this.sendWhatsappReceiptToCustomer();
            }
        };

    Registries.Component.extend(ReceiptScreen, WhatsappReceiptScreen);

    Printer.include({
        htmlToImg: function (receipt) {
            var self = this;
            $('.pos-receipt-print').html(receipt);
            var promise = new Promise(function (resolve, reject) {
                self.receipt = $('.pos-receipt-print>.pos-receipt');
                self.receipt.css({"margin": "20px", "padding": "15px" });
                html2canvas(self.receipt[0], {
                    onparsed: function(queue) {
                        queue.stack.ctx.height = Math.ceil(self.receipt.outerHeight(true) + self.receipt.offset().top);
                    },
                    onrendered: function (canvas) {
                        $('.pos-receipt-print').empty();
                        resolve(self.process_canvas(canvas));
                    }
                })
            });
            return promise;
        },
    });


    return WhatsappReceiptScreen;
});
