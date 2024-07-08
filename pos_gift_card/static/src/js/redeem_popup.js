odoo.define('pos_gift_card.redeem_popup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
      const { useExternalListener } = owl.hooks;
    // formerly TextAreaPopupWidget
    // IMPROVEMENT: This code is very similar to TextInputPopup.
    //      Combining them would reduce the code.
    class RedeemCardPopupWidget extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        constructor() {
            super(...arguments);
//            useExternalListener(window, 'focusout', this._giftCardScan);

        }
        async _giftCardScan() {
            console.log("scan barcode",$('#text_gift_card_no').val());
            var self = this;
            if ($('#text_gift_card_no').val()){
                if ( $('#text_gift_card_no').val().length != 0){
                     console.log("scan barcode val",$('#text_gift_card_no').val());
                    const order = this.env.pos.get_order();
                    var today = moment().format('YYYY-MM-DD');
                    var code = $('#text_gift_card_no').val();
                    var code = $('#text_gift_card_no').val();
                    $("#test-barcode").JsBarcode(code);
                    var get_redeems = order.get_redeem_giftcard();
                    var existing_card = _.where(get_redeems, {'redeem_card': code });
                    var params = {
                        model: 'pos.gift.card',
                        method: 'search_read',
                        domain: [['card_no', '=', code], ['expire_date', '>=', today], ['issue_date', '<=', today]],
                    }
                    this.rpc(params, {async: false})
                    .then(function(res){
                        console.log("red", res)
                        if(res.length > 0){
                            if (res[0]){
                                if(existing_card.length > 0){
                                    res[0]['card_value'] = existing_card[existing_card.length - 1]['redeem_remaining']
                                }

                                self.redeem = res[0];
                                $('#lbl_card_no').html("Your Balance is  "+ self.env.pos.format_currency(res[0].card_value));
                                if(res[0].customer_id[1]){
                                    $('#lbl_set_customer').html("Hello  "+ res[0].customer_id[1]);
                                } else{
                                    $('#lbl_set_customer').html("Hello  ");
                                }

                                if(res[0].card_value <= 0){
                                    $('#redeem_amount_row').hide();
                                    $('#in_balance').show();
                                }else{
                                    $('#redeem_amount_row').fadeIn('fast');
                                    $('#text_redeem_amount').focus();

//                                    edited
                                    if (res[0].card_value >0){
                                        if (res[0].card_value > order.get_due()){
                                            $('#text_redeem_amount').val(order.get_due());
                                        }else{
                                            $('#text_redeem_amount').val(res[0].card_value);
                                        }
                                    }
                                }
                            }
                        }
                        else{
                            alert("Barcode not found or gift card has been expired");
                            $('#text_gift_card_no').focus();
                            $('#lbl_card_no').html('');
                            $('#lbl_set_customer').html('');
                            $('#in_balance').html('');
                            return true
                        }
                    });
                }


            }
        }
        async confirmed(){
            var self = this;
            const order = this.env.pos.get_order();
            var client = order.get_client();
            var redeem_amount = $('#text_redeem_amount').val();
            var code = $('#text_gift_card_no').val();
            $("#test-barcode").JsBarcode(code);
            if(self.redeem.card_no){
                if(code == self.redeem.card_no){
                    if(!self.redeem.card_value == 0){
                        if(redeem_amount){
                            if (redeem_amount <= (order.get_due() || order.get_total_with_tax())){
                                if(!client){
                                    order.set_client(self.env.pos.db.get_partner_by_id(self.redeem.customer_id[0]));
                                }
                                if( 0 < Number(redeem_amount)){
                                    if(self.redeem && self.redeem.card_value >= Number(redeem_amount) ){
                                        if(self.redeem.customer_id[0]){
                                            var vals = {
                                                'redeem_card_no':self.redeem.id,
                                                'redeem_card':$('#text_gift_card_no').val(),
                                                'redeem_card_amount':$('#text_redeem_amount').val(),
                                                'redeem_remaining':self.redeem.card_value - $('#text_redeem_amount').val(),
                                                'card_customer_id': client ? client.id : self.redeem.customer_id[0],
                                                'customer_name': client ? client.name : self.redeem.customer_id[1],
                                                'barcode': $("#test-barcode").attr("src"),
                                            };
                                        } else {
                                            var vals = {
                                                'redeem_card_no':self.redeem.id,
                                                'redeem_card':$('#text_gift_card_no').val(),
                                                'redeem_card_amount':$('#text_redeem_amount').val(),
                                                'redeem_remaining':self.redeem.card_value - $('#text_redeem_amount').val(),
                                                'card_customer_id': order.get_client() ? order.get_client().id : false,
                                                'customer_name': order.get_client() ? order.get_client().name : '',
                                                'barcode':  $("#test-barcode").attr("src"),
                                            };
                                        }
                                        var get_redeem = order.get_redeem_giftcard();
                                        console.log("get redeem gift card",self.env.pos.payment_methods);
                                        console.log("get redeem gift card",get_redeem);
                                        if(get_redeem){
                                            if(self.env.pos.config.enable_journal_id[0]){
                                                var cashregisters = null;
                                                for ( var j = 0; j < self.env.pos.payment_methods.length; j++ ) {
                                                    if ( self.env.pos.payment_methods[j].id === self.env.pos.config.enable_journal_id[0] ){
                                                       cashregisters = self.env.pos.payment_methods[j];
                                                    }
                                                }
                                            }
                                             console.log("inside get redeem gift card",cashregisters);
                                             console.log("inside get redeem gift card",self.env.pos.config.enable_journal_id[0]);
                                             console.log("vals",vals);
                                            if (vals){
                                                if (cashregisters){
                                                    order.add_paymentline(cashregisters);
                                                    order.selected_paymentline.set_amount( Math.max(redeem_amount),0 );
                                                    order.selected_paymentline.set_giftcard_line_code(code);
                                                    order.set_redeem_giftcard(vals);
                                                    self.confirm();
                                                }
                                            }
                                        }
                                    }else{
                                        alert("Please enter amount below card value.");
                                        $('#text_redeem_amount').focus();
                                    }
                                }else{
                                    alert("Please enter valid amount.");
                                    $('#text_redeem_amount').focus();
                                }
                            }else{
                                alert("Card amount should be less than or equal to Order Due Amount.");
                            }

                        }else{
                            alert("Please enter amount.");
                            $('#text_redeem_amount').focus();
                        }
                    }
                }else{
                    alert("Please enter valid barcode.");
                    $('#text_gift_card_no').focus();
                }
            }else{
                alert("Press enter key.");
                $('#text_gift_card_no').focus();
            }

        }


    }
    RedeemCardPopupWidget.template = 'RedeemCardPopupWidget';
    RedeemCardPopupWidget.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',

    };

    Registries.Component.add(RedeemCardPopupWidget);

    return RedeemCardPopupWidget;

});
