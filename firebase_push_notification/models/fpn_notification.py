import requests

from odoo import models, fields, _
import logging
_logger = logging.getLogger(__name__)
class FpnNotificationToken(models.Model):
    _inherit = 'res.users'

    firebase_token = fields.Char(string='Firebase Token')
    enable_token = fields.Boolean(string='Enable Token', default=False)

class FpnNotification(models.Model):
    _name = 'fpn.notification'
    _inherit = 'mail.thread'

    name = fields.Char()
    message = fields.Text()
    title = fields.Text()
    link = fields.Char()

    state = fields.Selection(
        [('draft', 'Draft'), ('sent', 'Sent'), ('failed', 'Failed'), ('cancelled', 'Cancelled')],default='draft'
    )
    cast_user = fields.Many2many('res.users', domain=[('firebase_token', '!=', False)])

    def send_notification(self):
        import requests
        import json

        serverToken = 'AAAASvKsKqw:APA91bGmRO2aTcWb1f_CP4fvQQVor9tqCa3VHJ6XuZ3BfnHa9IWQvyWN5YmuNO9AImEhHgJvRCpftrz1NK7f77Y9TaMI2e21Lmrav-1jbA-8CqxiDwUsVvI4mfU3yh7suRbuREfCdO7T'
        deviceToken = 'eTaLWTO3KORZLfauXk4YQO:APA91bHrmb8za5qh7Bb9S73TVFO4bq1w0RiA5LB-Ar2FjTMzNzcp0i4nBpXo6zVAZswGUL2HRbvvpWjesDlIkLOqPSGiDa9ug5TTvPQ_z93kUElmn7oMrlWv7go9uWT_wJDsZFD6tVF0'
        serverToken = self.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.serverToken')

        for cast in self.cast_user:
            if cast.enable_token:
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'key=' + serverToken,
                }

                body = {
                    'notification': {
                                        "body": self.message,
                                        "title": self.title,
                                        "icon": "/firebase_push_notification/static/image/icon.png",
                                        "click_action": self.link
                                     },
                    'to':
                        cast.firebase_token,
                    'priority': 'high',
                    #   'data': dataPayLoad,
                }
                _logger.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s', headers)

                _logger.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s', body)
                response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
                _logger.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s', response)
                print(response.status_code)
                if response.status_code == 200:
                    self.write({
                        'state': 'sent'
                    })
                    self.message_post(body=_('Status Changed to %s' % self.state))
                print(response.json())

    def send_notification_all(self):
        import requests
        import json

        serverToken = 'AAAASvKsKqw:APA91bGmRO2aTcWb1f_CP4fvQQVor9tqCa3VHJ6XuZ3BfnHa9IWQvyWN5YmuNO9AImEhHgJvRCpftrz1NK7f77Y9TaMI2e21Lmrav-1jbA-8CqxiDwUsVvI4mfU3yh7suRbuREfCdO7T'
        deviceToken = 'eTaLWTO3KORZLfauXk4YQO:APA91bHrmb8za5qh7Bb9S73TVFO4bq1w0RiA5LB-Ar2FjTMzNzcp0i4nBpXo6zVAZswGUL2HRbvvpWjesDlIkLOqPSGiDa9ug5TTvPQ_z93kUElmn7oMrlWv7go9uWT_wJDsZFD6tVF0'
        serverToken = self.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.serverToken')
        users = self.env['res.users'].sudo().search([('firebase_token','!=', False)])

        for cast in users:
            if cast.enable_token:
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'key=' + serverToken,
                }

                body = {
                    'notification': {
                                        "body": self.message,
                                        "title": self.title,
                                        "icon": "/firebase_push_notification/static/image/icon.png",
                                        "click_action": self.link
                                     },
                    'to':
                        cast.firebase_token,
                    'priority': 'high',
                    #   'data': dataPayLoad,
                }
                response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
                print(response.status_code)
                if response.status_code == 200:
                    self.write({
                        'state': 'sent'
                    })
                    self.message_post(body=_('Status Changed to %s' % self.state))
                print(response.json())
