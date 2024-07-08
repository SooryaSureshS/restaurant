import json
import base64
import requests
import phonenumbers
import logging
from odoo import http
from odoo.http import request
from odoo.addons.phone_validation.tools import phone_validation
_logger = logging.getLogger(__name__)

from ...pragmatic_odoo_whatsapp_integration.controller.main import Whatsapp

class WhatsappMarketing(Whatsapp):


    @http.route(['/whatsapp/responce/message'], type='json', auth='public')
    def whatsapp_responce(self):
        res = super(WhatsappMarketing, self).whatsapp_responce()
        data = json.loads(request.httprequest.data)
        data = json.loads(request.httprequest.data)
        result = request.env['whatsapp.msg.res.partner']._default_unique_user()
        _request = data
        if 'messages' in data and data['messages']:
            msg_list = []
            msg_dict = {}
            whatsapp_contact_obj = request.env['whatsapp.contact']
            whatsapp_group_obj = request.env['whatsapp.group']
            odoo_group_obj = request.env['odoo.group']
            whatapp_msg = request.env['whatsapp.messages']
            for msg in data['messages']:
                # if msg.get('fromMe'):
                #     continue
                if 'chatId' in msg and msg['chatId']:
                    whatsapp_contact_obj = whatsapp_contact_obj.sudo().search([('whatsapp_id', '=', msg['chatId'])], limit=1)
                    whatsapp_group_obj = whatsapp_group_obj.sudo().search([('group_id', '=', msg['chatId'])],limit=1)
                    msg_dict = {
                        'name': msg['body'],
                        'message_id': msg['id'],
                        'fromMe': msg['fromMe'],
                        'to': msg['chatName'] if msg['fromMe'] == True else 'To Me',
                        'chatId': msg['chatId'],
                        'type': msg['type'],
                        'senderName': msg['senderName'],
                        'chatName': msg['chatName'],
                        'author': msg['author'],
                        'time': self.convert_epoch_to_unix_timestamp(msg['time']),
                        'state': 'sent' if msg['fromMe'] == True else 'received',
                    }
                    if whatsapp_contact_obj:
                        if msg['type'] == 'image' and whatsapp_contact_obj:
                            url = msg['body']
                            image_data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
                            msg_dict.update({'message_body': msg['caption'], 'whatsapp_contact_id': whatsapp_contact_obj.id, 'msg_image': image_data})
                        if whatsapp_contact_obj and msg['type'] == 'chat':
                            msg_dict.update({'message_body': msg['body'], 'whatsapp_contact_id': whatsapp_contact_obj.id})

                    if whatsapp_group_obj:
                        if msg['type'] == 'image' and whatsapp_group_obj:
                            url = msg['body']
                            image_data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
                            msg_dict.update({'message_body': msg['caption'], 'whatsapp_group_id': whatsapp_group_obj.id, 'msg_image': image_data })
                        if whatsapp_group_obj and msg['type'] == 'chat':
                            msg_dict.update({'message_body': msg['body'], 'whatsapp_group_id': whatsapp_group_obj.id})
                    if len(msg_dict) > 0:
                        msg_list.append(msg_dict)
            for msg in msg_list:
                whatapp_msg_id = whatapp_msg.sudo().search([('message_id', '=', msg.get('message_id'))])
                if whatapp_msg_id:
                    whatapp_msg_id.sudo().write(msg)
                    _logger.info("whatapp_msg_id %s: ", str(whatapp_msg_id))
                    if data.get('messages'):
                        for msg in data['messages']:
                            if whatapp_msg_id and msg['type'] == 'document':
                                msg_attchment_dict = {}
                                url = msg['body']
                                data_base64 = base64.b64encode(requests.get(url.strip()).content)
                                msg_attchment_dict = {'name': msg['caption'], 'datas': data_base64, 'type': 'binary',
                                                      'res_model': 'whatsapp.messages', 'res_id': whatapp_msg_id.id}
                                attachment_id = request.env['ir.attachment'].sudo().create(msg_attchment_dict)
                                res_update_whatsapp_msg = whatapp_msg_id.sudo().write({'attachment_id': attachment_id.id})
                                _logger.info("res_update_whatsapp_msg %s: ", str(res_update_whatsapp_msg))
                else:
                    res_create = whatapp_msg.sudo().create(msg)
                    _logger.info("In whatsapp_marketing_message res_create %s: ", str(res_create))
        return 'OK'
