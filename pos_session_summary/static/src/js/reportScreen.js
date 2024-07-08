odoo.define('pos_session_summary.reportScreen',function (require) {
    "use strict";


    const { parse } = require('web.field_utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const { useErrorHandlers } = require('point_of_sale.custom_hooks');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    var models = require('point_of_sale.models');
    const ajax = require('web.ajax');
    const { useExternalListener } = owl.hooks;

    class reportScreen extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
        }
        mounted() {

//          Cash Sales
            $('#input_cash').on('change', function(event) {
                var counted = $(event.currentTarget).val();
                var cash_counted = parseFloat(counted)
                var expected = $('#cash_expected');
                var cash_expected_count = parseFloat(expected.text())
                if (isNaN(cash_counted)){
                    cash_counted = 0;
                }
                if (isNaN(cash_expected_count)){
                    cash_expected_count = 0;
                }
                var cash_variance = cash_counted - cash_expected_count;
                var variance = $("#counted_variance").text(Math.round(cash_variance * 100) / 100)


//              Total Counted
                var eft_input = $('#input_eftpos')[0].value;
                var eftpos_expected_count = parseFloat(eft_input)
                if (isNaN(eftpos_expected_count)){
                    eftpos_expected_count = 0;
                }
                var total_counted = eftpos_expected_count + cash_counted;
                var counted_top = $("#counted_top").text(Math.round(total_counted * 100) / 100)


//              Total Variance
                var eft_variance = $('#eftpos_variance')[0].innerText;
                var eft_variance_count = parseFloat(eft_variance)
                if (isNaN(eft_variance_count)){
                    eft_variance_count = 0;
                }
                if (isNaN(cash_variance)){
                    cash_variance = 0;
                }
                var total_variance = eft_variance_count + cash_variance;
                var variance_top = $("#total_variance_top").text(Math.round(total_variance * 100) / 100)

//              Subtotal Counted
                var subtotal_counted = $("#subtotal_counted").text(Math.round(total_counted * 100) / 100)

//              Subtotal Variance
                var subtotal_variance = $("#subtotal_variance").text(Math.round(total_variance * 100) / 100)

//              Total Counted
                var total_counted = $("#total_counted").text(Math.round(total_counted * 100) / 100)

//              Total Variance
                var total_variance = $("#total_variance").text(Math.round(total_variance * 100) / 100)

//              Total Expected
                var expected_total = $('#subtotal_expected')[0].innerText;
                var expected_float = $('#subtotal_float_expected')[0].innerText;
                var subtotal = parseFloat(expected_total)
                var float_amount = parseFloat(expected_float)
                if (isNaN(subtotal)){
                    subtotal = 0;
                }
                if (isNaN(float_amount)){
                    float_amount = 0;
                }
                var expected_total_value = subtotal + float_amount
                var total_variance = $("#total_expected").text(Math.round(expected_total_value * 100) / 100)


            });


//          EFT-POS Sales
            $('#input_eftpos').on('change', function() {
                var counted = $(event.currentTarget).val();
                var eftpos_counted = parseFloat(counted)
                var expected = $('#eftpos_expected');
                var eftpos_expected_count = parseFloat(expected.text())
                if (isNaN(eftpos_counted)){
                    eftpos_counted = 0;
                }
                if (isNaN(eftpos_expected_count)){
                    eftpos_expected_count = 0;
                }
                var eftpos_variance = eftpos_counted - eftpos_expected_count;
                var variance = $("#eftpos_variance").text(Math.round(eftpos_variance * 100) / 100)


//              Total Counted
                var cash_input = $('#input_cash')[0].value;
                var cash_expected_count = parseFloat(cash_input)
                if (isNaN(cash_expected_count)){
                    cash_expected_count = 0;
                }
                var total_counted = cash_expected_count + eftpos_counted;
                var counted_top = $("#counted_top").text(Math.round(total_counted * 100) / 100)


//              Total Variance
                var cash_variance = $('#counted_variance')[0].innerText;
                var cash_variance_count = parseFloat(cash_variance)
                if (isNaN(cash_variance_count)){
                    cash_variance_count = 0;
                }
                if (isNaN(eftpos_variance)){
                    eftpos_variance = 0;
                }
                var total_variance = cash_variance_count + eftpos_variance;
                var variance_top = $("#total_variance_top").text(Math.round(total_variance * 100) / 100)

//              Subtotal Expected
                var subtotal_counted = $("#subtotal_counted").text(Math.round(total_counted * 100) / 100)

//              Subtotal Variance
                var subtotal_variance = $("#subtotal_variance").text(Math.round(total_variance * 100) / 100)

//              Total Counted
                var total_counted = $("#total_counted").text(Math.round(total_counted * 100) / 100)

//              Total Variance
                var total_variance = $("#total_variance").text(Math.round(total_variance * 100) / 100)

//              Total Expected
                var expected_total = $('#subtotal_expected')[0].innerText;
                var expected_float = $('#subtotal_float_expected')[0].innerText;
                var subtotal = parseFloat(expected_total)
                var float_amount = parseFloat(expected_float)
                if (isNaN(subtotal)){
                    subtotal = 0;
                }
                if (isNaN(float_amount)){
                    float_amount = 0;
                }
                var expected_total_value = subtotal + float_amount
                var total_variance = $("#total_expected").text(Math.round(expected_total_value * 100) / 100)

            });

        }
        get SessionUserDetails(){
            var self = this;
        }

        async printAndClose(){


            var current_order = this.env.pos.get_order();
            var self = this;

            var open_orders = self.env.pos.orders_open;
            var cash_input = $('#input_cash')[0].value;
            var cash_expected_count = parseFloat(cash_input)
            var eftpos_input = $('#input_eftpos')[0].value;
            var eftpos_expected_count = parseFloat(eftpos_input)
            var opening_balance_session = $('#opening_balance')[0].value;
            if (isNaN(cash_expected_count) || isNaN(eftpos_expected_count)) {
               await this.showPopup('ErrorPopup', {
                    title: 'Fill the required fields',
                    body: 'Please enter the counted value for both Cash and Eftpos',
                });
            }
            else if ((current_order !== null) && (current_order.orderlines.length > 0)) {
               await this.showPopup('ErrorPopup', {
                    title: 'Unpaid Order',
                    body: 'Please complete the unpaid orders',
                });
            }
            else{
                $('#print_and_close').hide()
                var current_session = this.env.pos.session_data['id'];
//              Counted Cash
                var cash_input = $('#input_cash')[0].value;
                var counted_cash = parseFloat(cash_input)
                if (isNaN(counted_cash)){
                    counted_cash = 0;
                }
//              Counted EFTPOS
                var eft_input = $('#input_eftpos')[0].value;
                var counted_eftpos = parseFloat(eft_input)
                if (isNaN(counted_eftpos)){
                    counted_eftpos = 0;
                }

//              Counted Total
                var total_input = $('#counted_top')[0].innerText;
                var counted_total = parseFloat(total_input)
                if (isNaN(counted_total)){
                    counted_total = 0;
                }

//              Counted Cash Variance
                var cash_variance = $('#counted_variance')[0].innerText;

//              Counted Cash Variance
                var eftpos_variance = $('#eftpos_variance')[0].innerText;

//              Total Variance
                var total_variance = $('#total_variance_top')[0].innerText;

//              Float/Opening Balance
                var opening_balance_value = $('#opening_balance')[0].value;

//              Voucher/Gift Card
                var total_voucher = $('#total_redeen_amount')[0].innerText;

//              Discount
                var total_discount = $('#total_discount_amount')[0].innerText;

//              Discount
                var total_loyalty_amount = $('#total_loyalty_amount')[0].innerText;
                var total_tips_amount = $('#total_tips_amount')[0].innerText;
                var self = this;

                this.rpc({
                    model: 'pos.order',
                    method: 'CheckUnpaidOpenOrders',
                    args: [current_session],
                }).then(function (result) {
                    if(result == true){
                       self.showPopup('ErrorPopup', {
                            title: 'Open Orders',
                            body: 'Please Complete the Open and Unpaid Orders',
                        });
                    }
                    else{
                        self.rpc({
                            model: 'pos.order',
                            method: 'printAndClose',
                            args: [current_session, counted_cash, counted_eftpos,counted_total,cash_variance, eftpos_variance, total_variance, opening_balance_value, total_voucher, total_discount, total_loyalty_amount, total_tips_amount],
                        }).then(function (result) {
                            if(result == true){
                                if (self.env.pos.user.kitchen_screen_user == 'cook'){
                                    window.location.href = "/web/session/logout?redirect=/web/login";
                                }
                                else{
                                  window.location = '/web#action=point_of_sale.action_client_pos_menu';
                                }
                            }
                            else{
                               self.showPopup('ErrorPopup', {
                                    title: 'Try Again',
                                    body: 'Something went wrong. Please try after sometime.',
                                });
                                $('#print_and_close').show()
                            }
                        });
                    }
                });





            }

        }

        close() {
            if(this.env.pos.user.kitchen_screen_user === 'cook'){
                this.showScreen('kitchenScreenWidget');
            }
            else if(this.env.pos.user.kitchen_screen_user === 'manager'){
                this.showScreen('kitchenScreenWidget');
            }
            else if(this.env.pos.user.kitchen_screen_user === 'admin'){
                this.showScreen('ProductScreen');
            }
        }
    }

    reportScreen.template = 'reportScreen';

    Registries.Component.add(reportScreen);

    return reportScreen;


});