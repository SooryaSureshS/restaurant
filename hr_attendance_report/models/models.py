from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from datetime import datetime
from datetime import date
from datetime import timedelta


class HrAttendanceReportCustom(models.Model):
    _inherit = 'hr.attendance'


class AttendanceReportData(models.AbstractModel):
    _name = 'report.hr_attendance_report.report_template_custom'

    @api.model
    def _get_report_values(self, docids, data=None):
        datas = self.env['hr.attendance'].search([('id', '=', docids)])
        docs = datas
        shift = []
        total = 0
        for i in datas:
            shift.append(i.worked_hours*i.base_pay)
        for ele in range(0, len(shift)):
            total = total + shift[ele]
        return {
            'docs': docs,
            'shift': total,
        }
