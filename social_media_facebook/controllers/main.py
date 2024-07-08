from odoo import http, _
from odoo.http import request
import werkzeug
from werkzeug.urls import url_encode, url_join
from odoo.addons.social_media_base.controllers.main import SocialValidationException
import requests
import base64
import functools


def fragment_to_query_string(func):
    @functools.wraps(func)
    def wrapper(self, *a, **kw):
        kw.pop('debug', False)
        if not kw:
            return """<html><head><script>
                var l = window.location;
                var q = l.hash.substring(1);
                var r = l.pathname + l.search;
                if(q.length !== 0) {
                    var s = l.search ? (l.search === '?' ? '' : '&') : '?';
                    r = l.pathname + l.search + s + q;
                }
                if (r == l.pathname) {
                    r = '/';
                }
                window.location = r;
            </script></head><body></body></html>"""
        return func(self, *a, **kw)

    return wrapper


class OAuthFacebookController(http.Controller):

    @http.route('/facebook/callback', type='http', auth='user')
    @fragment_to_query_string
    def facebook_authentication_callback(self, access_token=None, is_extended_token=False, **kw):
        if kw.get('error') != 'access_denied':
            if not access_token:
                return request.render(
                    'social_media_base.social_media_error_view',
                    {'error_message': _('Facebook did not provide a valid access token.')})
            socialmedia = request.env.ref('social_media_facebook.social_media_facebook')
            try:
                self.create_facebook_accounts(access_token, socialmedia, is_extended_token)
            except SocialValidationException as e:
                return request.render('social_media_base.social_media_error_view', {'error_message': str(e)})

        url_params = {
            'action': request.env.ref('social_media_base.action_social_media_accounts').id,
            'view_type': 'kanban',
            'model': 'social.media.accounts',
        }

        url = '/web?#%s' % url_encode(url_params)
        return werkzeug.utils.redirect(url)

    def create_facebook_accounts(self, access_token, socialmedia, is_extended_token):
        extended_access_token = access_token if is_extended_token else self.get_extended_access_token(access_token)

        account_url = url_join(request.env['social.media.types']._facebook_endpoint, "/me/accounts/")
        response = requests.get(account_url, params={
            'access_token': extended_access_token}).json()
        if 'data' in response:
            account_vals = []
            existing_account = self.get_existing_account(socialmedia, response)
            for account in response['data']:
                account_id = account['id']
                access_token = account['access_token']
                if not existing_account.get(account_id):
                    account_vals.append({
                        'name': account.get('name'),
                        'social_media_id':socialmedia.id,
                        'facebook_account_id':account_id,
                        'facebook_access_token':access_token,
                        'image': self.get_account_image(account_id)
                    })
                else:
                    existing_account.get(account_id).sudo().write({
                        'facebook_access_token': access_token
                    })
        else:
            raise SocialValidationException(_('Facebook did not provide a valid access token.'))
        if account_vals:
            request.env['social.media.accounts'].sudo().create(account_vals)

    def get_existing_account(self, socialmedia, response):
        facebook_accounts_ids = [account['id'] for account in response.get('data', [])]
        if facebook_accounts_ids:
            existing_accounts = request.env['social.media.accounts'].search([
                ('social_media_id', '=', int(socialmedia)),
                ('facebook_account_id', 'in', facebook_accounts_ids)
            ])

            return {existing_account.facebook_account_id: existing_account for existing_account in existing_accounts}
        return {}

    def get_extended_access_token(self, access_token):
        facebook_app_id = request.env['ir.config_parameter'].sudo().get_param('social_media_facebook.facebook_app_id')
        facebook_app_secret = request.env['ir.config_parameter'].sudo().get_param('social_media_facebook.facebook_app_secret')
        extended_token_url = url_join(request.env['social.media.types']._facebook_endpoint, "/oauth/access_token")
        extended_token_request = requests.post(extended_token_url, params={
            'client_id': facebook_app_id,
            'client_secret': facebook_app_secret,
            'grant_type': 'fb_exchange_token',
            'fb_exchange_token': access_token
        })
        return extended_token_request.json().get('access_token')

    def get_account_image(self, account_id):
        image_url = url_join(request.env['social.media.types']._facebook_endpoint,
                                     '/v3.3/%s/picture?height=300' % account_id)
        return base64.b64encode(requests.get(image_url).content)

class OAuthInstagramController(http.Controller):

    @http.route('/instagram/callback', type='http', auth='user')
    @fragment_to_query_string
    def instagram_authentication_callback(self, code, **kw):
        if kw.get('error') != 'access_denied':
            if not code:
                return request.render(
                    'social_media_base.social_media_error_view',
                    {'error_message': _('Instagram did not provide a valid Code.')})
            socialmedia = request.env.ref('social_media_facebook.social_media_instagram')
            try:
                self.create_instagram_accounts(code, socialmedia)
            except SocialValidationException as e:
                return request.render('social_media_base.social_media_error_view', {'error_message': str(e)})

        url_params = {
            'action': request.env.ref('social_media_base.action_social_media_accounts').id,
            'view_type': 'kanban',
            'model': 'social.media.accounts',
        }

        url = '/web?#%s' % url_encode(url_params)
        return werkzeug.utils.redirect(url)

    def create_instagram_accounts(self, code, socialmedia):
        accesstoken = self.exchange_code_for_accesstoken(code)
        account_url = url_join(request.env['social.media.types']._instagram_endpoint, "/me?fields=username")
        response = requests.get(account_url, params={'access_token': accesstoken}).json()
        if 'username' in response:
            account_vals = []
            existing_account = request.env['social.media.accounts'].sudo().search([('instagram_account_id','=',response.get('id'))])
            if not existing_account:
                account_vals.append({
                    'name': response.get('username'),
                    'social_media_id':socialmedia.id,
                    'instagram_account_id':response.get('id'),
                    'instagram_access_token':accesstoken,
                    # 'image': self.get_account_image(account_id)
                })
            else:
                existing_account.sudo().write({
                    'instagram_access_token': accesstoken
            })
        else:
            raise SocialValidationException(_('Instagram did not provide a valid access token.'))
        if account_vals:
            request.env['social.media.accounts'].sudo().create(account_vals)


    def exchange_code_for_accesstoken(self, code):
        instagram_app_id = request.env['ir.config_parameter'].sudo().get_param('social_media_facebook.instagram_app_id')
        instagram_app_secret = request.env['ir.config_parameter'].sudo().get_param('social_media_facebook.instagram_app_secret')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        in_values = {'client_id':instagram_app_id,
                     'client_secret':instagram_app_secret,
                     'grant_type':'authorization_code',
                     # 'redirect_uri': "https://f081-2405-201-f012-f02b-2856-e93c-a469-8b21.ngrok.io/instagram/callback",
                     'redirect_uri':url_join(base_url, "instagram/callback"),
                     'code':code }
        access_token_request = requests.post("https://api.instagram.com/oauth/access_token?", data = in_values).json()
        longlived_accesstoken = self.get_long_lived_accesstoke(instagram_app_secret, access_token_request.get('access_token'))
        return longlived_accesstoken

    def get_long_lived_accesstoke(self, instagram_app_secret, access_token):
        accesstoken_url = 'https://graph.instagram.com/access_token'
        response = requests.get(accesstoken_url, params={'grant_type':'ig_exchange_token', 'client_secret': instagram_app_secret, 'access_token': access_token})
        if response.status_code == 200:
            return response.json().get('access_token')
        return access_token
