from odoo import models, fields, api


class SocialMediaTypes(models.Model):
    _name = 'social.media.types'
    _description = 'social media types'

    name = fields.Char(string='Name', required=True, readonly=True)
    description = fields.Char('Description', readonly=True)
    social_media_types = fields.Selection([], readonly=True)
    social_media_account_ids = fields.One2many('social.media.accounts','social_media_id', strings='Social Media Accounts', readonly=True)
    social_media_account_counts = fields.Integer(readonly=True)
    image = fields.Binary('Image', readonly=True)
    can_link_accounts = fields.Boolean('Can link accounts ?', default=True, readonly=True, required=True)

    def action_get_accounts(self):
        pass