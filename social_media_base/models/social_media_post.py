from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError
import json


class SocialMediaPost(models.Model):
    _name = 'social.media.post'
    _description = 'social media post'

    is_facebook = fields.Boolean('Facebook')
    is_instagram = fields.Boolean('Instagram')
    message = fields.Text("Message")
    status = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('posting', 'Posting'),
        ('posted', 'Posted')],
        string='Status', default='draft', readonly=True)
    is_failed = fields.Boolean()
    failure_reason = fields.Char()
    has_post_errors = fields.Boolean("There are post errors on sub-posts" )
    social_media_account_ids = fields.Many2many('social.media.accounts', 'social_media_post_social_media_account', 'post_id', 'account_id',
                                   string='Social Accounts')
    has_active_accounts = fields.Boolean('Are Accounts Available?')
    social_media_ids = fields.Many2many('social.media', store=True)
    social_media_post_lines = fields.One2many('social.media.post.lines', 'social_media_post_id', string="Posts By Account", readonly=True)
    image_html = fields.Char('Kanban Images', compute='compute_image_html')
    image_ids = fields.Many2many('ir.attachment', string='Attach Images')
    publish_method = fields.Selection([
        ('now', 'Send now'),
        ('scheduled', 'Schedule later')], string="When", default='now')
    scheduled_date = fields.Datetime('Scheduled post date')
    published_date = fields.Datetime('Published date', readonly=True)

    @api.depends('image_ids')
    def compute_image_html(self):
        for rec in self:
            rec.image_html = 'localhost:8014/'+rec.image_ids.image_src

    def get_social_media_post_status(self):
        completed_lines = [n for n in self.social_media_post_lines if self.social_media_post_lines.status in ('posted', 'failed')]
        if completed_lines:
            self.sudo().write({'status': 'posted'})

    @api.onchange('is_facebook','is_instagram')
    def social_media_account_filter(self):
        if self.is_instagram and self.is_facebook:
            if self.env.context.get('bool_media_type'):
                return {'domain': {'social_media_account_ids': [('social_media_type', 'in', ['facebook','instagram'])]}}
        else:
            self.social_media_account_ids = False
            return {'domain': {
                'social_media_account_ids': [('social_media_type', '=', self.env.context.get('bool_media_type'))]}}

    @api.constrains('image_ids')
    def check_image_ids_mimetype(self):
        for social_post in self:
            if any(not image.mimetype.startswith('image') for image in social_post.image_ids):
                raise UserError(_('Uploaded file does not seem to be a valid image.'))

    def name_get(self):
        result = []
        for post in self:
            if post.message:
                name = post.message[:20] + '...'
            else:
                name = 'No name yet'
            result.append((post.id, name))
        return result

    def publish(self):
        self.write({
            'publish_method': 'now',
            'scheduled_date': False,
            'status': 'posting',
            'published_date': fields.Datetime.now(),
            'social_media_post_lines': [(0, 0, {'social_media_post_id': self.id, 'social_media_account_id': account.id})for account in self.social_media_account_ids]
        })
        for social_post in self.social_media_post_lines:
            social_post.publish_post()

    def action_schedule(self):
        self.write({'status': 'scheduled'})

    def cron_schedule(self):
        print('fffffff')
        scheduled_post = self.search([('status', '=', 'scheduled'), ('publish_method', '=', 'scheduled'), ('scheduled_date', '<=', fields.Datetime.now())])
        if scheduled_post:
            for rec in scheduled_post:
                rec.publish()


class SocialMediaPostLines(models.Model):
    _name = 'social.media.post.lines'
    _description = 'Social media post lines'

    social_media_post_id = fields.Many2one('social.media.post')
    social_media_account_id = fields.Many2one('social.media.accounts', string="Social Media Account", required=True)
    reason_for_failure = fields.Text('Failure Reason')
    status = fields.Selection([
        ('ready', 'Ready'),
        ('posted', 'POSTED'),
        ('failed', 'Failed')],
        string='Status', default='ready', required=True)
    social_media_type = fields.Char(compute="compute_social_media_types")
    account_name = fields.Char(compute='compute_account_name')

    def compute_social_media_types(self):
        for rec in self:
            rec.social_media_type = rec.social_media_account_id.social_media_type
            rec.account_name = rec.social_media_account_id.name

    def publish_post(self):
        pass

    def name_get(self):
        return [(n.id, n.social_media_account_id.social_media_type+"-"+n.social_media_post_id.message ) for n in self]