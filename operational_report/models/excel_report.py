# -*- encoding: utf-8 -*-

from odoo import models, api, fields
import xlsxwriter
from docutils.nodes import row

class OperationalReportXlsx(models.AbstractModel):
    _name = 'report.operational_report.report_operational_xlsx'
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, records):
        worksheet = workbook.add_worksheet('Operational Report')
        format5 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        format4 = workbook.add_format({'font_size': 10, 'align': 'center'})
        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 10})
        heading_format1 = workbook.add_format({'align': 'center',
                                               'valign': 'vcenter',
                                               'bold': True, 'size': 16})
        worksheet.merge_range('A1:H1', "Operational Report", heading_format1)

        vals = []
        pos = {}
        if data['from_date'] and data['to_date']:
            worksheet.set_column(0, 0, 5)
            worksheet.set_column(1, 1, 18)

            worksheet.set_column(2, 2, 15)
            worksheet.set_column(3, 3, 15)
            worksheet.set_column(4, 4, 15)
            worksheet.set_column(5, 5, 15)
            worksheet.set_column(6, 6, 20)
            worksheet.set_column(7, 7, 15)

            worksheet.write(3, 0, "Sl. No.", heading_format)
            worksheet.write(3, 1, "Order", heading_format)
            worksheet.write(3, 2, "Order Date", heading_format)
            worksheet.write(3, 3, "Picking Date", heading_format)
            worksheet.write(3, 4, "Start Time", heading_format)
            worksheet.write(3, 5, "Cooked Time", heading_format)
            worksheet.write(3, 6, "Collect/Delivery TIme", heading_format)
            worksheet.write(3, 7, "Preparation Time", heading_format)

            sale_order = self.env['sale.order'].search([('date_order', '>=', data['from_date']), ('date_order', '<=', data['to_date'])])

            for order in sale_order:

                vals.append({

                            # self.partner_id.ref if str(self.partner_id.ref).isdecimal() else str(self.partner_id.id))
                            'order_name': order.name,
                            'date_order': order.date_order.strftime("%d-%m-%Y %H:%M") if order.date_order else'',
                            'pickup_date_string': order.pickup_date_string or '',
                            'start_order_time': order.start_order_time.strftime("%d-%m-%Y %H:%M") if order.start_order_time else'',
                            'finish_order_time': order.finish_order_time.strftime("%d-%m-%Y %H:%M") if order.finish_order_time else '',
                            'delivery_order_time': order.delivery_order_time.strftime("%d-%m-%Y %H:%M") if order.delivery_order_time else '',
                            'done_order_time': order.done_order_time.strftime("%d-%m-%Y %H:%M") if order.done_order_time else '',
                            })
            pos_config = self.env['pos.order'].search([('date_order', '>=', data['from_date']), ('date_order', '<=', data['to_date'])])
            for pos in pos_config:
                vals.append({
                            'order_name': pos.pos_reference,
                            'date_order': pos.date_order.strftime("%d-%m-%Y %H:%M") if pos.date_order else'',
                            'pickup_date_string': '',
                            'start_order_time': pos.start_order_time.strftime("%d-%m-%Y %H:%M") if pos.start_order_time else'',
                            'finish_order_time': pos.finish_order_time.strftime("%d-%m-%Y %H:%M") if pos.finish_order_time else '',
                            'delivery_order_time': pos.delivery_order_time.strftime("%d-%m-%Y %H:%M") if pos.delivery_order_time else '',
                            'done_order_time': pos.done_order_time.strftime("%d-%m-%Y %H:%M") if pos.done_order_time else '',
                            })
            i = 0
            row = 3
            column = 0
            for data in vals:
                print(data)
                row += 1
                worksheet.write(row + 1, column, i + 1, format4)
                worksheet.write(row + 1, column + 1, data['order_name'], format4)
                worksheet.write(row + 1, column + 2, data['date_order'], format4)
                worksheet.write(row + 1, column + 3, data['pickup_date_string'], format4)
                worksheet.write(row + 1, column + 4, data['start_order_time'], format4)
                worksheet.write(row + 1, column + 5, data['finish_order_time'], format4)
                worksheet.write(row + 1, column + 6, data['delivery_order_time'], format4)
                worksheet.write(row + 1, column + 7, data['done_order_time'], format4)
                i += 1

        else:
            worksheet.write(2, 1, "Order", heading_format)
