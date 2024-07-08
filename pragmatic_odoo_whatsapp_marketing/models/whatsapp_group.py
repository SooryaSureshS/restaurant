import datetime
import logging
import json
import requests
from odoo.exceptions import UserError
from odoo import api, fields, models, _
logger = logging.getLogger(__name__)

class whatsappGroup(models.Model):
    _name = 'whatsapp.group'
    _description = 'Whatsapp Group'

    name = fields.Char('Name')
    active = fields.Boolean('Active', default=True)
    group_id = fields.Char('Group Id')
    whatsapp_contact = fields.Many2many('whatsapp.contact', 'whatsapp_group_contact_rel', 'whatsapp_group', 'whatsapp_contact','Whatsapp Contact')
    whatsapp_msg_whatsapp_group_ids = fields.One2many('whatsapp.messages', 'whatsapp_group_id', 'WhatsApp Messages')

    def _get_whatsapp_groups(self):
        param = self.env['res.config.settings'].sudo().get_values()
        whatsapp_group_dict = {}
        status_url = param.get('whatsapp_endpoint') + '/status?token=' + param.get('whatsapp_token')
        status_response = requests.get(status_url)
        json_response_status = json.loads(status_response.text)
        if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status[
            'accountStatus'] == 'authenticated':
            group_url = param.get('whatsapp_endpoint') + '/dialogs?token=' + param.get('whatsapp_token')
            group_response = requests.get(group_url)
            group_json_response = json.loads(group_response.text)
            if group_json_response:
                for dialog_dict in group_json_response['dialogs']:
                    if dialog_dict['metadata']['isGroup']:
                        if dialog_dict['id']:
                            whatsapp_group_dict['group_id'] = dialog_dict['id']
                        if dialog_dict['name']:
                            whatsapp_group_dict['name'] = dialog_dict['name']
                        if dialog_dict['metadata']['participants']:
                            whatsapp_contact_ids = self.env['whatsapp.contact'].search([('whatsapp_id', 'in', dialog_dict['metadata']['participants'])])
                            whatsapp_group_dict['whatsapp_contact'] = [(6, 0, whatsapp_contact_ids.ids)]
                        if whatsapp_group_dict:
                            whatsapp_group = self.sudo().search([('group_id', '=', whatsapp_group_dict['group_id'])])
                            if whatsapp_group:
                                whatsapp_group_write_record = whatsapp_group.sudo().write(whatsapp_group_dict)
                                logger.info("Write into existing Odoo whatsapp group----------- " + str(whatsapp_group.group_id))
                            else:
                                whatsapp_group_create_record = self.sudo().create(whatsapp_group_dict)
                                logger.info("Create into existing Odoo whatsapp group----------- " + str(whatsapp_group_create_record.id))
        else:
            raise UserError(_('Please authorize your mobile number with chat api'))


class whatsapp_group_target(models.Model):
    _name = 'whatsapp.group.list.action'
    _description = 'Whatsapp Group List Action'

    group_ids = fields.Many2many(
        'whatsapp.group', 'whatsapp_group_whatsapp_group_target_rel',
        'wizard_id', 'group_id', 'Whatsapp Groups')
    message = fields.Text('Message', required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'whatsapp_group_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')

    def _get_records(self, model):
        if self.env.context.get('active_ids'):
            records = model.browse(self.env.context.get('active_ids', []))
        else:
            records = model.browse(self.env.context.get('active_id', []))
        return records

    @api.model
    def default_get(self, fields):
        result = super(whatsapp_group_target, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        # res_id = self.env.context.get('active_id')
        model = self.env[active_model]
        records = self._get_records(model)
        result['group_ids'] = [(6, 0, records.ids)]
        return result

    def action_whatsapp_group_list(self):
        param = self.env['res.config.settings'].sudo().get_values()
        active_model = self.env.context.get('active_model')
        res_ids = self.env.context.get('active_ids')
        for res_id in res_ids:
            rec = self.env[active_model].browse(res_id)
            status_url = param.get('whatsapp_endpoint') + '/status?token=' + param.get('whatsapp_token')
            status_response = requests.get(status_url)
            json_response_status = json.loads(status_response.text)
            if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status['accountStatus'] == 'authenticated':
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
                    logger.info("\nSend Message successfully")
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
                                logger.info("\nSend file attachment successfully11")
            else:
                raise UserError(_('Please authorize your mobile number with chat api'))
