odoo.define('loyalty_pos.loyaltyClientScreen', function(require) {
'use strict';
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const utils = require('web.utils');
    const round_pr = utils.round_precision;
     const LoyaltyListScreen = ClientListScreen =>class  extends ClientListScreen {
             async customer_sync() {
                var self = this;
                    var params = {
                        model: 'pos.order',
                        method: 'get_client_sync',
                        args: [],
                    }
                    self.rpc(params, {async: false}).then(function(result){
                            if (result){
                            for (var line of self.env.pos.partners){
                                 for (var partner of result){
                                if (line.id==partner.id){
                                 // Reward products are ignored
                                   line.wk_website_loyalty_points=partner.wk_website_loyalty_points;
                                }
                                }
                               }
                            }
                            self.render();
                            });
        }
        }
        Registries.Component.extend(ClientListScreen, LoyaltyListScreen);

        return ClientListScreen;
});