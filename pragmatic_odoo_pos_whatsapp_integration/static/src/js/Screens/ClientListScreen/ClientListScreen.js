odoo.define('pragmatic_odoo_pos_whatsapp_integration.WhatsappClientListScreen', function (require) {
    'use strict';

    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    const WhatsappClientListScreen = (ClientListScreen) =>
        class extends ClientListScreen {
            constructor() {
                super(...arguments);
                useListener('click-whatsapp', (event) => this._sendWhatsapp(event));
            }
            async sendWhatsappMsg(payload) {
                await this.rpc({
                        model: 'pos.config',
                        method: 'action_send_whatsapp_msg',
                        args: [payload.template_id, payload.message, payload.mobileNo],
                    });
            }
            get selectionList() {
                let template_id = this.env.pos.config.whatsapp_msg_template_id ? this.env.pos.config.whatsapp_msg_template_id[0] : false
                const selectionList = this.env.pos.whatsapp_msg_templates.map(template => ({
                    id: template.id,
                    label: template.name,
                    isSelected: template.id === (template_id || this.env.pos.whatsapp_msg_templates[0].id),
                    message: template.message,
                }));
                return selectionList;
            }
            get whatsappPartner(){
                const partner = this.state.selectedClient || event.detail.client;
                return partner;
            }
            get whatsappSendMsgPopupDefaultValue() {
                const selectedTemplate = this.selectionList.filter(list => list.isSelected);
                const defaultValue = {
                    mobileNo: this.whatsappPartner && (this.whatsappPartner.mobile || this.whatsappPartner.phone || ''),
                    template_id: selectedTemplate.length && selectedTemplate[0].id,
                    message: selectedTemplate.length && selectedTemplate[0].message,
                };
                return defaultValue;
            }
            async _sendWhatsapp(event) {
                const { confirmed, payload: payload } = await this.showPopup('WhatsAppSendMsgPopup', {
                    startingValue: this.whatsappSendMsgPopupDefaultValue,
                    isSendGroup: false,
                    title: this.env._t('Send Message ?'),
                    body: this.env._t('Send a message to your customer on their Whatsapp number!'),
                    list: this.selectionList,
                });
                if (confirmed && payload) {
                    await this.sendWhatsappMsg(payload);
                }
            }
        };

    Registries.Component.extend(ClientListScreen, WhatsappClientListScreen);

    return WhatsappClientListScreen;
});