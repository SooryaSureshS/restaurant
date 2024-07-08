odoo.define('pragmatic_odoo_pos_whatsapp_integration.GroupWhatsappMessageButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class GroupWhatsappMessageButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async chatList() {
            try {
                let response = await this.rpc({
                    model: 'pos.config',
                    method: 'get_whatsapp_chatlist',
                    args: [],
                });
                return response.chatList
            } catch (error) {
                if (error.message.code < 0) {
                    await this.showPopup('OfflineErrorPopup', {
                        title: this.env._t('Offline'),
                        body: this.env._t('Unable to load Whatsapp chat list.'),
                    });
                } else {
                    throw error;
                }
            }
        }
        async sendGroupWhatsappMsg(template_id, message, chatIds) {
            await this.rpc({
                model: 'pos.config',
                method: 'action_send_whatsapp_group_msg',
                args: [template_id, message, chatIds],
            });
        }
        async openGroupWhatsappMsgDialog(template) {
            const { confirmed, payload:payload } = await this.showPopup('WhatsAppGroupSelectPopup', {
                title: this.env._t("Send Message ?"),
                body: this.env._t("Send group whatsapp message!"),
                list: await this.chatList(),
            });
            if(confirmed && payload){
                await this.sendGroupWhatsappMsg(template.template_id, template.message, payload);
            }
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
        get whatsappSendMsgPopupDefaultValue() {
            const selectedTemplate = this.selectionList.filter(list => list.isSelected);
            const defaultValue = {
                mobileNo: '',
                template_id: selectedTemplate.length && selectedTemplate[0].id,
//                msgTemplate: selectedTemplate.length && selectedTemplate[0],
                message: selectedTemplate.length && selectedTemplate[0].message,
            };
            return defaultValue;
        }
        async onClick() {
            const { confirmed, payload: payload } = await this.showPopup('WhatsAppSendMsgPopup', {

                startingValue: this.whatsappSendMsgPopupDefaultValue,
                isSendGroup: true,
                title: this.env._t('Send Message ?'),
                body: this.env._t('Send a message to your customer on their Whatsapp number!'),
                list: this.selectionList,
            });

            if (confirmed && payload) {
                await this.openGroupWhatsappMsgDialog(payload);
            }
        }
    }
    GroupWhatsappMessageButton.template = 'GroupWhatsappMessageButton';

    ProductScreen.addControlButton({
        component: GroupWhatsappMessageButton,
        condition: function() {
            return this.env.pos.config.iface_whatsapp_grp_msg;
        },
    });

    Registries.Component.add(GroupWhatsappMessageButton);

    return GroupWhatsappMessageButton;
});
