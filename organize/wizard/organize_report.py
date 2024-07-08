# -*- coding: utf-8 -*-
from datetime import datetime, date
import pytz
from dateutil import relativedelta
from odoo import api, models, fields, _
from odoo.exceptions import  ValidationError


class OrganizeReport(models.TransientModel):
    _name = "organize.report.wizard"

    from_date = fields.Datetime(string="From Date", readonly=True)
    to_date = fields.Datetime(string="To Date", readonly=True, compute='change_todate')
    change = fields.Boolean()

    @api.onchange('from_date')
    def change_todate(self):
        print(self.from_date)
        self.write({'to_date': self.from_date + relativedelta.relativedelta(days=6)})

    def print_report(self):
        print(self.to_date)
        today = date.today()
        if self.from_date > self.to_date:
            raise ValidationError(_('From date should be less than To Date'))
        return self.env.ref('organize.organize_report_action').report_action(self, data=self.read([])[0])


class OrganizeReportTemplate(models.AbstractModel):
    _name = 'report.organize.organize_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        current_uid = self.env.user
        tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
        start_date = data.get('from_date')
        print('start_date', start_date)
        end_date = data.get('to_date')
        start_date1 = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').astimezone(
                        tz).replace(tzinfo=None)
        end_date1 = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').astimezone(
                        tz).replace(tzinfo=None)
        print(start_date1, end_date1)
        # start_date1 = start_date1 + relativedelta.relativedelta(minutes=60 * 24)
        # end_date1 = end_date1 + relativedelta.relativedelta(minutes=60 * 24)
        r = relativedelta.relativedelta(end_date1, start_date1)
        datas = []
        organize = self.env['organize.slot'].search([('start_datetime', '>=', start_date1),
                                                     ('end_datetime', '<=', end_date1)])
        organize_before_start = self.env['organize.slot'].search([('start_datetime', '<=', start_date1)])
        for org in organize_before_start:
            if org.end_datetime >= start_date1:
                dat = {
                    'emp': org.employee_id.name,
                    'role': org.role_id.name,
                    'allocated_per': round(org.allocated_percentage),
                    'allocated_hou': round(org.allocated_hours),
                    'repeat': org.repeat if org.repeat else 'False',
                    'start_datetime': datetime.strptime(str(org.start_datetime), '%Y-%m-%d %H:%M:%S').astimezone(
                        tz).replace(tzinfo=None),
                    'end_datetime': datetime.strptime(str(org.end_datetime), '%Y-%m-%d %H:%M:%S').astimezone(
                        tz).replace(tzinfo=None),
                }
                datas.append(dat)
        organize_after_start = self.env['organize.slot'].search([('start_datetime', '>=', start_date1)])
        for org in organize_after_start:
            if org.start_datetime <= end_date1 and org.end_datetime > end_date1:
                dat = {
                    'emp': org.employee_id.name,
                    'role': org.role_id.name,
                    'allocated_per': round(org.allocated_percentage),
                    'allocated_hou': round(org.allocated_hours),
                    'repeat': org.repeat if org.repeat else 'False',
                    'start_datetime': datetime.strptime(str(org.start_datetime), '%Y-%m-%d %H:%M:%S').astimezone(
                        tz).replace(tzinfo=None),
                    'end_datetime': datetime.strptime(str(org.end_datetime), '%Y-%m-%d %H:%M:%S').astimezone(
                        tz).replace(tzinfo=None),
                }
                datas.append(dat)

        for org in organize:
            dat = {
                'emp': org.employee_id.name,
                'role': org.role_id.name,
                'allocated_per': round(org.allocated_percentage),
                'allocated_hou': round(org.allocated_hours),
                'repeat': org.repeat if org.repeat else 'False',
                'start_datetime': datetime.strptime(str(org.start_datetime), '%Y-%m-%d %H:%M:%S').astimezone(
                    tz).replace(tzinfo=None),
                'end_datetime': datetime.strptime(str(org.end_datetime), '%Y-%m-%d %H:%M:%S').astimezone(tz).replace(
                    tzinfo=None),
            }
            datas.append(dat)

        return {
            'data': datas,
            'doc_ids': docids,
            'doc_model': 'organize.slot',
            'docs': docids,
            'start_date': datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').astimezone(tz).replace(
                    tzinfo=None).strftime("%m/%d/%Y"),
            'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').astimezone(tz).replace(
                    tzinfo=None).strftime("%m/%d/%Y"),
        }
