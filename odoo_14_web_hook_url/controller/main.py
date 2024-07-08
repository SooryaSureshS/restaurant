# -*- coding: utf-8 -*-

from odoo import http, _


class WebhookURL(http.Controller):

    @http.route(['/wooshfood/webhook/url'], type='http', auth="public", website=True, methods=['POST'], csrf=False)
    def WooshWebhook(self, **kw):
        print("Hello! Here is the Webhook URL")
        return True
