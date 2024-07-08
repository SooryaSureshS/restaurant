odoo.define('loyalty_pos.RewardButton', function(require) {
'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');
    var rpc = require('web.rpc');
    var core = require('web.core');

    var _t = core._t;


    class RewardButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.OnClick);
        }
         async OnClick(order_id) {
            var self = this;
            var order = self.env.pos.get_order();
            var loyaltyorderLines = [];
            _.each(order.get_orderlines(),function(item) {
                loyaltyorderLines.push(item.export_as_JSON());
            });

            if (!order.get_client()){
                const { confirmed: confirmedPopup } = await this.showPopup('ConfirmPopup', {
                    title: 'Please Choose a Customer',
                    body: 'You Must Have a Customer Before proceeding'
                });
                if (!confirmedPopup) return;
            }

            else if (!order || loyaltyorderLines.length === 0) {
                const { confirmed: confirmedPopup } = await this.showPopup('ConfirmPopup', {
                    title: 'Error',
                    body: 'You Must Have a Order And Order Lines',
                });
                if (!confirmedPopup) return;
            }
            else  {
                 var points = 0;
                rpc.query({
                    model: 'pos.config',
                    method: 'loyalty_points',
                    args: [order.get_client().id,self.env.pos.config.wk_loyalty_program_id[0],order.get_spent_points()],
                }).then(function (result) {
//                    points+=result;
                    order.customerLoyaltydata=result;
                    order.customerLoyaltyPoint=result.point;
                    if (result['result']==0){
                    self.env.pos.loyaltyrule=result['rule'];
                    self.env.pos.current_point=result['current_point'];

                        Gui.showPopup("PosloyaltyRule", {
                            title : _t("Rewards"),
                            confirmText: _t("Exit")
                        });
                        }
                    else if (result['result']=='no_point'){
                            self.env.pos.loyaltyrule=result['rule'];
                            self.env.pos.current_point=result['current_point'];
                            Gui.showPopup("PosloyaltyRule", {
                                    title : _t("Rewards"),
                                    confirmText: _t("Exit")
                        });
                    }
                    else{
                        Gui.showPopup("PosloyaltyPopup", {
                        title : _t("Rewards"),
                        confirmText: _t("Exit")
                    });
                }
                });


            }


        }
    }
    RewardButton.template = 'RewardButton';

    ProductScreen.addControlButton({
        component: RewardButton,
        condition: function() {
            return this.env.pos.config.pos_loyalty;
        },
    });

    Registries.Component.add(RewardButton);

    return RewardButton;
});
