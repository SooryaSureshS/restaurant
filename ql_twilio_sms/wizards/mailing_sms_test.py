from odoo import models, exceptions, _
from odoo.addons.phone_validation.tools import phone_validation
from twilio.rest import Client


class MassSMSTest(models.TransientModel):
    _inherit = 'mailing.sms.test'

    def action_send_sms(self):
        self.ensure_one()
        numbers = [number.strip() for number in self.numbers.split(',')]
        sanitize_res = phone_validation.phone_sanitize_numbers_w_record(numbers, self.env.user)
        sanitized_numbers = [info['sanitized'] for info in sanitize_res.values() if info['sanitized']]
        invalid_numbers = [number for number, info in sanitize_res.items() if info['code']]
        if invalid_numbers:
            raise exceptions.UserError(
                _('Following numbers are not correctly encoded: %s, example : "+32 495 85 85 77, +33 545 55 55 55"',
                  repr(invalid_numbers)))

        record = self.env[self.mailing_id.mailing_model_real].search([], limit=1)
        body = self.mailing_id.body_plaintext
        if record:
            # Returns a proper error if there is a syntax error with jinja
            body = self.env['mail.render.mixin']._render_template(body, self.mailing_id.mailing_model_real, record.ids)[
                record.id]
        is_message_overwrite = self.env['ir.config_parameter'].sudo().get_param(
            'ql_scheduler_reminder.twilio_overrwrite_odoo_sms')
        if not is_message_overwrite:
            self.env['sms.api']._send_sms_batch([{
                'res_id': 0,
                'number': number,
                'content': body,
            } for number in sanitized_numbers])
        else:
            print("shek almost................")
            self.twilio_send_sms(sanitized_numbers, body)
        return True

    def twilio_send_sms(self, sanitized_numbers, body):
        param_obj = self.env['ir.config_parameter']
        twilio_account_sid = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_account_sid')
        twilio_auth_token = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_auth_token')
        twilio_from_number = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_from_number')
        client = Client(twilio_account_sid, twilio_auth_token)
        sanitized_numbers = set(sanitized_numbers)
        for number in sanitized_numbers:
            try:
                response = client.messages.create(body=body, from_=twilio_from_number, to=number)
                if response.error_message:
                    state = 'error'
                    error_message = response.error_message
                else:
                    state = 'sent'
                    error_message = None
            except Exception as e:
                state = 'error'
                error_message = e.msg or e.__str__()
