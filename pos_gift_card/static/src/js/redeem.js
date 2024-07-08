odoo.define('pos_gift_card.redeem',function (require) {
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');

    class PaymentScreenGiftCardButton extends PosComponent {
        constructor() {
            super(...arguments);
        }
        async selectGfitCard (){
             const { confirmed } = await this.showPopup('RedeemCardPopupWidget',{});
        }
    }
    PaymentScreenGiftCardButton.template = 'PaymentScreenGiftCardButton';

    Registries.Component.add(PaymentScreenGiftCardButton);

    return PaymentScreenGiftCardButton;


});