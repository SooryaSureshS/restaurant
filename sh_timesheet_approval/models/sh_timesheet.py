# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class SHTimesheet(models.Model):
    _name = 'account.analytic.line'
    _inherit = ['account.analytic.line', 'mail.thread']

    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), (
        'rejected', 'Rejected')], string="State", default='draft', track_visibility="onchange")
    sh_reject_reason = fields.Text(
        "Reject Reason", readonly=True, track_visibility="onchange")
    sh_rejected_by = fields.Many2one(
        'res.users', 'Rejected By', readonly=True, track_visibility="onchange")
    sh_rejected_date = fields.Datetime(
        'Rejected Date', readonly=True, track_visibility="onchange")
    sh_approved_by = fields.Many2one(
        'res.users', 'Approved By', readonly=True, track_visibility="onchange")
    sh_approved_date = fields.Datetime(
        'Approved Date', readonly=True, track_visibility="onchange")
    unit_amount = fields.Float(
        'Quantity', default=0.0, track_visiblity="onchange")
    base_url = fields.Char('URL', compute='_compute_url')

    def _compute_url(self):
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        action_id = self.env.ref('hr_timesheet.act_hr_timesheet_line')
        url_string = ''
        for rec in self:
            url_string += str(base_url)+'/web#id='+str(rec.id)+'&action=' + \
                str(action_id.id)+'&model=account.analytic.line&view_type=form'
            rec.base_url = url_string

    def sh_mass_approved_timesheet(self):
        for rec in self:
            template = self.env.ref(
                'sh_timesheet_approval.sh_approve_timesheet_template', raise_if_not_found=False)
            template.sudo().send_mail(rec.ids[0], force_send=True)
            rec.sh_approved_by = self.env.user.id
            rec.sh_approved_date = fields.Datetime.now()
            rec.state = 'approved'

    def action_submit_timesheet(self):
        self.state = 'submitted'

    def action_draft(self):
        self.state = 'draft'

    def action_approve_timesheet(self):
        template = self.env.ref(
            'sh_timesheet_approval.sh_approve_timesheet_template', raise_if_not_found=False)
        template.sudo().send_mail(self.ids[0], force_send=True)
        self.sh_approved_by = self.env.user.id
        self.sh_approved_date = fields.Datetime.now()
        self.state = 'approved'

    def action_reject_timesheet(self):
        return {
            'name': 'Timesheet Reject',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.timesheet.reject.wizard',
            'target': 'new',
        }
