import logging
import json
import requests
import phonenumbers
import datetime
from odoo.exceptions import UserError
from odoo import api, fields, models, _
logger = logging.getLogger(__name__)
from odoo.addons.phone_validation.tools import phone_validation



class whatsapp_contact(models.Model):
    _name = 'whatsapp.contact'
    _description = 'Whatsapp Contact'

    name = fields.Char('Name')
    mobile = fields.Char('Mobile')
    whatsapp_id = fields.Char('Whatsapp id')
    partner_id = fields.Many2one('res.partner','Partner', domain="[('mobile', '!=', False), ('country_id', '!=', False)]")
    whatsapp_group = fields.Many2many('whatsapp.group', 'whatsapp_contact_group_rel', 'whatsapp_contact', 'whatsapp_group','Whatsapp Group')
    odoo_group_id = fields.Many2many('odoo.group', column1='whatsapp_contact_id', column2='odoo_group_id', string='Odoo Group')

    active = fields.Boolean('Active', default=True)
    whatsapp_msg_ids = fields.One2many('whatsapp.messages', 'whatsapp_contact_id', 'WhatsApp Messages')
    chatId = fields.Char('Chat ID')
    sanitized_mobile = fields.Char('Sanitized Mobile')

    def write(self, vals):
        if vals.get('partner_id'):
            res_partner_id = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
            param = self.env['res.config.settings'].sudo().get_values()
            status_url = param.get('whatsapp_endpoint') + '/status?token=' + param.get('whatsapp_token')
            status_response = requests.get(status_url)
            json_response_status = json.loads(status_response.text)
            if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status[
                'accountStatus'] == 'authenticated':
                whatsapp_number = res_partner_id.mobile
                whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(res_partner_id.country_id.phone_code), "")
                number = str(res_partner_id.country_id.phone_code) + res_partner_id.mobile
                if res_partner_id.country_id.phone_code and res_partner_id.mobile:
                    phone_exists_url = param.get('whatsapp_endpoint') + '/checkPhone?token=' + param.get(
                        'whatsapp_token') + '&phone=' + str(
                        res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                    phone_exists_response = requests.get(phone_exists_url)
                    json_response_phone_exists = json.loads(phone_exists_response.text)
                    if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and json_response_phone_exists['result'] == 'exists':
                        logger.info("\nPartner phone exists")
                        res = super(whatsapp_contact, self).write(vals)
                    else:
                        raise UserError(_('Please add valid whatsapp number for %s customer') % res_partner_id.name)

        return super(whatsapp_contact, self).write(vals)

    @api.model
    def create(self, vals):
        res = super(whatsapp_contact, self).create(vals)
        return res

    def _get_whatsapp_contacts(self):
        param = self.env['res.config.settings'].sudo().get_values()
        whatsapp_contact_dict = {}
        status_url = param.get('whatsapp_endpoint')+'/status?token='+param.get('whatsapp_token')
        status_response = requests.get(status_url)
        json_response_status = json.loads(status_response.text)
        if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status[
            'accountStatus'] == 'authenticated':
            contact_url = param.get('whatsapp_endpoint')+'/dialogs?token='+param.get('whatsapp_token')
            contact_response = requests.get(contact_url)
            contact_json_response = json.loads(contact_response.text)
            if contact_json_response:
                for dialog_dict in contact_json_response['dialogs']:
                    if not dialog_dict['metadata']['isGroup']:
                        if dialog_dict['id']:
                            whatsapp_contact_dict['whatsapp_id'] = dialog_dict['id']
                            whatsapp_contact_dict['mobile'] = (dialog_dict['id'])[:-5]
                            mobile = "+"+whatsapp_contact_dict['mobile']
                        if dialog_dict['name']:
                            whatsapp_contact_dict['name'] = dialog_dict['name']
                        chatid_split = dialog_dict.get('id').split('@')
                        mobile = '+' + chatid_split[0]
                        mobile_coutry_code = phonenumbers.parse(mobile, None)
                        mobile_number = mobile_coutry_code.national_number
                        res_country_id = self.env['res.country'].sudo().search([('phone_code', '=', mobile_coutry_code.country_code)], limit=1)
                        reg_sanitized_number = phone_validation.phone_format(str(mobile_number), res_country_id.code, mobile_coutry_code.country_code)
                        res_partner_id = self.env['res.partner'].sudo().search([('mobile', '=', reg_sanitized_number)], limit=1)
                        whatsapp_contact_dict['sanitized_mobile'] = reg_sanitized_number
                        if res_partner_id:
                            whatsapp_contact_dict['partner_id'] = res_partner_id.id
                        if whatsapp_contact_dict:
                            whatsapp_contact = self.sudo().search([('whatsapp_id', '=', whatsapp_contact_dict['whatsapp_id'])])
                            if whatsapp_contact:
                                whatsapp_contact_write_record = whatsapp_contact.sudo().write(whatsapp_contact_dict)
                                logger.info("Write into existing Odoo whatsapp contact----------- " + str(whatsapp_contact.whatsapp_id))
                                whatsapp_group = self.env['whatsapp.group'].search([('whatsapp_contact', 'in', whatsapp_contact.id)])
                                if whatsapp_group:
                                    whatsapp_contact_write =  whatsapp_contact.sudo().write({'whatsapp_group':[(6, 0, whatsapp_group.ids)]})
                            else:
                                whatsapp_contact_create_record = self.sudo().create(whatsapp_contact_dict)
                                logger.info("Create into existing Odoo whatsapp contact----------- " + str(whatsapp_contact_create_record.id))
        else:
            raise UserError(_('Please authorize your mobile number with chat api'))

    def _sms_get_default_partners(self):
        """ Override of mail.thread method.
            SMS recipients on partners are the partners themselves.
        """
        return self

class whatsapp_contact_target(models.Model):
    _name = 'whatsapp.contact.list.action'
    _description = 'Whatsapp Contact List Action'

    contact_ids = fields.Many2many(
        'whatsapp.contact', 'whatsapp_contact_whatsapp_contact_target_rel',
        'wizard_id', 'contact_id', 'Whatsapp Contacts')
    message = fields.Text('Message', required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'whatsapp_contact_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')

    def _get_records(self, model):
        if self.env.context.get('active_ids'):
            records = model.browse(self.env.context.get('active_ids', []))
        else:
            records = model.browse(self.env.context.get('active_id', []))
        return records

    @api.model
    def default_get(self, fields):
        result = super(whatsapp_contact_target, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        # res_id = self.env.context.get('active_id')
        model = self.env[active_model]
        records = self.env['whatsapp.group.list.action']._get_records(model)
        result['contact_ids'] = [(6, 0, records.ids)]
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
                tmp_dict = {"chatId": str(rec.whatsapp_id), "body": self.message}
                response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                if response.status_code == 201 or response.status_code == 200:
                    msg_dict = {
                        # 'name': self.message,
                        'message_body': self.message,
                        # 'message_id': msg['id'],
                        'fromMe': True,
                        # 'to': rec.name,
                        'chatId': rec.whatsapp_id,
                        'type': 'chat',
                        'senderName': self.env.user.partner_id.name,
                        'chatName': rec.name,
                        # 'author': rec.name,
                        'time': datetime.datetime.now(),
                        'whatsapp_group_id': rec.id,
                        'state': 'sent',
                    }
                    # res_create = self.env['whatsapp.messages'].sudo().create(msg_dict)
                    logger.info("\nSend Message successfully")
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
                                logger.info("\nSend file attachment successfully11")
            else:
                raise UserError(_('Please authorize your mobile number with chat api'))




