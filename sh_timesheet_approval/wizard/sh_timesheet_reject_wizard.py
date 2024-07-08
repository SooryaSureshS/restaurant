# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class ShTimesheetRejectWizard(models.TransientModel):
    _name = 'sh.timesheet.reject.wizard'
    _description = 'Timesheet Reject'

    name = fields.Text("Reason", required=True)

    def action_reject(self):
        for timesheet_id in self.env['account.analytic.line'].sudo().search([('id', 'in', self.env.context.get('active_ids'))]):
            timesheet_id.sudo().write({
                'sh_reject_reason': self.name,
                'sh_rejected_by': self.env.user.id,
                'sh_rejected_date': fields.Datetime.now(),
                'state': 'rejected'
            })
            template = self.env.ref(
                'sh_timesheet_approval.sh_reject_timesheet_template', raise_if_not_found=False)
            template.sudo().send_mail(timesheet_id.ids[0], force_send=True)
