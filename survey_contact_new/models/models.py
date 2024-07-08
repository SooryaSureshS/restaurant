# from odoo import models, fields, api
#
# class Partner(models.Model):
#     _inherit = 'res.partner'
#     _description = 'Contact'


# class survey_contact(models.Model):
#     _name = 'survey_contact.survey_contact'
#     _description = 'survey_contact.survey_contact'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

# from ast import literal_eval
# import re
# from odoo import api, exceptions, fields, models, tools, _
# from odoo.exceptions import AccessError, UserError
# from odoo.osv import expression
# import logging
# _logger = logging.getLogger(__name__)
#
# emails_split = re.compile(r"[;,\n\r]+")
#
# MASS_MAILING_BUSINESS_MODELS = [
#     'crm.lead',
#     'event.registration',
#     'hr.applicant',
#     'res.partner',
#     'event.track',
#     'sale.order',
#     'mailing.list',
#     'mailing.contact'
# ]
#
#
# class SurveyCont(models.TransientModel):
#     _inherit = 'survey.invite'
#
#
#
#     mailing_model_id = fields.Many2one(
#         'ir.model', string='Recipients Model', ondelete='cascade', required=True,
#         domain=[('model', 'in', MASS_MAILING_BUSINESS_MODELS)],
#         default=lambda self: self.env.ref('mass_mailing.model_mailing_list').id)
#
#     contact_list_ids = fields.Many2many('mailing.list', 'mail_mass_mailing_list_rel1', string='Mailing Lists')
#     mailing_model_name = fields.Char(
#         string='Recipients Model Name', related='mailing_model_id.model',
#         readonly=True, related_sudo=True)
#     mailing_model_real = fields.Char(string='Recipients Real Model',
#                                      compute='_compute_model')
#     mailing_domain = fields.Char(
#         string='Domain', compute='_compute_mailing_domain',
#         readonly=False, store=True)
#
#     @api.depends('mailing_model_id')
#     def _compute_model(self):
#         for record in self:
#             record.mailing_model_real = (
#                                                 record.mailing_model_name != 'mailing.list') and record.mailing_model_name or 'mailing.contact'
#
#     @api.depends('mailing_model_name', 'contact_list_ids')
#     def _compute_mailing_domain(self):
#         for mailing in self:
#             if not mailing.mailing_model_name:
#                 mailing.mailing_domain = ''
#             else:
#                 mailing.mailing_domain = repr(mailing._get_default_mailing_domain())
#
#     def _get_default_mailing_domain(self):
#         mailing_domain = []
#         if self.mailing_model_name == 'mailing.list' and self.contact_list_ids:
#             mailing_domain = [('list_ids', 'in', self.contact_list_ids.ids)]
#
#         if 'is_blacklisted' in self.env[self.mailing_model_name]._fields:
#             mailing_domain = expression.AND([[('is_blacklisted', '=', False)], mailing_domain])
#         print(mailing_domain,'domainnnnnnnnnnnnnnnnnnn')
#
#         return mailing_domain
#
#     @api.model
#     def default_get(self, fields):
#         vals = super(SurveyCont, self).default_get(fields)
#         if 'contact_list_ids' in fields and not vals.get('contact_list_ids') and vals.get('mailing_model_id'):
#             if vals.get('mailing_model_id') == self.env['ir.model']._get('mailing.list').id:
#                 mailing_list = self.env['mailing.list'].search([], limit=2)
#                 if len(mailing_list) == 1:
#                     vals['contact_list_ids'] = [(6, 0, [mailing_list.id])]
#         return vals
#     def _send_mail(self, answer):
#         """ Create mail specific for recipient containing notably its access token """
#         subject = self.env['mail.render.mixin']._render_template(self.subject, 'survey.user_input', answer.ids, post_process=True)[answer.id]
#         body = self.env['mail.render.mixin']._render_template(self.body, 'survey.user_input', answer.ids, post_process=True)[answer.id]
#         # post the message
#         mail_values = {
#             'email_from': self.email_from,
#             'author_id': self.author_id.id,
#             'model': None,
#             'res_id': None,
#             'subject': subject,
#             'body_html': body,
#             'attachment_ids': [(4, att.id) for att in self.attachment_ids],
#             'auto_delete': True,
#         }
#         if answer.partner_id:
#             mail_values['recipient_ids'] = [(4, answer.partner_id.id)]
#         else:
#             mail_values['email_to'] = answer.email
#
#         # optional support of notif_layout in context
#         notif_layout = self.env.context.get('notif_layout', self.env.context.get('custom_layout'))
#         if notif_layout:
#             try:
#                 template = self.env.ref(notif_layout, raise_if_not_found=True)
#             except ValueError:
#                 _logger.warning('QWeb template %s not found when sending survey mails. Sending without layouting.' % (notif_layout))
#             else:
#                 template_ctx = {
#                     'message': self.env['mail.message'].sudo().new(dict(body=mail_values['body_html'], record_name=self.survey_id.title)),
#                     'model_description': self.env['ir.model']._get('survey.survey').display_name,
#                     'company': self.env.company,
#                 }
#                 body = template._render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
#                 mail_values['body_html'] = self.env['mail.render.mixin']._replace_local_links(body)
#
#         return self.env['mail.mail'].sudo().create(mail_values)
#     def action_invite(self):
#         valid_partners=0
#         valid_emails=0
#         mailing_domain = []
#         mailing_domains=0
#         if 'is_blacklisted' in self.env[self.mailing_model_name]._fields:
#             print(self.env[self.mailing_model_name]._fields,"ppppp")
#             mailing_domain = expression.AND([[('is_blacklisted', '=', False)], mailing_domain])
#             print("dpmavvvvvvvvin",mailing_domain,"domain")
#             # if self.mailing_model_id:
#             #     """ Process the wizard content and proceed with sending the related
#             #         email(s), rendering any template patterns on the fly if needed """
#             #     self.ensure_one()
#             rece_lst = []
#             Partner = self.env['res.partner']
#             #     a=self.env[self.mailing_model_id.model].search([])
#             #     print(a,"aa")
#             #     mailing_domain = literal_eval(self.mailing_domain)
#             #
#             #     print("sfgrfd",mailing_domain)
#             try:
#
#                 mailing_domain = literal_eval(self.mailing_domain )
#
#
#                 print("yes",self.mailing_model_id.model)
#                 print("trydom,",mailing_domain)
#             except Exception:
#                 mailing_domain = [('id', 'in', [])]
#                 print("yy")
#             print(mailing_domain,"iiii")
#
#
#
#             partner_obj = self.env[self.mailing_model_name].search(mailing_domain)
#             for x in partner_obj:
#                 print(x.name,"nammm")
#
#             print("elc",len(partner_obj))
#
#
#             for data in partner_obj:
#                 rece_lst.append(data.id)
#             print("listelc",len(rece_lst))
#
#
#             self.mailing_model_id = [(6, 0, rece_lst)]
#             # compute partners and emails, try to find partners for given emails
#             valid_partners = self.mailing_model_id
#
#             valid_emails = []
#             for email in emails_split.split(self.emails or ''):
#                 partner = False
#                 email_normalized = tools.email_normalize(email)
#                 if email_normalized:
#                     limit = None if self.survey_users_login_required else 1
#                     partner = Partner.search([('email_normalized', '=', email_normalized)], limit=limit)
#                     print(partner,"ppppp")
#                 if partner:
#                     valid_partners |= partner
#                 else:
#                     email_formatted = tools.email_split_and_format(email)
#                     if email_formatted:
#                         valid_emails.extend(email_formatted)
#
#             if not valid_partners and not valid_emails:
#                 raise UserError(_("Please enter at least one valid recipient."))
#             print("lenn",len(rece_lst))
#             print("emmm",valid_emails)
#
#             answers = self._prepare_answers(valid_partners, valid_emails)
#             for answer in answers:
#                 self._send_mail(answer)
#
#             return {'type': 'ir.actions.act_window_close'}
#
# class PartnerInherits(models.Model):
#     _inherit = "res.partner"
#     _description = 'Contact'