import requests
import json
import datetime
from odoo.exceptions import UserError
from odoo import api, fields, models, _ , tools
import logging
_logger = logging.getLogger(__name__)


class SendWAMessageMarketing(models.TransientModel):
    _name = 'whatsapp.msg.marketing'
    _description = 'Send WhatsApp Message'
    _inherit =  ['mail.thread', 'mail.activity.mixin']

    def _default_unique_user(self):
        IPC = self.env['ir.config_parameter'].sudo()
        dbuuid = IPC.get_param('database.uuid')
        return dbuuid + '_' + str(self.env.uid)

    message = fields.Text('Message', required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'whatsapp_msg_marketing_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')
    unique_user = fields.Char(default=_default_unique_user)

    @api.model
    def default_get(self, fields):
        result = super(SendWAMessageMarketing, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        return result

    def action_send_msg_marketing(self):
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        param = self.env['res.config.settings'].sudo().get_values()
        status_url = param.get('whatsapp_endpoint') + '/status?token=' + param.get('whatsapp_token')
        status_response = requests.get(status_url)
        json_response_status = json.loads(status_response.text)
        if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status[
            'accountStatus'] == 'authenticated':
            if active_model == 'whatsapp.contact':
                url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                headers = {"Content-Type": "application/json"}
                tmp_dict = {"chatId": str(rec.whatsapp_id), "body": self.message}
                response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                if response.status_code == 201 or response.status_code == 200:
                    msg_dict = {
                        'message_body': self.message,
                        'fromMe': True,
                        'chatId': rec.whatsapp_id,
                        'type': 'chat',
                        'senderName': self.env.user.partner_id.name,
                        'chatName': rec.name,
                        'time': datetime.datetime.now(),
                        'whatsapp_contact_id': rec.id,
                        'state': 'sent',
                    }
                    _logger.info("\nSend Message to contact successfully")
                if self.attachment_ids:
                    for attachment in self.attachment_ids:
                        with open("/tmp/" + attachment.name, 'wb') as tmp:
                            encoded_file = str(attachment.datas)
                            url_send_file = param.get('whatsapp_endpoint') + '/sendFile?token=' + param.get('whatsapp_token')
                            headers_send_file = {"Content-Type": "application/json"}
                            dict_send_file = {
                                "chatId": str(rec.whatsapp_id),
                                "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                "filename": attachment.name
                            }
                            response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                            if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                _logger.info("\nSend file attachment successfully11")

            elif active_model == 'whatsapp.group':
                url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                headers = {"Content-Type": "application/json"}
                tmp_dict = {"chatId": str(rec.group_id), "body": self.message}
                response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                if response.status_code == 201 or response.status_code == 200:
                    msg_dict = {
                        'message_body': self.message,
                        'fromMe': True,
                        'chatId': rec.group_id,
                        'type': 'chat',
                        'senderName': self.env.user.partner_id.name,
                        'chatName': rec.name,
                        'time': datetime.datetime.now(),
                        'whatsapp_group_id': rec.id,
                        'state': 'sent',
                    }
                    # res_create = self.env['whatsapp.messages'].sudo().create(msg_dict)
                    _logger.info("\nSend Message to group successfully")

                if self.attachment_ids:
                    for attachment in self.attachment_ids:
                        with open("/tmp/" + attachment.name, 'wb') as tmp:
                            encoded_file = str(attachment.datas)
                            url_send_file = param.get('whatsapp_endpoint') + '/sendFile?token=' + param.get('whatsapp_token')
                            headers_send_file = {"Content-Type": "application/json"}

                            dict_send_file = {
                                "chatId": str(rec.group_id),
                                "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                "filename": attachment.name
                            }
                            response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                            if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                _logger.info("\nSend file attachment successfully11")
        else:
            raise UserError(_('Please authorize your mobile number with chat api'))
