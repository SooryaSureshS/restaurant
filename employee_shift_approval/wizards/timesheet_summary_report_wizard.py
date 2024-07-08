import datetime
from odoo import api, models, fields,_
from collections import OrderedDict
from datetime import date, timedelta
from odoo.exceptions import ValidationError
from datetime import date


class TimesheetSummaryWizard(models.TransientModel):
    _name = 'timesheet.approval.report'

    start_date = fields.Date('Start Date',required=True)
    end_date = fields.Date('End Date',required=True)

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        today = date.today()
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError(_('Start Date cannot be greater than  End Date'))
            if self.start_date > today :
                raise ValidationError(_("Start date cannot be greater than today's date"))
            if self.start_date == today :
                data = self.env['timesheet.approval'].sudo().search([('create_date', '>=', self.start_date),
                                                                     ('create_date', '<=', self.end_date),('state','=','publish')])
                if data:
                    pass
                else:
                    raise ValidationError(_("There is no published timesheet records"))

    def print_report(self):

        return self.env.ref('employee_shift_approval.report_timesheet_summary_based_on_date').report_action(self)

    def _get_report_values(self):
        summary_dict={}
        data = self.env['timesheet.approval'].sudo().search([('create_date', '>=', self.start_date),
                                                             ('create_date', '<=', self.end_date),
                                                             ('state','=','publish')])
        if data:
            for line in data:
                c_date = line.create_date.strftime('%d-%m-%Y')
                c_date_data = data.filtered(lambda r:  r.create_date.strftime('%d-%m-%Y') == c_date)
                labour_wages=0
                scheduled_hours=0
                timesheet_hours=0
                for datas in c_date_data:
                    labour_wages =labour_wages+datas.timesheet_wages
                    scheduled_hours =round(scheduled_hours +datas.scheduled_hours,2)
                    timesheet_hours =round(timesheet_hours +datas.timesheet_hours,2)
                sales_web =self.env['sale.order'].sudo().search([])
                sale_data = sales_web.filtered(lambda r:  r.date_order.strftime('%d-%m-%Y') == c_date)
                sale_website=0
                for x in sale_data:
                    sale_website=sale_website+x.amount_untaxed
                sales_pos_details =self.env['pos.order'].sudo().search([])
                sale_pos_data = sales_pos_details.filtered(lambda r:  r.date_order.strftime('%d-%m-%Y') == c_date)
                sale_pos=0
                for x in sale_pos_data:
                    sale_pos=sale_pos+x.amount_total
                sale=sale_website+sale_pos
                if sale !=0:
                    labour_per =round((labour_wages / sale)*100)
                else:
                    labour_per=0
                smph=round(sale/timesheet_hours,2)
                ahr=round(labour_wages/timesheet_hours,2)
                for datas in c_date_data:
                    rec = datas.create_date.strftime('%d-%m-%Y')
                    if rec in summary_dict:
                       pass
                    else:
                        summary_dict[rec] = [{'date':line.create_date.strftime('%d/%m/%Y'),
                                              'day':line.create_date.strftime('%A'),
                                              'sales_net': sale,
                                              'labour_dollar': labour_wages,
                                              'labour_per': labour_per,
                                              'scheduled_hour': scheduled_hours,
                                              'timesheet_hour': timesheet_hours,
                                              'spmh': smph,
                                              'ahr':ahr
                                              }

                        ]
            counter = 0
            n = 7
            data = []
            data_keys = list(summary_dict.keys())
            while data_keys[counter: counter + n]:
                data_dict = {}
                for key in data_keys[counter: counter + n]:
                    data_dict[key] = summary_dict[key]
                data.append(data_dict)
                counter += n
            return data
        else:
            return []



