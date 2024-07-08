odoo.define('pragmatic_odoo_pos_whatsapp_integration.WhatsAppSendMsgPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class WhatsAppSendMsgPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            useListener('click-template', this._msgTemplateChange);
            this.state = useState({ mobileNo: this.props.startingValue.mobileNo,
                                    template_id: this.props.startingValue.template_id,
                                    message: this.props.startingValue.message});
            this.MobileNoInputRef = useRef('mobileNoInput');
            this.MsgInput = useRef('MsgInput');
            this.MsgTemplate = useRef('MsgTemplate');
        }
        mounted() {
            if(this.MobileNoInputRef.el){
                this.MobileNoInputRef.el.focus();
            }else{
                this.MsgInput.el.focus();
            }
        }
        getPayload() {
            return this.state;
        }
        _msgTemplateChange(event) {
            const item = this.props.list.find((item) => item.id === parseFloat(this.state.template_id));
            this.state.message = item.message;
        }
    }
    WhatsAppSendMsgPopup.template = 'WhatsAppSendMsgPopup';
    WhatsAppSendMsgPopup.defaultProps = {
        confirmText: 'Send',
        cancelText: 'Cancel',
        title: 'Send Message',
        body: 'Send a message to your customer on their Whatsapp number!',
        startingValue: '',
    };

    Registries.Component.add(WhatsAppSendMsgPopup);

    return WhatsAppSendMsgPopup;
});