from odoo import api, fields, models, _
from datetime import date, datetime
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError


class SalesDetails(models.TransientModel):
    _name = 'sales.report.wizard'
    _description = 'Sales Details Report'

    start_date = fields.Date(string="Start Date", default=date.today() - timedelta(days=6))
    end_date = fields.Date(string="End Date", default=date.today())

    def generate_report_pdf(self):
        data = {'date_start': self.start_date, 'date_end': self.end_date}
        return self.env.ref('sales_report.sales_details_pdf_report').report_action([], data=data)

    def generate_report_xlsx(self):
        data = {'date_start': self.start_date, 'date_end': self.end_date}
        return self.env.ref('sales_report.sales_details_xlsx_report').report_action([], data=data)

    @api.onchange('start_date')
    def valid_range(self):
        if (self.end_date - self.start_date).days < 6:
            raise ValidationError(_("Incorrect Week Interval"))
