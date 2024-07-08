from odoo import models, fields
from twilio.rest import Client
import threading
from functools import reduce
import operator
from odoo import models, fields, api, _


class TwilioSMS(models.Model):
    _inherit = 'sms.sms'

    error_message = fields.Text('Error Message', copy=False, readonly=1)

    def send(self, delete_all=False, auto_commit=False, raise_exception=False):
        """ Main API method to send SMS.

          :param delete_all: delete all SMS (sent or not); otherwise delete only
            sent SMS;
          :param auto_commit: commit after each batch of SMS;
          :param raise_exception: raise if there is an issue contacting IAP;
        """
        is_message_overwrite = self.env['ir.config_parameter'].sudo().get_param(
            'ql_scheduler_reminder.twilio_overrwrite_odoo_sms')
        for batch_ids in self._split_batch():
            if not is_message_overwrite:
                self.browse(batch_ids)._send(delete_all=delete_all, raise_exception=raise_exception)
            else:
                self.browse(batch_ids).twilio_send_sms()
            # auto-commit if asked except in testing mode

            if auto_commit is True and not getattr(threading.currentThread(), 'testing', False):
                self._cr.commit()

    def twilio_send_sms(self, delete_all=False, raise_exception=False):
        # todo: fix send sms option
        param_obj = self.env['ir.config_parameter']
        twilio_account_sid = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_account_sid')
        twilio_auth_token = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_auth_token')
        twilio_from_number = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_from_number')

        client = Client(twilio_account_sid, twilio_auth_token)
        sent_numbers = []
        for rec_id in self:
            phone = rec_id.number
            if phone:
                phone = phone.replace(" ", "")
                if len(phone) == 12:
                    pass
                elif len(phone) == 10:
                    phone = "+61" + phone[1:]
                else:
                    phone = False
            if phone not in sent_numbers:
                sent_numbers.append(phone)
                try:
                    response = client.messages.create(body=rec_id.body, from_=twilio_from_number, to=phone)
                    if response.error_message:
                        state = 'error'
                        error_message = response.error_message
                    else:
                        state = 'sent'
                        error_message = None
                except Exception as e:
                    state = 'error'
                    error_message = e.msg or e.__str__()
                rec_id.write({'error_message': error_message, 'state': state})


class SmsSms(models.Model):

    _inherit = 'wk.sms.sms'

    @api.onchange('group_ids')
    def add_group_member_number(self):
        phone_lists = [self._get_partner_mobile_numbers(
            group) for group in self.group_ids if self.group_ids]
        combined_list = reduce(
            operator.add, phone_lists) if phone_lists else []
        if combined_list:
            blocked_list = self.env['phone.blacklist'].sudo().browse('number')
            for i in combined_list:
                if i in blocked_list:
                    combined_list.pop(i)
        self.to = self.get_mobile_number(list(set(combined_list)))
