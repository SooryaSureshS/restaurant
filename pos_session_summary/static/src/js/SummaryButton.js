odoo.define('pos_session_summary.SummaryButton', function(require) {
    'use strict';

    const { useState } = owl;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class SummaryButton extends PosComponent {
        constructor() {
            super(...arguments);
        }

        mounted() {
            if(this.env.pos.user.kitchen_screen_user === 'cook'){
                $('.status-buttons-portal .close_button').css("display", "none !important");
            }
            if(this.env.pos.user.kitchen_screen_user === 'manager'){
                $('.status-buttons-portal .close_button').css("display", "none !important");
            }
            if(this.env.pos.user.kitchen_screen_user === 'admin'){
                $('.status-buttons-portal .close_button').css("display", "none !important");
            }
        }

        onClick() {
            this.showScreen('ProductScreen');
            var self = this;
            var current_session = self.env.pos.pos_session.id;
            this.rpc({
                    model: 'pos.order',
                    method: 'load_session_details',
                    args: [current_session],
                }).then(function (result) {
                    if(result == false){
                        if (self.env.pos.user.kitchen_screen_user == 'cook'){
                            window.location.href = "/web/session/logout?redirect=/web/login";
                        }
                        else{
                          window.location = '/web#action=point_of_sale.action_client_pos_menu';
                        }

                    }
                    else{
                        self.env.pos.session_data = result;
                        self.showScreen('reportScreen');
                    }
                });


        }
    }
    SummaryButton.template = 'SummaryButton';

    Registries.Component.add(SummaryButton);

    return SummaryButton;
});
