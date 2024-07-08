# -*- coding: utf-8 -*-
from odoo.exceptions import Warning
from odoo import models, fields, api, _
from datetime import date
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HrEmployeeContract(models.Model):
    _inherit = 'hr.contract'

    weekly_time_total = fields.Float(compute="grand_total_amount")

    def get_date(self):

        date_today = datetime.now()
        first_week_today = datetime.now() + relativedelta(days=-7)
        dates = {'date_today': date_today, 'first_week_today': first_week_today}
        return dates

    @api.depends('shift_schedule')
    def grand_total_amount(self):
        for rec in self:
            if len(rec.shift_schedule):
                for line in rec.shift_schedule:
                    rec.total_time_shift = sum([line.total_time for line in rec.shift_schedule])
            else:
                rec.total_time_shift = 0

        weekly_time_total = fields.Float(compute="compute_week_time")

        for rec in self:
            total_hours = 0
            week_dates = []
            curr_date = datetime.now() + relativedelta(days=-7)
            while curr_date <= datetime.now():
                week_dates.append(curr_date)
                curr_date += timedelta(days=1)
            for line in rec.shift_schedule:
                dates = [x for x in week_dates if
                         x.date() >= line.start_date and x.date() <= line.end_date and x.date().weekday() <= 4]
                total_hours += len(dates) * line.hr_shift.hours_per_day
            rec.weekly_time_total = total_hours

    @api.onchange('state')
    def change_state(self):
        if self.employee_id:
            if self.state == 'open':
                self.employee_id.write({'availability': False})
