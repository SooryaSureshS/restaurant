from odoo import api, fields, models,_
from datetime import datetime
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError

class ScrapReportWizard(models.TransientModel):
    _name = "scrap.report.wizard"

    # order_no = fields.Char(string="Order No")
    from_date = fields.Date(string="From Date", default=datetime.today(),required=True)
    to_date = fields.Date(string="To Date", default=datetime.today(),required=True)



    def print_report(self):
        return self.env.ref('scrap_report.report_scrap').report_action(self, data=self.read([])[0])



class ScrapReport(models.AbstractModel):
    _name = 'report.scrap_report.report_scrap'

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date=data.get('from_date')
        end_date=data.get('to_date')
        domain =  [('date_done', '>=', start_date), ('date_done', '<=',end_date),('state','=','done')]
        scrap = self.env['stock.scrap'].search(domain)

        if not scrap:
            raise ValidationError(_('No scrap orders provided during the selected dates.'))
        return {
            'data': scrap,
            'doc_ids': docids,
            'doc_model': 'stock.scrap',
            'docs': docids,
            'start_date': datetime.strptime(start_date,'%Y-%m-%d').strftime("%m/%d/%Y"),
            'end_date': datetime.strptime(end_date,'%Y-%m-%d').strftime("%m/%d/%Y"),
        }