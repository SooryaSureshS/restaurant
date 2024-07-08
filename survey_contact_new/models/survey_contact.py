from ast import literal_eval
import re
from odoo import api, exceptions, fields, models, tools, _
from odoo.exceptions import AccessError, UserError
from odoo.osv import expression

emails_split = re.compile(r"[;,\n\r]+")

MASS_MAILING_BUSINESS_MODELS = [
    # 'crm.lead',
    # 'event.registration',
    # 'hr.applicant',
    'res.partner',
    # 'event.track',
    # 'sale.order',
    # 'mailing.list',
    # 'mailing.contact'
]


class SurveyCont(models.TransientModel):
    _inherit = 'survey.invite'

    mailing_model_id = fields.Many2one(
        'ir.model', string='Recipients Model', ondelete='cascade', required=True,
        domain=[('model', 'in', MASS_MAILING_BUSINESS_MODELS)], )
    # default=lambda self: self.env.ref('mass_mailing.model_mailing_list').id)

    contact_list_ids = fields.Many2many('mailing.list', 'mail_mass_mailing_list_rel1', string='Mailing Lists')
    mailing_model_name = fields.Char(
        string='Recipients Model Name', related='mailing_model_id.model',
        readonly=True, related_sudo=True)
    mailing_model_real = fields.Char(string='Recipients Real Model',
                                     compute='_compute_model')
    mailing_domain = fields.Char(
        string='Domain', compute='_compute_mailing_domain',
        readonly=False, store=True)

    @api.depends('mailing_model_id')
    def _compute_model(self):
        for record in self:
            record.mailing_model_real = (
                                                record.mailing_model_name != 'mailing.list') and record.mailing_model_name or 'mailing.contact'

    @api.depends('mailing_model_name', 'contact_list_ids')
    def _compute_mailing_domain(self):
        for mailing in self:
            if not mailing.mailing_model_name:
                mailing.mailing_domain = ''
            else:
                mailing.mailing_domain = repr(mailing._get_default_mailing_domain())

    def _get_default_mailing_domain(self):
        mailing_domain = []
        if self.mailing_model_name == 'mailing.list' and self.contact_list_ids:
            mailing_domain = [('list_ids', 'in', self.contact_list_ids.ids)]

        if 'is_blacklisted' in self.env[self.mailing_model_name]._fields:
            mailing_domain = expression.AND([[('is_blacklisted', '=', False)], mailing_domain])

        return mailing_domain

    @api.model
    def default_get(self, fields):
        vals = super(SurveyCont, self).default_get(fields)
        if 'contact_list_ids' in fields and not vals.get('contact_list_ids') and vals.get('mailing_model_id'):
            if vals.get('mailing_model_id') == self.env['ir.model']._get('mailing.list').id:
                mailing_list = self.env['mailing.list'].search([], limit=2)
                if len(mailing_list) == 1:
                    vals['contact_list_ids'] = [(6, 0, [mailing_list.id])]
        return vals


    def _prepare_answers(self, partners, emails):
        answers = self.env['survey.user_input']
        existing_answers = self.env['survey.user_input'].search([
            '&', ('survey_id', '=', self.survey_id.id),
            '|',
            ('partner_id', 'in', partners.ids),
            ('email', 'in', emails)
        ])
        partners_done = self.env['res.partner']
        emails_done = []
        if existing_answers:
            if self.existing_mode == 'resend':
                partners_done = existing_answers.mapped('partner_id')
                emails_done = existing_answers.mapped('email')

                # only add the last answer for each user of each type (partner_id & email)
                # to have only one mail sent per user
                for partner_done in partners_done:
                    answers |= next(existing_answer for existing_answer in
                                    existing_answers.sorted(lambda answer: answer.create_date, reverse=True)
                                    if existing_answer.partner_id == partner_done)

                for email_done in emails_done:
                    answers |= next(existing_answer for existing_answer in
                                    existing_answers.sorted(lambda answer: answer.create_date, reverse=True)
                                    if existing_answer.email == email_done)

        for new_partner in partners - partners_done:
            answers |= self.survey_id._create_answer(partner=new_partner, check_attempts=False, **self._get_answers_values())
        for new_email in [email for email in emails if email not in emails_done]:
            answers |= self.survey_id._create_answer(email=new_email, check_attempts=False, **self._get_answers_values())

        return answers

    def action_invite(self):
        if self.mailing_model_id:
            """ Process the wizard content and proceed with sending the related
                email(s), rendering any template patterns on the fly if needed """
            self.ensure_one()
            rece_lst = []
            Partner = self.env['res.partner']
            try:
                mailing_domain = literal_eval(self.mailing_domain)
            except Exception:
                mailing_domain = [('id', 'in', [])]
            print("trydom,",mailing_domain)

            partner_obj = self.env['res.partner'].search(mailing_domain)
            print("partner_obj", partner_obj)
            print("lennn",len(partner_obj))

            for data in partner_obj:
                # if data.email:
                    # print(data, data.name, "partner_obj")
                rece_lst.append(data.id)
            print("list lennn",len(rece_lst))
            self.partner_ids = [(6, 0, rece_lst)]
                # compute partners and emails, try to find partners for given emails
            valid_partners = self.partner_ids
            print(valid_partners, "valid_partners")
            valid_emails = []
            for email in emails_split.split(self.emails or ''):
                partner = False
                email_normalized = tools.email_normalize(email)
                if email_normalized:
                    limit = None if self.survey_users_login_required else 1
                    partner = Partner.search([('email_normalized', '=', email_normalized)], limit=limit)
                if partner:
                    valid_partners |= partner
                else:
                    email_formatted = tools.email_split_and_format(email)
                    if email_formatted:
                        valid_emails.extend(email_formatted)

            if not valid_partners and not valid_emails:
                raise UserError(_("Please enter at least one valid recipient."))

            answers = self._prepare_answers(valid_partners, valid_emails)
            for answer in answers:
                self._send_mail(answer)

            return {'type': 'ir.actions.act_window_close'}