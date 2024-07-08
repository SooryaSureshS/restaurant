import logging
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, _
from odoo.http import request
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SurveySurvey(models.TransientModel):
    _inherit = "survey.invite"

    @api.model
    def _get_default_from(self):
        if self.env.user.email:
            return tools.formataddr((self.env.user.name, self.env.user.email))
        # raise UserError(_("Unable to post message, please configure the sender's email address."))

    def _send_mail(self, answer):
        """ Create mail specific for recipient containing notably its access token """
        subject = self.env['mail.render.mixin'].with_context(safe=True)._render_template(self.subject, 'survey.user_input', answer.ids, post_process=True)[answer.id]
        body = self.env['mail.render.mixin']._render_template(self.body, 'survey.user_input', answer.ids, post_process=True)[answer.id]
        # post the message
        if not self.email_from_selection:
            raise ValidationError(_("Select Email from"))
        if not self.email_from_selection.email:
            # return tools.formataddr((self.env.user.name, self.env.user.email))
            raise UserError(_("Unable to post message, please configure the sender's email address."))

        mail_values = {
            'email_from': tools.formataddr((self.email_from_selection.name, self.email_from_selection.email)),
            'author_id': self.author_id.id,
            'model': None,
            'res_id': None,
            'subject': subject,
            'body_html': body,
            'attachment_ids': [(4, att.id) for att in self.attachment_ids],
            'auto_delete': True,
        }
        if answer.partner_id:
            mail_values['recipient_ids'] = [(4, answer.partner_id.id)]
        else:
            mail_values['email_to'] = answer.email

        # optional support of notif_layout in context
        notif_layout = self.env.context.get('notif_layout', self.env.context.get('custom_layout'))
        if notif_layout:
            try:
                template = self.env.ref(notif_layout, raise_if_not_found=True)
            except ValueError:
                _logger.warning('QWeb template %s not found when sending survey mails. Sending without layouting.' % (notif_layout))
            else:
                template_ctx = {
                    'message': self.env['mail.message'].sudo().new(dict(body=mail_values['body_html'], record_name=self.survey_id.title)),
                    'model_description': self.env['ir.model']._get('survey.survey').display_name,
                    'company': self.env.company,
                }
                body = template._render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
                mail_values['body_html'] = self.env['mail.render.mixin']._replace_local_links(body)

        return self.env['mail.mail'].sudo().create(mail_values)

    email_from_selection = fields.Many2one('res.users',string="Email From")

