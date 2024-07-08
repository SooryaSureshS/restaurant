import logging
import requests
import json
import random
import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
from ast import literal_eval
_logger = logging.getLogger(__name__)
WHATSAPP_BUSINESS_MODELS = [
    'crm.lead',
    'event.registration',
    'hr.applicant',
    'res.partner',
    'event.track',
    'sale.order',
    'odoo.group',
    'whatsapp.group',
    'whatsapp.contact'
]

class whatsapp_marketing(models.Model):
    _name = 'whatsapp.marketing'
    _inherit = ['mail.render.mixin']
    _description = 'Whatsapp Message'

    whatsapp_model_id = fields.Many2one('ir.model', string='Recipients', ondelete='cascade', required=True,
                                        domain=[('model', 'in', WHATSAPP_BUSINESS_MODELS)],
                default = lambda self: self.env.ref('pragmatic_odoo_whatsapp_marketing.model_odoo_group').id)
    whatsapp_model_real = fields.Char(string='Recipients Real Model', compute='_compute_model')
    whatsapp_model_name = fields.Char(
        string='Recipients Model Name', related='whatsapp_model_id.model',
        readonly=True, related_sudo=True)
    whatsapp_domain = fields.Char(
        string='Domain', compute='_compute_whatsapp_domain',
        readonly=False, store=True)
    message_type = fields.Selection([('message', 'Message')], string="Message Type", default="message", required=True)
    message_body = fields.Text('Body', required=True)
    body_arch = fields.Html(string='Body', translate=False)
    body_html = fields.Html(string='Body converted to be sent by mail', sanitize_attributes=False)
    user_id = fields.Many2one('res.users', string='Responsible', tracking=True,  default=lambda self: self.env.user)
    attachment_ids = fields.Many2many('ir.attachment', 'whatsapp_marketing_ir_attachments_rel',
                                      'whatsapp_message_id', 'attachment_id', string='Attachments')
    campaign_id = fields.Many2one('utm.campaign', string='UTM Campaign', index=True)
    source_id = fields.Char()
    odoo_group_ids = fields.Many2many('odoo.group', 'whatsapp_marketing_odoo_group_rel', string='Whatsapp Message')
    state = fields.Selection([('draft', 'Draft'), ('in_queue', 'In Queue'),('done', 'Sent')],
                             string='Status', required=True, tracking=True, copy=False, default='draft')
    schedule_date = fields.Datetime(string='Scheduled for', tracking=True)
    next_departure = fields.Datetime(compute="_whatsapp_compute_next_departure", string='Scheduled date')
    sent_date = fields.Datetime(string='Sent Date', copy=False)


    def _whatsapp_compute_next_departure(self):
        cron_next_call = self.env.ref('pragmatic_odoo_whatsapp_marketing.send_whatsapp_msg_marketing').sudo().nextcall
        str2dt = fields.Datetime.from_string
        cron_time = str2dt(cron_next_call)
        for whatsapp_message in self:
            if whatsapp_message.schedule_date:
                schedule_date = str2dt(whatsapp_message.schedule_date)
                whatsapp_message.next_departure = max(schedule_date, cron_time)
            else:
                whatsapp_message.next_departure = cron_time

    @api.depends('whatsapp_model_id')
    def _compute_model(self):
        for record in self:
            record.whatsapp_model_real = record.whatsapp_model_name or 'whatsapp.contact'

    @api.depends('whatsapp_model_name', 'odoo_group_ids')
    def _compute_whatsapp_domain(self):
        for message in self:
            if not message.whatsapp_model_name:
                message.whatsapp_domain = ''
            else:
                message.whatsapp_domain = repr(message._get_default_message_domain())

    def _get_default_message_domain(self):
        message_domain = []
        return message_domain

    def _get_remaining_recipients(self):
        res_ids = self._get_recipients()
        return res_ids

    def _get_recipients(self):
        message_domain = self._parse_message_domain()
        res_ids = self.env[self.whatsapp_model_real].search(message_domain).ids
        return res_ids

    def _parse_message_domain(self):
        self.ensure_one()
        try:
            message_domain = literal_eval(self.whatsapp_domain)
        except Exception:
            message_domain = [('id', 'in', [])]
        return message_domain

    def action_send_message(self):
        param = self.env['res.config.settings'].sudo().get_values()
        no_phone_partners = []
        for message in self:
            res_ids = message._get_remaining_recipients()
            bodies = self.env['mail.render.mixin']._render_template(self.message_body, message.whatsapp_model_real,
                                                                    res_ids,
                                                                    post_process=True)
            for res_id in res_ids:
                rec = self.env[message.whatsapp_model_real].browse(res_id)
                if message.whatsapp_model_real == 'res.partner':
                    if rec.country_id.phone_code and rec.mobile:
                        whatsapp_number = rec.mobile
                        whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(rec.country_id.phone_code), "")
                        phone_exists_url = param.get('whatsapp_endpoint') + '/checkPhone?token=' + param.get('whatsapp_token') + '&phone=' + str(
                            rec.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                        phone_exists_response = requests.get(phone_exists_url)
                        json_response_phone_exists = json.loads(phone_exists_response.text)
                        if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and \
                                json_response_phone_exists['result'] == 'exists':
                            url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                            headers = {"Content-Type": "application/json"}
                            for key, value in bodies.items():
                                if res_id == key:
                                    tmp_dict = {
                                        "phone": "+" + str(rec.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                        "body": str(value)
                                    }
                                    response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                                    if response.status_code == 201 or response.status_code == 200:
                                        _logger.info("\nSend Message successfully")
                                        self.write({'state': 'done'})
                            if self.attachment_ids:
                                for attachment in self.attachment_ids:
                                    with open("/tmp/" + attachment.name, 'wb') as tmp:
                                        encoded_file = str(attachment.datas)
                                        url_send_file = param.get('whatsapp_endpoint') + '/sendFile?token=' + param.get('whatsapp_token')
                                        headers_send_file = {"Content-Type": "application/json"}
                                        dict_send_file = {
                                            "phone": "+" + str(rec.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                            "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                            "filename": attachment.name
                                        }
                                        response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                                        if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                            _logger.info("\nSend file attachment successfully11")
                        else:
                            no_phone_partners.append(rec.name)
                    else:
                        raise UserError(_('Please enter %s mobile number or select country', rec.name))
                    if len(no_phone_partners) >= 1:
                        raise UserError(_('Please add valid whatsapp number for %s customer')% ', '.join(no_phone_partners))

                elif message.whatsapp_model_real == 'sale.order' or message.whatsapp_model_real == 'crm.lead':
                    if rec.partner_id.country_id.phone_code and rec.partner_id.mobile:
                        whatsapp_number = rec.partner_id.mobile
                        whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                            '+' + str(rec.partner_id.country_id.phone_code), "")
                        phone_exists_url = param.get('whatsapp_endpoint') + '/checkPhone?token=' + param.get('whatsapp_token') + '&phone=' + str(
                            rec.partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                        phone_exists_response = requests.get(phone_exists_url)
                        json_response_phone_exists = json.loads(phone_exists_response.text)
                        if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and \
                                json_response_phone_exists['result'] == 'exists':
                            url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                            headers = {"Content-Type": "application/json"}
                            for key, value in bodies.items():
                                if res_id == key:
                                    tmp_dict = {
                                        "phone": "+" + str(rec.partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                        "body": str(value)}
                                    response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                                    if response.status_code == 201 or response.status_code == 200:
                                        _logger.info("\nSend Message successfully")
                                        self.write({'state': 'done'})
                            if self.attachment_ids:
                                for attachment in self.attachment_ids:
                                    with open("/tmp/" + attachment.name, 'wb') as tmp:
                                        encoded_file = str(attachment.datas)
                                        url_send_file = param.get('whatsapp_endpoint') + '/sendFile?token=' + param.get('whatsapp_token')
                                        headers_send_file = {"Content-Type": "application/json"}
                                        dict_send_file = {
                                            "phone": "+" + str(rec.partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                            "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                            "filename": attachment.name
                                        }
                                        response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                                        if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                            _logger.info("\nSend file attachment successfully11")
                        else:
                            no_phone_partners.append(rec.partner_id.name)
                    else:
                        raise UserError(_('Please enter %s mobile number or select country', rec.partner_id.name))
                    if len(no_phone_partners) >= 1:
                        raise UserError(
                            _('Please add valid whatsapp number for %s customer') % ', '.join(no_phone_partners))

                elif message.whatsapp_model_real == 'odoo.group':
                    for res_partner_id in rec.partner_ids:
                        if rec.whatsapp_contact_id:
                            for contact_id in rec.whatsapp_contact_id:
                                if contact_id.sanitized_mobile != res_partner_id.mobile:
                                    whatsapp_number = res_partner_id.mobile
                                    whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                                    whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                                        '+' + str(res_partner_id.country_id.phone_code), "")
                                    phone_exists_url = param.get('whatsapp_endpoint') + '/checkPhone?token=' + param.get(
                                        'whatsapp_token') + '&phone=' + str(
                                        res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                                    phone_exists_response = requests.get(phone_exists_url)
                                    json_response_phone_exists = json.loads(phone_exists_response.text)
                                    url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                                    headers = {"Content-Type": "application/json"}
                                    for key, value in bodies.items():
                                        if res_id == key:
                                            tmp_dict = {
                                                "phone": "+" + str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                                "body": str(value)}
                                            response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                                            if response.status_code == 201 or response.status_code == 200:
                                                _logger.info("\nSend Message successfully")
                                                self.write({'state': 'done'})

                                    if self.attachment_ids:
                                        for attachment in self.attachment_ids:
                                            with open("/tmp/" + attachment.name, 'wb') as tmp:
                                                encoded_file = str(attachment.datas)
                                                url_send_file = param.get('whatsapp_endpoint') + '/sendFile?token=' + param.get('whatsapp_token')
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
                            headers = {"Content-Type": "application/json" }
                            for key, value in bodies.items():
                                if res_id == key:
                                    tmp_dict = {
                                        "phone": "+" + str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                        "body": str(value)}
                                    response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                                    if response.status_code == 201 or response.status_code == 200:
                                        _logger.info("\nSend Message successfully")
                                        self.write({'state': 'done'})

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
                        for key, value in bodies.items():
                            if res_id == key:
                                tmp_dict = {"chatId": str(contact_id.whatsapp_id), "body": str(value)}
                                response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                                if response.status_code == 201 or response.status_code == 200:
                                    _logger.info("\nSend Message successfully")
                                    self.write({'state': 'done'})
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

                elif message.whatsapp_model_real == 'whatsapp.group':
                    url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                    headers = {"Content-Type": "application/json"}
                    for key, value in bodies.items():
                        if res_id == key:
                            tmp_dict = {"chatId": str(rec.group_id),"body": str(value)}
                            response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                            if response.status_code == 201 or response.status_code == 200:
                                msg_dict = {
                                    'message_body': str(value),
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
                                _logger.info("\nSend Message successfully")
                                self.write({'state': 'done'})
                    if self.attachment_ids:
                        for attachment in self.attachment_ids:
                            with open("/tmp/" + attachment.name, 'wb') as tmp:
                                encoded_file = str(attachment.datas)
                                url_send_file = param.get('whatsapp_endpoint') + '/sendFile?token=' + param.get('whatsapp_token')
                                headers_send_file = {"Content-Type": "application/json"}
                                dict_send_file = {
                                    "chatId": "+" + str(rec.group_id),
                                    "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                    "filename": attachment.name
                                }
                                response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                                if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                    _logger.info("\nSend file attachment successfully11")

                elif message.whatsapp_model_real == 'whatsapp.contact':
                    url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                    headers = {"Content-Type": "application/json"}
                    for key, value in bodies.items():
                        if res_id == key:
                            tmp_dict = {"phone": str(rec.mobile), "body": str(value)}
                            response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                            if response.status_code == 201 or response.status_code == 200:
                                msg_dict = {
                                    'message_body': str(value),
                                    'fromMe': True,
                                    'chatId': rec.whatsapp_id,
                                    'type': 'chat',
                                    'senderName': self.env.user.partner_id.name,
                                    'chatName': rec.name,
                                    'time': datetime.datetime.now(),
                                    'whatsapp_contact_id': rec.id,
                                    'state': 'sent',
                                }
                                _logger.info("\nSend Message successfully")
                                self.write({'state': 'done'})
                    if self.attachment_ids:
                        for attachment in self.attachment_ids:
                            with open("/tmp/" + attachment.name, 'wb') as tmp:
                                encoded_file = str(attachment.datas)
                                url_send_file = param.get('whatsapp_endpoint') + '/sendFile?token=' + param.get('whatsapp_token')
                                headers_send_file = {"Content-Type": "application/json"}
                                dict_send_file = {
                                    "phone": str(rec.mobile),
                                    "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                    "filename": attachment.name
                                }
                                response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                                if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                    _logger.info("\nSend file attachment successfully11")

    def action_schedule(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("pragmatic_odoo_whatsapp_marketing.whatsapp_message_schedule_date_action")
        action['context'] = dict(self.env.context, default_odoo_group_id=self.id)
        return action

    def action_cancel(self):
        self.write({'state': 'draft', 'schedule_date': False})


    def _send_schedule_messages(self):
        mass_messages = self.search(
            [('state', '=', ('in_queue')), '|', ('schedule_date', '<', fields.Datetime.now()),
             ('schedule_date', '=', False)])
        for mass_message in mass_messages:
            user = mass_message.write_uid or self.env.user
            mass_message = mass_message.with_context(**user.with_user(user).context_get())
            if len(mass_message._get_remaining_recipients()) > 0:
                mass_message.action_send_message()
            else:
                mass_message.write({
                    'state': 'done',
                    'sent_date': fields.Datetime.now(),
                })

        messages = self.env['whatsapp.marketing'].search([
            ('state', '=', 'done'),
            ('sent_date', '<=', fields.Datetime.now() - relativedelta(days=1)),
            ('sent_date', '>=', fields.Datetime.now() - relativedelta(days=5)),
        ])
        if messages:
            messages.action_send_message()
