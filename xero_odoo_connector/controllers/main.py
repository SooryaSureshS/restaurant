# -*- coding: utf-8 -*-

import requests
import json
import base64
import werkzeug
from odoo import http
from werkzeug import urls
from odoo.http import request


class XeroAuth_2(http.Controller):

    def getBearerToken(self, CLIENT_ID, CLIENT_SECRET, AUTH_CODE, REDIRECT_URI, ACCESS_TOKEN_URL):
        auth_header = 'Basic ' + base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode()
        headers = {
            'Accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': auth_header,
        }
        payload = {
            'code': AUTH_CODE,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code',
        }
        r = requests.post(ACCESS_TOKEN_URL, data=payload, headers=headers)
        if r.status_code != 200:
            return r.text
        bearer_raw = json.loads(r.text)

        if 'id_token' in bearer_raw:
            idToken = bearer_raw['id_token']
        else:
            idToken = None

        return {
            'access_token': bearer_raw['access_token'],
            'token_type': bearer_raw['token_type'],
            'refresh_token': bearer_raw['refresh_token'],
            'expires_in': bearer_raw['expires_in'],
            'idToken': idToken,
            'status_code': r.status_code,
        }

    @http.route('/xero/callback', auth='public', type='http')
    def xero_callback(self, **kwargs):
        if kwargs.get('state') and kwargs.get('code'):
            xero = request.env['xero.xero'].sudo().browse(int(kwargs['state']))
            token_info = self.getBearerToken(xero.clientkey, xero.clientsecret, kwargs['code'], xero.redirect_url, xero.access_token_url)

            if isinstance(token_info, dict):
                if token_info.get('status_code') == 200:
                    xero.access_token = token_info.get('access_token')
                    xero.refresh_access_token = token_info.get('refresh_token')

                    headers = {
                        'authorization': "Bearer %s" % token_info.get('access_token'),
                        'content-type': "application/json",
                    }

                    response = requests.request("GET", 'https://api.xero.com/connections', headers=headers)
                    if response.status_code == 200:
                        res = json.loads(response.text)
                        xero.xero_referral_id = res[0].get('tenantId')

                    base_url = request.env['ir.config_parameter'].get_param('web.base.url')
                    end_point = urls.url_encode({
                        'id': str(kwargs['state']), 
                        'model': 'xero.xero',
                        'view_type': 'form'})
                    ConfigUrl = base_url + '/web#' + end_point
                    return werkzeug.utils.redirect(ConfigUrl)
        return werkzeug.utils.redirect('/web')
