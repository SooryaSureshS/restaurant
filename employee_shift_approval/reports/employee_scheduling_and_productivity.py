# from odoo import models
#
# class EmployeeScheduleXlsx(models.AbstractModel):
#     _name = 'report.employee_shift_approval.scheduling_productivity_report'
#     _inherit = 'report.report_xlsx.abstract'
#
#     def generate_xlsx_report(self, workbook, data, employees):
#         format_sub_head = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center'})
#         format_main_head = workbook.add_format({'font_size': 14, 'bold': True})
#         format_h_value = workbook.add_format()
#         format_h_value.set_align('center')
#         sheet = workbook.add_worksheet('Employees Scheduling and Productivity')
#         bold = workbook.add_format({'bold': True})
#         row=5
#         col=5
#         sheet.write(row, col, 'Employee Scheduling and Productivity Report',format_main_head)
#         sheet.set_column('A:A',18)
#
#         sheet.write(9, 0, 'Sales NET', bold)
#         sheet.write(10, 0, 'Labour $', bold)
#         sheet.write(11, 0, 'Labour %', bold)
#         sheet.write(12, 0, 'Scheduled Hours', bold)
#         sheet.write(13, 0, 'Timesheet Hours', bold)
#         sheet.write(14, 0, 'SPMH', bold)
#         sheet.write(15, 0, 'AHR', bold)
#         row= 7
#         col=0
#         summary_dict={}
#         start=data['start_date']
#         end=data['end_date']
#         summary_list=[]
#         data = self.env['timesheet.approval'].sudo().search([('create_date', '>=', start),
#                                                              ('create_date', '<=', end),('state','=','publish')])
#         currency=0
#         company =self.env['res.company'].sudo().search([],limit=1)
#         for x in company:
#             currency=str(x.currency_id.symbol)
#
#
#         if data:
#
#             for line in data:
#                 c_date = line.create_date.strftime('%d-%m-%Y')
#
#                 c_date_data = data.filtered(lambda r:  r.create_date.strftime('%d-%m-%Y') == c_date)
#                 labour_wages=0
#                 scheduled_hours=0
#                 timesheet_hours=0
#
#                 for datas in c_date_data:
#
#                     labour_wages =labour_wages+datas.timesheet_wages
#
#
#                     scheduled_hours =round(scheduled_hours +datas.scheduled_hours,2)
#                     timesheet_hours =round(timesheet_hours +datas.timesheet_hours,2)
#
#                 sales_net =self.env['sale.report'].sudo().search([])
#                 sale_date=0
#                 create_date=0
#
#                 sale_data = sales_net.filtered(lambda r:  r.date.strftime('%d-%m-%Y') == c_date)
#                 sale=0
#                 for x in sale_data:
#                     sale=sale+x.price_subtotal
#                 if sale !=0:
#
#                     labour_per =str(round((labour_wages / sale)*100)) +'%'
#
#                 else:
#                     labour_per=0
#
#                 sales=currency + str(sale)
#                 labour_dollar=currency+str(round(labour_wages,2))
#
#                 smph=round(sale/timesheet_hours,2)
#                 smph_formatted=currency+str(smph)
#                 ahr=round(labour_wages/timesheet_hours,2)
#                 ahr_formatted=currency+str(ahr)
#
#                 for datas in c_date_data:
#                     print(datas.create_date.strftime('%d-%m-%Y'),"gggdddddddddddddd")
#                     if datas.create_date.strftime('%d-%m-%Y') in summary_list :
#                         print("hhhikui",datas.create_date.strftime('%d-%m-%Y'))
#                         pass
#                     else:
#                         col =col+1
#                         sheet.set_column(col,col ,15)
#
#
#                         sheet.write(7, col, line.create_date.strftime('%d/%m/%Y'), format_sub_head)
#                         sheet.write(8, col, line.create_date.strftime('%A'), format_sub_head)
#                         sheet.write(9, col, sales, format_h_value)
#                         sheet.write(10, col, labour_dollar, format_h_value)
#                         sheet.write(11, col, labour_per , format_h_value)
#                         sheet.write(12, col, scheduled_hours, format_h_value)
#                         sheet.write(13, col, timesheet_hours, format_h_value)
#                         sheet.write(14, col, smph_formatted, format_h_value)
#                         sheet.write(15, col, ahr_formatted, format_h_value)
#                         summary_list.append(datas.create_date.strftime('%d-%m-%Y'))
#                         print(summary_list,"kkkkkkkkkkk")

