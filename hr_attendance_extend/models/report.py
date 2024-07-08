import pytz
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from datetime import datetime
from datetime import date
from datetime import timedelta


class TimesheetSummaryWizardInherit(models.TransientModel):
    _inherit = 'timesheet.approval.report'

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        today = date.today()
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError(_('Start Date cannot be greater than  End Date'))
            if self.start_date > today:
                raise ValidationError(_("Start date cannot be greater than today's date"))
            # if self.start_date == today:
            #     data = self.env['timesheet.approval'].sudo().search([('create_date', '>=', self.start_date),
            #                                                          ('create_date', '<=', self.end_date),
            #                                                          ('state', '=', 'publish')])
            #     if data:
            #         pass
            #     else:
            #         raise ValidationError(_("There is no published timesheet records"))

    def print_report(self):
        data = {
            'from_date': self.start_date,
            'to_date': self.end_date
        }
        print("date_data", data)
        return self.env.ref('hr_attendance_extend.report_attendance_summary').report_action(self, data=data)


class StudentCard(models.AbstractModel):
    _name = 'report.hr_attendance_extend.attendance_detailed_report_report'

    @api.model
    def _get_report_values(self, docids, data):
        docs = self.env['hr.attendance'].browse(docids)
        print(data, "datata")
        date_from = data['from_date']
        date_to = data['to_date']
        data = {}
        datass = self.env['hr.attendance'].search([('attendance_state', '=', 'approve'), ('check_in', '>=', date_from),
                                                   ('check_in', '<=', date_to)])
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        for rec in datass:
            template_context = pytz.utc.localize(rec.check_in).astimezone(
                tz).replace(
                tzinfo=None)

        return {
            'doc_ids': docids,
            'doc_model': 'hr.attendance',
            'docs': datass,
        }
