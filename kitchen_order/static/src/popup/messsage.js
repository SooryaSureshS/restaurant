odoo.define('kitchen_order.messsage', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PopupControllerMixin = require('point_of_sale.PopupControllerMixin')
    const Chrome = require('point_of_sale.Chrome');
    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    var session = require('web.Session');
    const ajax = require('web.ajax');

   models.load_models({
        model:  'pos.session',
        fields: ['id', 'name', 'user_id', 'config_id', 'start_at', 'stop_at', 'sequence_number', 'payment_method_ids', 'cash_register_id', 'state'],
        domain: function(self){
            var domain = [
                ['state','in',['opening_control','opened']],
                ['rescue', '=', false],
            ];
            return domain;
        },
        loaded: function(self, pos_sessions){
            self.pos_session_db = pos_sessions;

        },
        },
        {
        model: 'pos.config',
        fields: [],
        loaded: function(self, config){
            self.pos_config_db = config;
        }

    });

    /*Kitchen order button for view the kitchen screen for managers*/
    class MessageButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
            var self = this;
            console.log("info",self)
            const { confirmed, payload: inputPin } = await Gui.showPopup('TextAreaPopupUpdates', {
                                title: 'Message To Kitchen Screen',
                                session: self.env.pos.pos_session_db,

                 });
                 var session_id = self.env.pos.pos_session.id;
                 if (confirmed){
                    if (inputPin['inputValue'] !== undefined){
                        ajax.rpc("/upadate/message", {'inputPin': inputPin, 'session_id':session_id}).then(function (result) {
                        });
                    }
                 }
        }
    }
    MessageButton.template = 'MessageButton';

    ProductScreen.addControlButton({
        component: MessageButton,
        condition: function() {
            return this.env.pos.config.send_message;
        },
    });

    Registries.Component.add(MessageButton);

    return MessageButton;


});