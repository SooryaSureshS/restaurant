from odoo import models, fields, api, _
from werkzeug.urls import url_encode, url_join
from odoo.exceptions import UserError, ValidationError


class SocialMediaFacebook(models.Model):
    _inherit = 'social.media.types'

    _facebook_endpoint = 'https://graph.facebook.com'
    _instagram_endpoint = 'https://graph.instagram.com'
    social_media_types = fields.Selection(selection_add=[('facebook', 'Facebook'),
                                                         ('instagram','Instagram')])

    def action_get_accounts(self):
        self.ensure_one()
        if self.social_media_types == 'facebook':
            facebook_app_id = self.env['ir.config_parameter'].sudo().get_param('social_media_facebook.facebook_app_id')
            facebook_app_secret = self.env['ir.config_parameter'].sudo().get_param('social_media_facebook.facebook_app_secret')
            if facebook_app_id and facebook_app_secret:
                return self.configure_facebook_account(facebook_app_id)
            raise ValidationError(_('Facebook AppID and App secret are not Provided'))
        if self.social_media_types == 'instagram':
            instagram_app_id = self.env['ir.config_parameter'].sudo().get_param('social_media_facebook.instagram_app_id')
            instagram_app_secret = self.env['ir.config_parameter'].sudo().get_param('social_media_facebook.instagram_app_secret')
            if instagram_app_id and instagram_app_secret:
                return self.configure_instagram_account(instagram_app_id)
            raise ValidationError(_('Instagram AppID and App secret are not Provided'))
        return super(SocialMediaFacebook, self).action_get_accounts()

    def configure_instagram_account(self, appid):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        instagram_url = 'https://api.instagram.com/oauth/authorize?%s'
        params = {
            'client_id': appid,
            # 'redirect_uri': "https://f081-2405-201-f012-f02b-2856-e93c-a469-8b21.ngrok.io/instagram/callback",
            'redirect_uri': url_join(base_url, "instagram/callback"),
            'response_type': 'code',
            'scope': 'user_profile,user_media'}
        return {
            'type': 'ir.actions.act_url',
            'url': instagram_url % url_encode(params),
            'target': 'self'
        }

    def configure_facebook_account(self, appid):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        facebook_url = 'https://www.facebook.com/v13.0/dialog/oauth?%s'
        params = {
            'client_id': appid,
            'redirect_uri': url_join(base_url, "facebook/callback"),
            'response_type': 'token',
            'scope': 'leads_retrieval,pages_manage_ads,pages_read_engagement,ads_management'}
        return {
            'type': 'ir.actions.act_url',
            'url': facebook_url % url_encode(params),
            'target': 'self'
        }
