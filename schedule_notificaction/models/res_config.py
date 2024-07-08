# -*- coding: utf-8 -*-
from odoo import models, fields,tools, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_whatsapp_send_msg = fields.Boolean('Is Whats App')
    is_sms_send_msg = fields.Boolean('Is SMS')
    is_mail_send_msg = fields.Boolean("Is Email")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('schedule_notificaction.is_whatsapp_send_msg', self.is_whatsapp_send_msg)
        self.env['ir.config_parameter'].set_param('schedule_notificaction.is_sms_send_msg', self.is_sms_send_msg)
        self.env['ir.config_parameter'].set_param('schedule_notificaction.is_mail_send_msg', self.is_mail_send_msg)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            is_whatsapp_send_msg=self.env['ir.config_parameter'].sudo().get_param('schedule_notificaction.is_whatsapp_send_msg'),
            is_sms_send_msg=self.env['ir.config_parameter'].sudo().get_param('schedule_notificaction.is_sms_send_msg'),
            is_mail_send_msg=self.env['ir.config_parameter'].sudo().get_param('schedule_notificaction.is_mail_send_msg')
        )
        return res