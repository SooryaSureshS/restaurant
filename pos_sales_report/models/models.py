# -*- encoding: utf-8 -*-

from odoo import models, api, fields, _
import xlsxwriter
from odoo.osv.expression import AND
import pytz
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from docutils.nodes import row


class ReportExcel(models.TransientModel):
    _inherit = "pos.details.wizard"

    def action_report_excel(self):
        print(self)
        return self.env.ref('pos_sales_report.sales_details_report').report_action(self)


class SalesDetailsReportXlsx(models.AbstractModel):
    _name = 'report.pos_sales_report.report_pos_xlsx'
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, records, session_ids=False):
        tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        worksheet = workbook.add_worksheet('Sales Details Report')
        start = records.start_date.astimezone(tz).strftime('%m-%d-%Y %H:%M:%S')
        end = records.end_date.astimezone(tz).strftime('%m-%d-%Y %H:%M:%S')
        format5 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        format4 = workbook.add_format({'font_size': 10, 'align': 'center'})
        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 10})
        heading_format1 = workbook.add_format({'align': 'center',
                                               'valign': 'vcenter',
                                               'bold': True, 'size': 16})
        date_format = workbook.add_format({'align': 'center',
                                           'valign': 'vcenter',
                                           'bold': True, 'size': 12})
        heading_format2 = workbook.add_format({'align': 'left',
                                               'valign': 'left',
                                               'bold': True, 'size': 12})
        worksheet.merge_range('A1:H1', "Sales Details Report", heading_format1)
        worksheet.merge_range('A2:H2', start + '-' + end, date_format)
        worksheet.write(2, 0, "Products", heading_format2)
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 30)

        worksheet.set_column(2, 2, 15)
        worksheet.set_column(3, 3, 15)

        worksheet.write(4, 0, "Sl. No.", heading_format)
        worksheet.write(4, 1, "Product", heading_format)
        worksheet.write(4, 2, "Quantity", heading_format)
        worksheet.write(4, 3, "Price Unit", heading_format)

        domain = [('state', 'in', ['paid', 'invoiced', 'done'])]
        if (session_ids):
            domain = AND([domain, [('session_id', 'in', session_ids)]])
        else:
            if records.start_date:
                date_start = records.start_date
            else:
                # start by default today 00:00:00
                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
                today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
                date_start = today.astimezone(pytz.timezone('UTC'))

            if records.end_date:
                date_stop = records.end_date
                # avoid a date_stop smaller than date_start
                if (date_stop < date_start):
                    date_stop = date_start + timedelta(days=1, seconds=-1)
            else:
                # stop by default today 23:59:59
                date_stop = date_start + timedelta(days=1, seconds=-1)

            domain = AND([domain,
                          [('date_order', '>=', fields.Datetime.to_string(date_start)),
                           ('date_order', '<=', fields.Datetime.to_string(date_stop))]
                          ])
            conf = []
            if records.pos_config_ids:
                for rec in records.pos_config_ids:
                    conf.append(rec.id)
                domain = AND([domain, [('config_id', 'in', conf)]])

        orders = self.env['pos.order'].search(domain)
        # if not orders:
        #     raise ValidationError(_('No Sales details found'))

        user_currency = self.env.company.currency_id

        total = 0.0
        products_sold = {}
        taxes = {}
        for order in orders:
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id._convert(
                    order.amount_total, user_currency, order.company_id, order.date_order or fields.Date.today())
            else:
                total += order.amount_total
            currency = order.session_id.currency_id

            for line in order.lines:
                key = (line.product_id, line.price_unit, line.discount)
                products_sold.setdefault(key, 0.0)
                products_sold[key] += line.qty

                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.sudo().compute_all(
                        line.price_unit * (1 - (line.discount or 0.0) / 100.0), currency, line.qty,
                        product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'tax_amount': 0.0, 'base_amount': 0.0})
                        taxes[tax['id']]['tax_amount'] += tax['amount']
                        taxes[tax['id']]['base_amount'] += tax['base']
                else:
                    taxes.setdefault(0, {'name': _('No Taxes'), 'tax_amount': 0.0, 'base_amount': 0.0})
                    taxes[0]['base_amount'] += line.price_subtotal_incl

        payment_ids = self.env["pos.payment"].search([('pos_order_id', 'in', orders.ids)]).ids
        if payment_ids:
            self.env.cr.execute("""
                        SELECT method.name, sum(amount) total
                        FROM pos_payment AS payment,
                             pos_payment_method AS method
                        WHERE payment.payment_method_id = method.id
                            AND payment.id IN %s
                        GROUP BY method.name
                    """, (tuple(payment_ids),))
            payments = self.env.cr.dictfetchall()
        else:
            payments = []

        values = {
            'currency_precision': user_currency.decimal_places,
            'total_paid': user_currency.round(total),
            'payments': payments,
            'company_name': self.env.company.name,
            'taxes': list(taxes.values()),
            'products': sorted([{
                'product_id': product.id,
                'product_name': product.name,
                'code': product.default_code,
                'quantity': qty,
                'price_unit': price_unit,
                'discount': discount,
                'uom': product.uom_id.name
            } for (product, price_unit, discount), qty in products_sold.items()], key=lambda l: l['product_name'])
        }

        i = 0
        row = 3
        column = 0
        for data in values.get('products'):
            row += 1
            worksheet.write(row + 1, column, i + 1, format4)
            worksheet.write(row + 1, column + 1, data.get('product_name'), format4)
            worksheet.write(row + 1, column + 2, data.get('quantity'), format4)
            worksheet.write(row + 1, column + 3, data['price_unit'], format4)
            i += 1
        worksheet.write(row + 3, 0, "Payments", heading_format2)
        worksheet.write(row + 5, 0, "Name", heading_format)
        worksheet.write(row + 5, 1, "Total", heading_format)
        for datas in values.get('payments'):
            row += 1
            worksheet.write(row + 6, column, datas.get('name'), format4)
            worksheet.write(row + 6, column + 1, datas.get('total'), format4)
        worksheet.write(row + 8, 0, "Taxes", heading_format2)
        worksheet.write(row + 10, 0, "Name", heading_format)
        worksheet.write(row + 10, 1, "Tax Amount", heading_format)
        worksheet.write(row + 10, 2, "Base Amount", heading_format)
        for taxed in values.get('taxes'):
            row += 1
            worksheet.write(row + 11, column, taxed.get('name'), format4)
            worksheet.write(row + 11, column + 1, taxed.get('tax_amount'), format4)
            worksheet.write(row + 11, column + 2, round(taxed.get('base_amount'), 2), format4)

        worksheet.write(row + 14, 0, "Total:", heading_format)
        worksheet.write(row + 14, 1, values.get('total_paid'), format4)
