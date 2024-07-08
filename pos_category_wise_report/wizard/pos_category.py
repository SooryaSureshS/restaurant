from odoo import api, fields, models, _
from datetime import datetime
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError


class PosReportWizard(models.TransientModel):
    _name = "pos.category.report.wizard"

    from_date = fields.Date(string="From Date", default=datetime.today(), required=True)
    to_date = fields.Date(string="To Date", default=datetime.today(), required=True)
    net_sales = fields.Selection([('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year')],
                                 string="Net sales percentages accessible for", required=True)

    def print_report(self):
        return self.env.ref('pos_category_wise_report.pos_category_report_action').report_action(self,
                                                                                                 data=self.read([])[0])


class PosReportCategory(models.AbstractModel):
    _name = 'report.pos_category_wise_report.pos_category_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date = data.get('from_date')
        end_date = data.get('to_date')
        net_sales = data.get('net_sales')
        from datetime import datetime
        from dateutil import relativedelta
        date1 = datetime.strptime(start_date, '%Y-%m-%d')
        date2 = datetime.strptime(end_date, '%Y-%m-%d')
        r = relativedelta.relativedelta(date2, date1)
        date_difference = 1
        if net_sales == 'day':
            day = r.days
            if day != 0:
                date_difference = day
        elif net_sales == 'week':
            week = r.weeks
            if week != 0:
                date_difference = week
        elif net_sales == 'month':
            months = r.months
            if months != 0:
                date_difference = months
        elif net_sales == 'year':
            years = r.years
            if years != 0:
                date_difference = years

        all_category = self.env['pos.category'].search([])
        if not all_category:
            raise ValidationError(_('No Category Found.'))
        total_sale = []

        for cat in all_category:
            gross_sale = 0
            net_sale = 0
            sale_order_line = self.env['sale.order.line'].search(
                [('product_id.pos_categ_id', '=', cat.id), ('order_id.state', '=', 'sale'),
                 ('order_id.date_order', '>=', start_date), ('order_id.date_order', '<=', end_date)])
            pos_order_line = self.env['pos.order.line'].search(
                [('product_id.pos_categ_id', '=', cat.id), ('order_id.state', 'not in', ['draft','cancel']),
                 ('order_id.date_order', '>=', start_date), ('order_id.date_order', '<=', end_date)])
            print(cat.name,sale_order_line)
            if sale_order_line:
                gross_sale = gross_sale + sum([grs.price_total - grs.price_tax for grs in sale_order_line])
                net_sale = net_sale + sum([line.price_total for line in sale_order_line])
            if pos_order_line:
                gross_sale = gross_sale + sum([grs.price_subtotal for grs in pos_order_line])
                net_sale = net_sale + sum([line.price_subtotal_incl for line in pos_order_line])
            if gross_sale!=0:
                pro_net_sale=round(net_sale/date_difference)
                percentage =( pro_net_sale/round(net_sale))*100
                vales = {'cat_id': cat.id, 'cat_name': cat.name,'gross_sale':round(gross_sale),'net_sale':round(net_sale),'pro_net_sale':round(net_sale/date_difference),
                         'percentage':round(percentage)}
                total_sale.append(vales)
        if len(total_sale)<1:
            raise ValidationError(_('No data found for the selected Dates.'))
        return {
            'data': total_sale,
            'doc_ids': docids,
            'doc_model': 'pos.category',
            'docs': docids,
            'start_date': datetime.strptime(start_date,'%Y-%m-%d').strftime("%m/%d/%Y"),
            'end_date': datetime.strptime(end_date,'%Y-%m-%d').strftime("%m/%d/%Y"),
        }
