from odoo import api, fields, models,_
from datetime import datetime
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError

class OperationalReportWizard(models.TransientModel):
    _name = "feedback.report.wizard"

    report_summary_file = fields.Binary('Generated Report')
    # order_no = fields.Char(string="Order No")
    from_date = fields.Date(string="From Date", default=datetime.today())
    to_date = fields.Date(string="To Date", default=datetime.today())
    feedback_face = fields.Selection(
        [('good', 'Good Experience'), ('sad', 'Poor Experience'), ('all', 'All Faces')], 'Feedback Face', required=True)

    # order_date = fields.Date(string="Order Date", default=datetime.today())
    # picking_time = fields.Date(string="Picking Time", default=datetime.today())

    @api.constrains('from_date', 'to_date')
    def _date_check(self):
        today = date.today()
        if not self.from_date:
            raise ValidationError(_('Select From Date'))
        if not self.to_date:
            raise ValidationError(_('Select To Date'))
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValidationError(_('From date should be less than To Date'))


    def print_report(self):
        return self.env.ref('website_delivery_type.report_feedback').report_action(self, data=self.read([])[0])



class ReplenishmentTemplateReport(models.AbstractModel):
    _name = 'report.website_delivery_type.report_feed_back'
    @api.model
    def _get_report_values(self, docids, data=None):
        start_date=data.get('from_date')
        end_date=data.get('to_date')
        feedback_face=data.get('feedback_face')
        print(start_date,end_date)
        domain =  [('date_order', '>=', start_date), ('date_order', '<=',end_date),('feedback_check','!=',False)]
        if feedback_face=='sad':
            domain.append(('feedback_face', '=', 'sad'))
        elif feedback_face=='good':
            domain.append(('feedback_face', '=', 'good'))
        else:
            pass
        sale_order = self.env['sale.order'].search(domain)
        if not sale_order:
            raise ValidationError(_('No feedback provided during the selected dates.'))
        print(sale_order)
        return {
            'data': sale_order,
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docids,
        }