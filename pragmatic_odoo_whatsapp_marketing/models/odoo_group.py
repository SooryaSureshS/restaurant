import logging
import json
import requests
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class odooGroup(models.Model):
    _name = 'odoo.group'
    _description = 'Odoo Group'

    name = fields.Char('Name', required=True)
    active = fields.Boolean("Active", default=True)
    partner_ids = fields.Many2many(
        'res.partner', 'odoo_group_res_partner_rel',
        'wizard_id', 'partner_id', 'Associated Partner', domain="[('mobile', '!=', False), ('country_id', '!=', False)]")
    whatsapp_contact_id = fields.Many2many('whatsapp.contact', column1='odoo_group_id', column2='whatsapp_contact_id', string='Whatsapp Contact')
    odoo_group_id = fields.Char('Group Id')


    @api.model
    def create(self, vals):
        param = self.env['res.config.settings'].sudo().get_values()
        if vals.get('partner_ids'):
            if len(vals.get('partner_ids')[0][2]) >= 1:
                res_partner_ids = self.env['res.partner'].search([('id', 'in', vals.get('partner_ids')[0][2])])
                for res_partner_id in res_partner_ids:
                    whatsapp_number = res_partner_id.mobile
                    whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                    whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(res_partner_id.country_id.phone_code), "")
                    number = str(res_partner_id.country_id.phone_code) + res_partner_id.mobile
                    if res_partner_id.country_id.phone_code and res_partner_id.mobile:
                        phone_exists_url = param.get('whatsapp_endpoint') + '/checkPhone?token=' + param.get('whatsapp_token') + '&phone=' + str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                        phone_exists_response = requests.get(phone_exists_url)
                        json_response_phone_exists = json.loads(phone_exists_response.text)
                        if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and json_response_phone_exists['result'] == 'exists':
                            _logger.info("\nPartner phone exists")
                        else:
                            raise UserError(_('Please add valid whatsapp number for %s customer') % res_partner_id.name)
        res = super(odooGroup, self).create(vals)
        return res

    def write(self, vals):
        param = self.env['res.config.settings'].sudo().get_values()
        if vals.get('partner_ids'):
            if len(vals.get('partner_ids')[0][2]) >= 1:
                res_partner_ids = self.env['res.partner'].search([('id', 'in', vals.get('partner_ids')[0][2])])
                for res_partner_id in res_partner_ids:
                    whatsapp_number = res_partner_id.mobile
                    whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                    whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(res_partner_id.country_id.phone_code), "")
                    number = str(res_partner_id.country_id.phone_code) + res_partner_id.mobile
                    if res_partner_id.country_id.phone_code and res_partner_id.mobile:
                        phone_exists_url = param.get('whatsapp_endpoint') + '/checkPhone?token=' + param.get('whatsapp_token') + '&phone=' + str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                        phone_exists_response = requests.get(phone_exists_url)
                        json_response_phone_exists = json.loads(phone_exists_response.text)
                        if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and json_response_phone_exists['result'] == 'exists':
                            _logger.info("\nPartner phone exists")
                        else:
                            raise UserError(_('Please add valid whatsapp number for %s customer') % res_partner_id.name)
        res = super(odooGroup, self).write(vals)
        return res

class odoo_group_form(models.Model):
    _name = 'odoo.group.form'
    _description = 'Whatsapp Contact List Action'

    contact_ids = fields.Many2many(
        'odoo.group', 'odoo_group_odoo_group_form_action_rel',
        'wizard_id', 'odoo_group_id', 'Associated Partner')
    message = fields.Text('Message', required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'odoo_group_form_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')

    def action_send_msg_odoo_group(self):
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        param = self.env['res.config.settings'].sudo().get_values()
        status_url = param.get('whatsapp_endpoint') + '/status?token=' + param.get('whatsapp_token')
        status_response = requests.get(status_url)
        json_response_status = json.loads(status_response.text)
        if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status[
            'accountStatus'] == 'authenticated' and active_model == 'odoo.group':
            for res_partner_id in rec.partner_ids:
                number = str(res_partner_id.country_id.phone_code) + res_partner_id.mobile
                if rec.whatsapp_contact_id:
                    for contact_id in rec.whatsapp_contact_id:
                        if contact_id.sanitized_mobile != res_partner_id.mobile:
                            whatsapp_number = res_partner_id.mobile
                            whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                                '+' + str(res_partner_id.country_id.phone_code), "")
                            url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                            headers = {"Content-Type": "application/json"}
                            tmp_dict = {
                                "phone": "+" + str(
                                    res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                "body": self.message}
                            response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                            if response.status_code == 201 or response.status_code == 200:
                                _logger.info("\nSend Message successfully")
                            if self.attachment_ids:
                                for attachment in self.attachment_ids:
                                    with open("/tmp/" + attachment.name, 'wb') as tmp:
                                        encoded_file = str(attachment.datas)
                                        url_send_file = param.get('whatsapp_endpoint') + '/sendFile?token=' + param.get(
                                            'whatsapp_token')
                                        headers_send_file = {"Content-Type": "application/json"}
                                        dict_send_file = {
                                            "phone": "+" + str(
                                                res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                            "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                            "filename": attachment.name
                                        }
                                        response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                                        if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                            _logger.info("\nSend file attachment successfully11")

                elif not rec.whatsapp_contact_id:
                    whatsapp_number = res_partner_id.mobile
                    whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                    whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                        '+' + str(res_partner_id.country_id.phone_code), "")
                    url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                    headers = {"Content-Type": "application/json"}
                    tmp_dict = {
                        "phone": "+" + str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                        "body": self.message}
                    response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                    if response.status_code == 201 or response.status_code == 200:
                        _logger.info("\nSend Message successfully")
                    if self.attachment_ids:
                        for attachment in self.attachment_ids:
                            with open("/tmp/" + attachment.name, 'wb') as tmp:
                                encoded_file = str(attachment.datas)
                                url_send_file = param.get('whatsapp_endpoint') + '/sendFile?token=' + param.get(
                                    'whatsapp_token')
                                headers_send_file = {"Content-Type": "application/json"}
                                dict_send_file = {
                                    "phone": "+" + str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                    "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                    "filename": attachment.name
                                }
                                response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                                if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                    _logger.info("\nSend file attachment successfully11")
            for contact_id in rec.whatsapp_contact_id:
                url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                headers = {"Content-Type": "application/json"}
                tmp_dict = {"chatId": str(contact_id.whatsapp_id), "body": self.message}
                response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                if response.status_code == 201 or response.status_code == 200:
                    _logger.info("\nSend Message successfully")
                if self.attachment_ids:
                    for attachment in self.attachment_ids:
                        with open("/tmp/" + attachment.name, 'wb') as tmp:
                            encoded_file = str(attachment.datas)
                            url_send_file = param.get('whatsapp_endpoint') + '/sendFile?token=' + param.get(
                                'whatsapp_token')
                            headers_send_file = {"Content-Type": "application/json"}
                            dict_send_file = {
                                 "chatId": str(contact_id.whatsapp_id),
                                "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                "filename": attachment.name
                            }
                            response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                            if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                _logger.info("\nSend file attachment successfully11")
        else:
            raise UserError(_('Please authorize your mobile number with chat api'))


class odoo_group_target(models.Model):
    _name = 'odoo.group.list.action'
    _description = 'Whatsapp Contact List Action'

    contact_ids = fields.Many2many(
        'odoo.group', 'odoo_group_odoo_group_list_action_rel',
        'wizard_id', 'odoo_group_id', 'Associated Partner')
    message = fields.Text('Message', required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'odoo_group_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')

    def _get_records(self, model):
        if self.env.context.get('active_ids'):
            records = model.browse(self.env.context.get('active_ids', []))
        else:
            records = model.browse(self.env.context.get('active_id', []))
        return records

    @api.model
    def default_get(self, fields):
        result = super(odoo_group_target, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        model = self.env[active_model]
        records = self.env['whatsapp.group.list.action']._get_records(model)
        result['contact_ids'] = [(6, 0, records.ids)]
        return result

    def action_odoo_group_list(self):
        param = self.env['res.config.settings'].sudo().get_values()
        active_model = self.env.context.get('active_model')
        res_ids = self.env.context.get('active_ids')
        for res_id in res_ids:
            rec = self.env[active_model].browse(res_id)
            status_url = param.get('whatsapp_endpoint') + '/status?token=' + param.get('whatsapp_token')
            status_response = requests.get(status_url)
            json_response_status = json.loads(status_response.text)
            if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status[
                'accountStatus'] == 'authenticated':
                for res_partner_id in rec.partner_ids:
                    number = str(res_partner_id.country_id.phone_code) + res_partner_id.mobile
                    if res_partner_id.country_id.phone_code and res_partner_id.mobile:
                        mobile_list = rec.whatsapp_contact_id.mapped('sanitized_mobile')
                        if rec.whatsapp_contact_id:
                            for contact_id in rec.whatsapp_contact_id:
                                if contact_id.sanitized_mobile != res_partner_id.mobile:
                                    whatsapp_number = res_partner_id.mobile
                                    whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                                    whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                                        '+' + str(res_partner_id.country_id.phone_code), "")
                                    url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                                    headers = {"Content-Type": "application/json"}
                                    tmp_dict = {
                                        "phone": "+" + str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                        "body": self.message}
                                    response = requests.post(url, json.dumps(tmp_dict), headers=headers)

                                    if response.status_code == 201 or response.status_code == 200:
                                        _logger.info("\nSend Message successfully")
                                    if self.attachment_ids:
                                        for attachment in self.attachment_ids:
                                            with open("/tmp/" + attachment.name, 'wb') as tmp:
                                                encoded_file = str(attachment.datas)
                                                url_send_file = param.get('whatsapp_endpoint') + '/sendFile?token=' + param.get(
                                                    'whatsapp_token')
                                                headers_send_file = {"Content-Type": "application/json"}
                                                dict_send_file = {
                                                    "phone": "+" + str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                                    "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                                    "filename": attachment.name
                                                }
                                                response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                                                if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                                    _logger.info("\nSend file attachment successfully11")
                        elif not rec.whatsapp_contact_id:
                            whatsapp_number = res_partner_id.mobile
                            whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                                '+' + str(res_partner_id.country_id.phone_code), "")
                            url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                            headers = {"Content-Type": "application/json"}
                            tmp_dict = {
                                "phone": "+" + str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                "body": self.message}
                            response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                            if response.status_code == 201 or response.status_code == 200:
                                _logger.info("\nSend Message successfully")
                            if self.attachment_ids:
                                for attachment in self.attachment_ids:
                                    with open("/tmp/" + attachment.name, 'wb') as tmp:
                                        encoded_file = str(attachment.datas)
                                        url_send_file = param.get('whatsapp_endpoint') + '/sendFile?token=' + param.get(
                                            'whatsapp_token')
                                        headers_send_file = {"Content-Type": "application/json"}
                                        dict_send_file = {
                                            "phone": "+" + str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                            "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                            "filename": attachment.name
                                        }
                                        response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                                        if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                            _logger.info("\nSend file attachment successfully11")

                for contact_id in rec.whatsapp_contact_id:
                    url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                    headers = {"Content-Type": "application/json"}
                    tmp_dict = {"chatId": str(contact_id.whatsapp_id), "body": self.message}
                    response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                    if response.status_code == 201 or response.status_code == 200:
                        _logger.info("\nSend Message successfully")
                    if self.attachment_ids:
                        for attachment in self.attachment_ids:
                            with open("/tmp/" + attachment.name, 'wb') as tmp:
                                encoded_file = str(attachment.datas)
                                url_send_file = param.get('whatsapp_endpoint') + '/sendFile?token=' + param.get('whatsapp_token')
                                headers_send_file = {"Content-Type": "application/json"}
                                dict_send_file = {
                                    "chatId": str(contact_id.whatsapp_id),
                                    "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                    "filename": attachment.name
                                }
                                response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                                if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                    _logger.info("\nSend file attachment successfully11")
            else:
                raise UserError(_('Please authorize your mobile number with chat api'))
