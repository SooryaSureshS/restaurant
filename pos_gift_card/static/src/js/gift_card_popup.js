odoo.define('pos_gift_card.gift_card_popup', function(require) {
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
    class CreateCardPopupWidget extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        constructor() {
            super(...arguments);
            useExternalListener(window, 'keyup', this._jsBarcode);
               this.partner_id = useState({ partner_id: this.props.partner_id.id });
               this.partner_name = useState({ partner_id: this.props.partner_id.name });
               this.exp_date = useState(this.exp_date_array());
               this.card_type = this.env.pos.card_type;
               console.log("after",this);
        }
        _jsBarcode() {
            if ($('#card_no').val()){
                $("#test-barcode").JsBarcode($('#card_no').val());
                const order = this.env.pos.get_order();
                order.set_giftcard_barcode($("#test-barcode").attr("src"));
                console.log("data",$("#test-barcode").attr("src"));
            }
        }
        exp_date_array(array) {
            // If no array is provided, we initialize with one empty item.
           var date = new Date();
                date.setMonth(date.getMonth() + this.env.pos.config.default_exp_date);
                var new_date = date.getFullYear()+ "/" +(date.getMonth() + 1)+ "/" +date.getDate();
                return new_date
        }
        mounted() {
//            this.inputRef.el.focus();
        }
        async ClientScreen(){
            await this.showScreen('ClientListScreen');
        }
        async confirmed(){
            var self = this;
            var card_no = $('#card_no').val();
            var select_customer = $('#select_customer').data('partner_id');
            var text_expire_date = $('#text_expire_date').val();
            var text_amount = $('#text_amount').val();
            var select_card_type = $('#select_card_type').val();
            var expire_date = moment($('#text_expire_date').val(), 'YYYY/MM/DD').format('YYYY-MM-DD');
            var move = true;
            const order = this.env.pos.get_order();
            if (!card_no){
                alert('please enter card number');
            }
            if (!card_no){
                alert('please enter card number');
            }else{
                var params = {
                        model: 'pos.gift.card',
                        method: 'search_read',
                        domain: [['card_no', '=', $('#card_no').val()]],
                    }
                    this.rpc(params, {async: false}).then(function(gift_count){
                        gift_count = gift_count.length;
                        if(gift_count > 0){
                            $('#card_no').css('border', 'thin solid red');
                            alert("Card already exist");
                            move = false;
                        } else{
                            $('#card_no').css('border', '0px');
                                 if(select_customer){
                                        var client = self.env.pos.db.get_partner_by_id(select_customer);
                                    }
                                    var checkbox_paid = true;
                                    if(expire_date){
                                        if(checkbox_paid){
                                            $('#text_amount').focus();
                                            var input_amount =$('#text_amount').val();
                                            if(input_amount){
                                                order.set_client(client);
                                                var product = self.env.pos.db.get_product_by_id(self.env.pos.config.gift_card_product_id[0]);
                                                if (self.env.pos.config.gift_card_product_id[0]){
                                                    var orderlines=order.get_orderlines()
                                                    for(var i = 0, len = orderlines.length; i < len; i++){
                                                        order.remove_orderline(orderlines);
                                                    }
                                                    let selectedLine = self.env.pos.get_order().get_selected_orderline();
                                                    order.add_product(product, {price:input_amount});

                                                }
                                                var gift_order = {'giftcard_card_no': $('#card_no').val(),
                                                    'giftcard_customer': select_customer ? select_customer : false,
                                                    'giftcard_expire_date': moment($('#text_expire_date').val(), 'YYYY/MM/DD').format('YYYY-MM-DD'),
                                                    'giftcard_amount': $('#text_amount').val(),
                                                    'giftcard_customer_name': $("#select_customer").val(),
                                                    'card_type': $('#select_card_type').val(),
                                                }
                                                    order.set_giftcard(gift_order);
                                                     self.showScreen('PaymentScreen');
                                                     self.confirm();
                                            }else{
                                                alert("Please enter card value.")
                                                $('#text_amount').focus();
                                            }
                                        }
                                    }else{
                                        alert("Please select expire date.")
                                        $('#text_expire_date').focus();
                                    }

                        }
                    });
            }



        }
    }
    CreateCardPopupWidget.template = 'CreateCardPopupWidget';
    CreateCardPopupWidget.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',

    };

    Registries.Component.add(CreateCardPopupWidget);

    return CreateCardPopupWidget;

});
