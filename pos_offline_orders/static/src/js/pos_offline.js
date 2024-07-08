odoo.define('pos_offline_orders.pos_offline', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useState } = owl;
    var PosDB = require('point_of_sale.DB');
    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    var framework = require('web.framework');
    var core = require('web.core');
    var _t = core._t;

    class ClearCache extends PosComponent {
        constructor() {
            super(...arguments);
//            this.state = useState({ isUnlockIcon: true, title: 'Unlocked' });
        }
        async OfflineCache() {
            var self = this;
            var current_session = self.env.pos;
            console.log("logedddd",self.env.pos);
            if (self.env.pos.db.cache.unpaid_orders || self.env.pos.db.cache.orders){
                 Gui.showPopup("OfflinePopupConfirmPopupWidget", {
                    'title': this.env._t("PIN Error"),
                    'body':  this.env._t('Invalid PIN'),
                    'total_unpaid_orders': self.env.pos.db.cache.unpaid_orders.length,
                    'total_paid_orders': self.env.pos.db.cache.orders.length,
             });
            }



        }
//        onMouseOver(isMouseOver) {
//            this.state.isUnlockIcon = !isMouseOver;
//            this.state.title = isMouseOver ? 'Lock' : 'Unlocked';
//        }
    }
    ClearCache.template = 'SummaryButton1';

    Registries.Component.add(ClearCache);

    return ClearCache;

//odoo.define('pos_session_summary.SummaryButton', function(require) {
//    'use strict';
//
//    const { useState } = owl;
//    const PosComponent = require('point_of_sale.PosComponent');
//    const Registries = require('point_of_sale.Registries');
//
//    class SummaryButton extends PosComponent {
//        constructor() {
//            super(...arguments);
//        }
//
//        mounted() {
//            if(this.env.pos.user.kitchen_screen_user === 'cook'){
//                $('.status-buttons-portal .close_button').css("display", "none !important");
//            }
//            if(this.env.pos.user.kitchen_screen_user === 'manager'){
//                $('.status-buttons-portal .close_button').css("display", "none !important");
//            }
//            if(this.env.pos.user.kitchen_screen_user === 'admin'){
//                $('.status-buttons-portal .close_button').css("display", "none !important");
//            }
//        }
//
//        onClick() {
//            this.showScreen('ProductScreen');
//            var self = this;
//            var current_session = self.env.pos.pos_session.id;
//            this.rpc({
//                    model: 'pos.order',
//                    method: 'load_session_details',
//                    args: [current_session],
//                }).then(function (result) {
//                    if(result == false){
//                        if (self.env.pos.user.kitchen_screen_user == 'cook'){
//                            window.location.href = "/web/session/logout?redirect=/web/login";
//                        }
//                        else{
//                          window.location = '/web#action=point_of_sale.action_client_pos_menu';
//                        }
//
//                    }
//                    else{
//                        self.env.pos.session_data = result;
//                        self.showScreen('reportScreen');
//                    }
//                });
//
//
//        }
//    }
//    SummaryButton.template = 'SummaryButton';
//
//    Registries.Component.add(SummaryButton);
//
//    return SummaryButton;


});
