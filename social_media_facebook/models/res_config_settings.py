from odoo import models, fields, api, _
import requests
from odoo.exceptions import ValidationError
import base64
from werkzeug.urls import url_encode, url_join
from odoo.http import request


class ResConfigInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    use_facebook = fields.Boolean(string='Use Facebook Account')
    facebook_app_id = fields.Char(string='Facebook App Id')
    facebook_app_secret = fields.Char(string='Facebook App Secret')
    facebook_token_manually = fields.Boolean(string="Enter Token Manually")
    facebook_user_access_token = fields.Char(string='Facebook User Access Token')
    use_instagram = fields.Boolean(string='Use instagram Account')
    instagram_app_id = fields.Char(string='instagram App Id')
    instagram_app_secret = fields.Char(string='instagram App Secret')
    instagram_token_manually = fields.Boolean(string="Enter Token Manually")
    instagram_user_access_token = fields.Char(string='instagram User Access Token')

    def get_values(self):
        res = super(ResConfigInherit, self).get_values()
        config_para = self.env['ir.config_parameter'].sudo()
        res.update(use_facebook=config_para.get_param('social_media_facebook.use_facebook'),
                   facebook_app_id=config_para.get_param('social_media_facebook.facebook_app_id'),
                   facebook_app_secret=config_para.get_param('social_media_facebook.facebook_app_secret'),
                   facebook_token_manually=config_para.get_param('social_media_facebook.facebook_token_manually'),
                   facebook_user_access_token=config_para.get_param('social_media_facebook.facebook_user_access_token'),
                   use_instagram=config_para.get_param('social_media_facebook.use_instagram'),
                   instagram_app_id=config_para.get_param('social_media_facebook.instagram_app_id'),
                   instagram_app_secret=config_para.get_param('social_media_facebook.instagram_app_secret'),
                   instagram_token_manually=config_para.get_param('social_media_facebook.instagram_token_manually'),
                   instagram_user_access_token=config_para.get_param('social_media_facebook.instagram_user_access_token')
                   )
        return res

    def set_values(self):
        super(ResConfigInherit, self).set_values()
        para = self.env['ir.config_parameter'].sudo()
        para.set_param('social_media_facebook.use_facebook',self.use_facebook)
        para.set_param('social_media_facebook.facebook_app_id', self.facebook_app_id)
        para.set_param('social_media_facebook.facebook_app_secret', self.facebook_app_secret)
        para.set_param('social_media_facebook.facebook_token_manually',self.facebook_token_manually)
        para.set_param('social_media_facebook.facebook_user_access_token', self.facebook_user_access_token)
        para.set_param('social_media_facebook.use_instagram', self.use_instagram)
        para.set_param('social_media_facebook.instagram_app_id', self.instagram_app_id)
        para.set_param('social_media_facebook.instagram_app_secret', self.instagram_app_secret)
        para.set_param('social_media_facebook.instagram_token_manually', self.instagram_token_manually)
        para.set_param('social_media_facebook.instagram_user_access_token', self.instagram_user_access_token)

    def action_get_facebook_accounts(self):
        self.get_values()
        self.set_values()
        if not self.facebook_user_access_token:
            raise ValidationError(_('Please Provide Facebook Accesstoken'))
        else:
            response = requests.get(self.env['social.media.types']._facebook_endpoint+"/v7.0/me/accounts",
                                    params={'access_token': self.facebook_user_access_token}).json()
            socialmedia = self.env.ref('social_media_facebook.social_media_facebook')
            if response.get('error'):
                raise ValidationError(response['error']['message'])
            if not response.get('data'):
                return
            account_vals = []
            for account in response['data']:
                if not self.env['social.media.accounts'].search([('facebook_account_id', '=', account.get('id'))]):
                    account_vals.append({
                            'name': account.get('name'),
                            'social_media_id': socialmedia.id,
                            'facebook_account_id': account.get('id'),
                            'facebook_access_token': self.get_extended_access_token(account.get('access_token')),
                            'image': self.get_account_image(account.get('id'))
                        })
            if account_vals:
                self.env['social.media.accounts'].sudo().create(account_vals)
            action = self.env.ref('social_media_base.action_social_media_accounts').read()[0]
            return action

    def get_account_image(self, account_id):
        image_url = url_join(self.env['social.media.types']._facebook_endpoint,
                                     '/v3.3/%s/picture?height=300' % account_id)
        return base64.b64encode(requests.get(image_url).content)

    def get_extended_access_token(self, access_token):
        facebook_app_id = self.env['ir.config_parameter'].sudo().get_param('social_media_facebook.facebook_app_id')
        facebook_app_secret = self.env['ir.config_parameter'].sudo().get_param(
            'social_media_facebook.facebook_app_secret')
        extended_token_url = url_join(request.env['social.media.types']._facebook_endpoint, "/oauth/access_token")
        extended_token_request = requests.post(extended_token_url, params={
            'client_id': facebook_app_id,
            'client_secret': facebook_app_secret,
            'grant_type': 'fb_exchange_token',
            'fb_exchange_token': access_token
        })
        return extended_token_request.json().get('access_token')
