from odoo import fields,models,api,_,tools
import pytz
import requests
import json
import re
import logging
_logger = logging.getLogger(__name__)
from twilio.rest import Client


class OrganizeOrganize(models.Model):

    _inherit = 'organize.organize'

    def _send_organize(self, message=None, employees=False):
        Param = self.env['res.config.settings'].sudo().get_values()
        email_from = self.env.user.email or self.env.user.company_id.email or ''
        sent_slots = self.env['organize.slot']
        for organize in self:
            slots = organize.slot_ids
            slots_open = slots.filtered(lambda line: not line.employee_id) if organize.include_unassigned else 0
            employees = employees or slots.mapped('employee_id')
            employee_url_map = employees.sudo()._organize_get_url(organize)
            template = self.env.ref('organize.email_template_organize_organize', raise_if_not_found=False)
            template_context = {
                'slot_unassigned_count': slots_open and len(slots_open),
                'slot_total_count': slots and len(slots),
                'message': message,
            }
            if template:
                is_email = self.env['ir.config_parameter'].sudo().get_param('schedule_notificaction.is_mail_send_msg')
                is_whatsapp = self.env['ir.config_parameter'].sudo().get_param('schedule_notificaction.is_whatsapp_send_msg')
                is_sms = self.env['ir.config_parameter'].sudo().get_param('schedule_notificaction.is_sms_send_msg')
                for employee in self.env['hr.employee.public'].browse(employees.ids):
                    if employee.work_email and is_email:
                        template_context['employee'] = employee
                        destination_tz = pytz.timezone(self.env.user.tz or 'UTC')
                        template_context['start_datetime'] = pytz.utc.localize(organize.start_datetime).astimezone(
                            destination_tz).replace(tzinfo=None)
                        template_context['end_datetime'] = pytz.utc.localize(organize.end_datetime).astimezone(
                            destination_tz).replace(tzinfo=None)
                        template_context['organize_url'] = employee_url_map[employee.id]
                        template_context['assigned_new_shift'] = bool(
                            slots.filtered(lambda line: line.employee_id.id == employee.id))
                        template.with_context(**template_context).send_mail(organize.id, email_values={
                            'email_to': employee.work_email, 'email_from': email_from},
                                                                            notif_layout='mail.mail_notification_light')
                for employee_id in employees:
                    if is_whatsapp:
                        print("\n ______-is_whatsapp_______\n")
                        msg = ''
                        msg_number = employee_id.mobile_phone if employee_id.mobile_phone else employee_id.phone
                        if msg_number and employee_id.country_id:
                            whatsapp_msg_number_without_space = msg_number.replace(" ", "")
                            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(employee_id.country_id.phone_code), "")
                            phone_exists_url = Param.get('whatsapp_endpoint') + '/checkPhone?token=' + Param.get(
                                'whatsapp_token') + '&phone=' + str(
                                employee_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                            phone_exists_response = requests.get(phone_exists_url)
                            json_response_phone_exists = json.loads(phone_exists_response.text)
                            if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) \
                                    and json_response_phone_exists['result'] == 'exists':
                                msg = _('Hello') + ' ' + employee_id.name
                                url = Param.get('whatsapp_endpoint') + '/sendMessage?token=' + Param.get('whatsapp_token')
                                headers = {"Content-Type": "application/json"}
                                tmp_dict = {"phone": "+" + str(employee_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code, "body": msg}
                                response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                                if response.status_code == 201 or response.status_code == 200:
                                    _logger.info("\nSend Message successfully")
                                    mail_message_obj = self.env['mail.message']
                                    if self.env['ir.config_parameter'].sudo().get_param(
                                            'pragmatic_odoo_whatsapp_integration.group_crm_display_chatter_message'):
                                        comment = "fa fa-whatsapp"
                                        body_html = tools.append_content_to_html(
                                            '<div class = "%s"></div>' % tools.ustr(comment), msg)
                                        body_msg = self.convert_to_html(body_html)
                                        mail_message_id = mail_message_obj.sudo().create({
                                            'res_id': self.id,
                                            'model': 'crm.lead',
                                            'body': body_msg,
                                        })
                    if is_sms:
                        print("\n __________is_sms_________\n")
                        param_obj = self.env['ir.config_parameter']
                        twilio_account_sid = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_account_sid')
                        twilio_auth_token = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_auth_token')
                        twilio_from_number = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_from_number')

                        client = Client(twilio_account_sid, twilio_auth_token)
                        message_body = "Hello " + str(employee_id.name)
                        msg_number = employee_id.mobile_phone if employee_id.mobile_phone else employee_id.phone
                        if msg_number:
                            try:
                                response = client.messages.create(body=message_body, from_=twilio_from_number, to=msg_number)
                                if response.error_message:
                                    state = 'error'
                                    error_message = response.error_message
                                else:
                                    state = 'sent'
                                    error_message = None
                            except Exception as e:
                                state = 'error'
                                error_message = e.msg or e.__str__()

            sent_slots |= slots
        sent_slots.write({
            'is_published': True,
            'publication_warning': False
        })
        return True