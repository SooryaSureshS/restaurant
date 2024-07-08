odoo.define('pos_gift_card.pos',function (require) {
    "use strict";


    const { parse } = require('web.field_utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const { useErrorHandlers } = require('point_of_sale.custom_hooks');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { onChangeOrder } = require('point_of_sale.custom_hooks');
    var models = require('point_of_sale.models');
    var DB = require('point_of_sale.DB');
    var OrderReceipt = require('point_of_sale.OrderReceipt');

    models.load_models({
        model: 'pos.gift.card.type',
        fields: ['name'],
        loaded: function(self, card_type) {
            console.log("types",card_type);
            self.card_type = card_type;
        }
    });
    models.load_models({
        model: 'pos.gift.card',
        fields: ['card_no','card_value','card_type','customer_id','issue_date','expire_date','is_active'],
        domain: [['is_active', '=', true]],
        loaded: function(self, gift_cards) {
//            self.db.add_giftcard(gift_cards);
//            self.pos.set({'gift_card_order_list' : gift_cards});
            console.log("log cards",gift_cards);
            self.gift_card_order_lists = gift_cards
        }
    });

    var _super_paymentline = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        set_giftcard_line_code: function(code) {
            this.code = code;
        },
        get_giftcard_line_code: function(){
            return this.code;
        },
        set_freeze: function(freeze) {
            this.freeze = freeze;
        },
        get_freeze: function(){fr
            return this.freeze;
        },
    });


    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr,options) {
            _super_order.initialize.apply(this,arguments);
           this.giftcard = [];
           this.redeem =[];
           this.giftcard_barcode = '';
        },
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.giftcard = this.giftcard;
            json.redeem = this.redeem;
            json.giftcard_barcode = this.giftcard_barcode;
            return json;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);

            this.giftcard = json.giftcard || 1;
            this.redeem = json.redeem || 1;
            this.giftcard_barcode = json.giftcard_barcode;
        },
        export_for_printing: function() {
            var json = _super_order.export_for_printing.apply(this,arguments);
            json.giftcard = this.get_giftcard();
            json.redeem = this.get_redeem_giftcard();
            json.giftcard_barcode = this.get_giftcard_barcode();
            return json;
        },
        get_giftcard: function(){
            return this.giftcard;
        },
        set_giftcard: function(giftcard) {
            this.giftcard.push(giftcard)
//            this.gift_cards = gift_cards;
            this.trigger('change');
        },
        set_redeem_giftcard: function(redeem) {
            this.redeem.push(redeem)
        },
        get_redeem_giftcard: function() {
            return this.redeem;
        },
        get_giftcard_barcode: function(){
            return this.giftcard_barcode;
        },
        set_giftcard_barcode: function(giftcard_barcode) {
            this.giftcard_barcode = giftcard_barcode;
            this.trigger('change');
        },
    });


    class GiftScreenWidget extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
        }
        close() {
            $('#hide_div_collapse').show();
            this.showScreen('ProductScreen');
        }
        get filteredCardList() {
            var self = this;
            console.log("card order",self.env.pos);
            return self.env.pos.gift_card_order_lists;
        }
//        async CreateGiftCard() {
//            var self = this;
//
//        }
        async CreateGiftCard() {
            const order = this.env.pos.get_order();
            if (!order.get_client()) {
                const { confirmed: confirmedPopup } = await this.showPopup('ConfirmPopup', {
                    title: 'Need customer to gift card',
                    body: 'Do you want to open the customer list to select customer?',
                });
                if (!confirmedPopup) return;
                $('.gift_card_header_buttons').hide();
                $('.client-details-contents .client-details').css('background-color','snow');
                const { confirmed: confirmedTempScreen, payload: newClient } = await this.showTempScreen(
                    'ClientListScreen'
                );
                if (!confirmedTempScreen) {
                     $('.gift_card_header_buttons').show();
                }
                if (!confirmedTempScreen) return;
                $('.gift_card_header_buttons').show();
                const { confirmed } = await this.showPopup('CreateCardPopupWidget',{'partner_id': newClient});
            }else{
                const { confirmed } = await this.showPopup('CreateCardPopupWidget',{'partner_id': order.get_client()});
            }
        }
    }

    GiftScreenWidget.template = 'GiftScreen';

    Registries.Component.add(GiftScreenWidget);

    return GiftScreenWidget;


});