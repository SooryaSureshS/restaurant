import json
import requests
import logging

from odoo import fields, models, _, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    iface_whatsapp_receipt = fields.Boolean(string="Whatsapp Receipt",
                                            help="Allow to send POS Receipt to customer's Whatsapp")
    iface_whatsapp_receipt_auto = fields.Boolean(string="Whatsapp Receipt Automatically",
                                                 help="Allow to send POS Receipt to customer's Whatsapp automatically")
    iface_whatsapp_msg = fields.Boolean(string="Whatsapp message",
                                        help="Allow to send Whatsapp message to specific customer")
    iface_whatsapp_grp_msg = fields.Boolean(string="Send message",
                                            help="Allow to send messages")
    iface_whatsapp_msg_template = fields.Boolean(string="Whatsapp message template",
                                                 help="Allow to set Whatsapp default message template")
    whatsapp_msg_template_id = fields.Many2one("whatsapp.message.template", string="Message Template",
                                               help="Set default whatsapp message template")

    @api.model
    def parse_mobile_no(self, mobile_no):
        """
        Convert mobile no. to chat api phone no format.
        :param mobile_no: customer mobile no.
        :return:
        """
        return mobile_no.replace(" ", "").replace("+", "")

    @api.model
    def _get_whatsapp_endpoint(self, method):
        param = self.env['res.config.settings'].sudo().get_values()
        endpoint = param.get('whatsapp_endpoint')
        token = param.get('whatsapp_token')
        url = ''
        if all([endpoint, token]):
            url = f"{endpoint}/{method}?token={token}"
        else:
            ValidationError(_(f'Missing Whatsapp credentials, \ncontact to your Administrator.'))
        return url

    @api.model
    def get_whatsapp_chatlist(self, *args, **kwargs):
        url = self._get_whatsapp_endpoint("dialogs")
        response = {}
        if not url:
            response["error"] = {
                "code": 400,
                "message": "Missing Whatsapp configuration, contact to your Adminstrator"
            }
            return json.dumps(response)
        headers = {
            "Content-Type": "application/json",
        }
        try:
            req = requests.get(url, headers=headers)
            result = req.json()
            if req.status_code == 201 or req.status_code == 200:
                response["code"] = req.status_code
                response["chatList"] = list(map(lambda dialog: {"id": dialog["id"], "name": dialog["name"],
                                                                "image": dialog["image"] or "/pragmatic_odoo_pos_whatsapp_integration/static/src/img/empty-profile.png"}, result["dialogs"]))
            else:
                if 'error' in result:
                    message = response['error']
                    _logger.error(f"Failed Whatsapp API call => Reason: {req.reason}, Message:{message}")
                    response["error"] = {
                        "code": req.status_code,
                        "message": message
                    }
        except Exception as e:
            _logger.error(e)
            response["error"] = {
                "code": 500,
                "message": e
            }
        return response

    @api.model
    def action_send_whatsapp_group_msg(self, template_id, message, chat_ids, *args, **kwargs):
        for chat_id in chat_ids:
            self.action_send_whatsapp_msg(template_id, message, chat_id, is_bulk=True)

    @api.model
    def action_send_whatsapp_msg(self, template_id, message, mobile_no, is_bulk=False, *args, **kwargs):
        url = self._get_whatsapp_endpoint('sendMessage')
        if not url:
            return json.dumps("Missing Whatsapp configuration, contact to your Adminstrator")
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "phone": self.parse_mobile_no(mobile_no),
            "body": message
        }
        if is_bulk:

            payload["chatId"] = mobile_no
        else:
            payload["phone"] = self.parse_mobile_no(mobile_no)
        try:
            req = requests.post(url, data=json.dumps(payload), headers=headers)
            response = req.json()
            if req.status_code == 201 or req.status_code == 200:
                _logger.info(f"\n11Whatsapp Message successfully send to {mobile_no}")
            else:
                if 'error' in response:
                    message = response['error']
                    _logger.error(f"Reason: {req.reason}, Message:{message}")
        except Exception as e:
            _logger.error(e)

    @api.model
    def action_send_whatsapp_receipt(self, order_id, ticket_img, mobile_no, country_id, *args, **kwargs):
        url = self._get_whatsapp_endpoint('sendFile')
        url_checkphone = self._get_whatsapp_endpoint('checkPhone')
        url_checkphone += "&phone=" + str(self.parse_mobile_no(mobile_no))

        if not url or not url_checkphone:
            return json.dumps("Missing Whatsapp configuration, contact to your Adminstrator")
        try:
            req_check_phone = requests.get(url_checkphone)
            response_phone_exists = json.loads(req_check_phone.text)
            if (req_check_phone.status_code == 200 or req_check_phone.status_code == 201) and response_phone_exists.get('result') == 'exists':
                headers = {"Content-Type": "application/json"}
                country_id = self.env['res.country'].search([('id', '=', country_id)])
                payload = {
                    "phone": self.parse_mobile_no(mobile_no),
                    "body": f"data:image/jpeg;base64,{ticket_img}",
                    "filename": "receipt.jpeg"
                }
                try:
                    req = requests.post(url, data=json.dumps(payload), headers=headers)
                    response = req.json()
                    if req.status_code == 201 or req.status_code == 200:
                        _logger.info(f"\n22Whatsapp Message successfully send to {mobile_no}")
                        return 'Whatsapp Message send successfully'
                    else:
                        if 'error' in response:
                            message = response['error']
                            _logger.error(f"Reason: {req.reason}, Message:{message}")
                            return message
                        return False
                except Exception as e:
                    _logger.error(e)
            elif response_phone_exists.get('result') == 'not exists':
                return "Phone not exists on whatsapp"
            else:
                return response_phone_exists.get('error')
        except Exception as e:
            _logger.error(e)