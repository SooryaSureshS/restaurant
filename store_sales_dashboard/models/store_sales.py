# -*- coding: utf-8 -*-
import math
import random
from collections import defaultdict
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import pandas as pd
import pytz
from pytz import utc
from odoo import models, fields, api, _
from odoo.http import request
from odoo.tools import float_utils
from odoo.exceptions import UserError, ValidationError
import time



ROUNDING_FACTOR = 16


class GetStores(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_user_employee_details(self):
        uid = request.session.uid
        data = []
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.now(tz)
        this_week_end = datetime.now(tz).astimezone(tz)
        this_week_start = datetime.now(tz).astimezone(tz) - timedelta(days=7)

        last_week_end = datetime.now(tz).astimezone(tz) - timedelta(days=7)
        last_week_start = datetime.now(tz).astimezone(tz) - timedelta(days=13)

        this_week_sale_data = self.env['sale.order'].sudo().search(
            [('state', '=', 'sale'), ('date_order', '<=', this_week_end),
             ('date_order', '>=', this_week_start)])
        this_week_pos_data = self.env['pos.order'].sudo().search(
            [('state', '=', 'paid'), ('date_order', '<=', this_week_end),
             ('date_order', '>=', this_week_start)])

        this_week_sale_transactions = len(this_week_sale_data)
        this_week_pos_transactions = len(this_week_pos_data)
        this_week_net_sales = 0
        this_week_net_pos = 0
        for i in this_week_sale_data:
            this_week_net_sales += i.amount_untaxed
        for i in this_week_pos_data:
            this_week_net_pos += i.amount_paid

        this_week_total_transactions = this_week_sale_transactions + this_week_pos_transactions
        this_week_total_sales = this_week_net_sales + this_week_net_pos
        this_week_average_sale = 0
        if this_week_total_sales > 0:
            this_week_average_sale = this_week_total_sales / this_week_total_transactions

        last_week_sale_data = self.env['sale.order'].sudo().search(
            [('state', '=', 'sale'), ('date_order', '<=', last_week_end),
             ('date_order', '>=', last_week_start)])
        last_week_pos_data = self.env['pos.order'].sudo().search(
            [('state', '=', 'paid'), ('date_order', '<=', last_week_end),
             ('date_order', '>=', last_week_start)])

        last_week_sale_transactions = len(last_week_sale_data)
        last_week_pos_transactions = len(last_week_pos_data)
        last_week_net_sales = 0
        last_week_net_pos = 0
        for i in last_week_sale_data:
            last_week_net_sales += i.amount_untaxed
        for i in last_week_pos_data:
            last_week_net_pos += i.amount_paid

        last_week_total_transactions = last_week_sale_transactions + last_week_pos_transactions
        last_week_total_sales = last_week_net_sales + last_week_net_pos
        last_week_average_sale = 0
        if last_week_total_sales > 0:
            last_week_average_sale = last_week_total_sales / last_week_total_transactions

        variance = 0
        if this_week_total_sales > last_week_total_sales:
            variance = 1
        elif this_week_total_sales < last_week_total_sales:
            variance = 2

        variance = 0
        if this_week_total_sales > last_week_total_sales:
            variance = 1
        elif this_week_total_sales < last_week_total_sales:
            variance = 2

        company_name = self.env['res.company'].sudo().search([], limit=1)

        date_diff = timedelta(days=1)
        this_week_order_data = []
        last_week_order_data = []
        while this_week_start <= this_week_end:
            this_week_sale_data_graph = self.env['sale.order'].sudo().search(
                [('state', '=', 'sale'), ('date_order', '<=', this_week_start.date()),
                 ('date_order', '>=', this_week_start.date())])
            this_week_pos_data_graph = self.env['pos.order'].sudo().search(
                [('state', '=', 'paid'), ('date_order', '<=', this_week_start.date()),
                 ('date_order', '>=', this_week_start.date())])

            this_week_order_data.append(round(sum([i.amount_untaxed for i in this_week_sale_data_graph]) + sum(
                [i.amount_total for i in this_week_pos_data_graph]), 2))
            this_week_start += date_diff
        while last_week_start <= last_week_end:
            last_week_sale_data_graph = self.env['sale.order'].sudo().search(
                [('state', '=', 'sale'), ('date_order', '<=', last_week_start.date()),
                 ('date_order', '>=', last_week_start.date())])
            last_week_pos_data_graph = self.env['pos.order'].sudo().search(
                [('state', '=', 'paid'), ('date_order', '<=', last_week_start.date()),
                 ('date_order', '>=', last_week_start.date())])
            last_week_order_data.append(round(sum([i.amount_untaxed for i in last_week_sale_data_graph]) + sum(
                [i.amount_total for i in last_week_pos_data_graph]), 2))
            last_week_start += date_diff

        company_dict = []
        company_ids = self.env['res.company'].search([])
        for i in company_ids:
            company_dict.append({'id': i.id, 'name': i.name})
        vals = {
            "company_ids": company_dict,
            # "this_week_total_sales": round(this_week_total_sales, 2),
            # "this_week_total_transactions": this_week_total_transactions,
            # "this_week_average_sale": round(this_week_average_sale, 2),
            # "last_week_total_sales": round(last_week_total_sales, 2),
            # "last_week_total_transactions": last_week_total_transactions,
            # "last_week_average_sale": round(last_week_average_sale, 2),
            "variance": variance,
            "company_name": company_name.name,
            "this_week_order_data_graph": this_week_order_data,
            "last_week_order_data_graph": last_week_order_data,
        }

        return vals

    @api.model
    def get_company_ids(self):
        company_dict = []
        company_ids = self.env['res.company'].sudo().search([])
        for i in company_ids:
            company_dict.append({'id': i.id, 'name': i.name})
        vals = {"company_ids": company_dict}
        return vals
    
    def get_days(self, this_week_start_time, this_week_end_time, day):
        return [this_week_start_time + timedelta(days=x) for x in range((this_week_end_time - this_week_start_time).days + 1) if
                 (this_week_start_time + timedelta(days=x)).weekday() == time.strptime(day, '%A').tm_wday]

    def day_with_time(self, day, time):
        return datetime.strptime(str(day[0].date()) + time, '%Y-%m-%d %H:%M:%S') - timedelta(hours=5,minutes=30)
    
    def day_sales_with_time(self, date_order_frm, date_order_to, all_company_ids):
        return self.env['sale.order'].sudo().search(
            [('state', '=', 'sale'), ('date_order', '<=', date_order_frm),
             ('date_order', '>=', date_order_to), ('company_id', 'in', all_company_ids)])
    
    def day_pos_with_time(self, date_order_frm, date_order_to, all_company_ids):
        return self.env['pos.order'].sudo().search(
            [('state', '=', 'paid'), ('date_order', '<=', date_order_frm),
             ('date_order', '>=', date_order_to), ('company_id', 'in', all_company_ids)])

    def day_with_net_sales(self, day_sales):
        day_net_sales = 0
        for i in day_sales:
            day_net_sales += i.amount_untaxed
        return day_net_sales

    def day_with_net_pos(self, day_pos):
        day_net_pos = 0
        for i in day_pos:
            day_net_pos += i.amount_paid
        return day_net_pos

    @api.model
    def change_date_dashboard(self, date_val, company_ids):
        if not company_ids:
            raise ValidationError(_('Please choose a company'))
        if not date_val:
            raise ValidationError(_('Please choose a date'))
        all_company_ids = []
        list_company_ids = company_ids.split(',')
        if company_ids:
            all_company_ids = [int(x) for x in list_company_ids]
        else:
            all_company_ids = []
        date1 = date_val + " 23:59:59"
        change_date = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
        change_date_time = datetime.strptime(date_val, '%Y-%m-%d')
        uid = request.session.uid
        data = []
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.now(tz)
        this_week_end = change_date.astimezone(tz)
        this_week_start = change_date.astimezone(tz) - timedelta(days=6)

        this_week_start_time = change_date_time.astimezone(tz) - timedelta(days=6)
        this_week_end_time = change_date_time.astimezone(tz)

        last_week_end = change_date.astimezone(tz) - timedelta(days=7)
        last_week_start = change_date.astimezone(tz) - timedelta(days=13)

        this_week_sale_data = self.env['sale.order'].sudo().search(
            [('state', '=', 'sale'), ('date_order', '<=', this_week_end),
             ('date_order', '>=', this_week_start), ('company_id', 'in', all_company_ids)])
        this_week_pos_data = self.env['pos.order'].sudo().search(
            [('state', '=', 'paid'), ('date_order', '<=', this_week_end),
             ('date_order', '>=', this_week_start), ('company_id', 'in', all_company_ids)])

        mondays = self.get_days(this_week_start_time, this_week_end_time, "Monday")
        tuesdays = self.get_days(this_week_start_time, this_week_end_time, "Tuesday")
        wednesdays = self.get_days(this_week_start_time, this_week_end_time, "Wednesday")
        thursdays = self.get_days(this_week_start_time, this_week_end_time, "Thursday")
        fridays = self.get_days(this_week_start_time, this_week_end_time, "Friday")
        saturdays = self.get_days(this_week_start_time, this_week_end_time, "Saturday")
        sundays = self.get_days(this_week_start_time, this_week_end_time, "Sunday")

        monday_9am = self.day_with_time(mondays, " 09:00:00")
        tuesday_9am = self.day_with_time(tuesdays, " 09:00:00")
        wednesday_9am = self.day_with_time(wednesdays, " 09:00:00")
        thursday_9am = self.day_with_time(thursdays, " 09:00:00")
        friday_9am = self.day_with_time(fridays, " 09:00:00")
        saturday_9am = self.day_with_time(saturdays, " 09:00:00")
        sunday_9am = self.day_with_time(sundays, " 09:00:00")

        monday_10am = self.day_with_time(mondays, " 10:00:00")
        tuesday_10am = self.day_with_time(tuesdays, " 10:00:00")
        wednesday_10am = self.day_with_time(wednesdays, " 10:00:00")
        thursday_10am = self.day_with_time(thursdays, " 10:00:00")
        friday_10am = self.day_with_time(fridays, " 10:00:00")
        saturday_10am = self.day_with_time(saturdays, " 10:00:00")
        sunday_10am = self.day_with_time(sundays, " 10:00:00")

        monday_11am = self.day_with_time(mondays, " 11:00:00")
        tuesday_11am = self.day_with_time(tuesdays, " 11:00:00")
        wednesday_11am = self.day_with_time(wednesdays, " 11:00:00")
        thursday_11am = self.day_with_time(thursdays, " 11:00:00")
        friday_11am = self.day_with_time(fridays, " 11:00:00")
        saturday_11am = self.day_with_time(saturdays, " 11:00:00")
        sunday_11am = self.day_with_time(sundays, " 11:00:00")

        monday_12pm = self.day_with_time(mondays, " 12:00:00")
        tuesday_12pm = self.day_with_time(tuesdays, " 12:00:00")
        wednesday_12pm = self.day_with_time(wednesdays, " 12:00:00")
        thursday_12pm = self.day_with_time(thursdays, " 12:00:00")
        friday_12pm = self.day_with_time(fridays, " 12:00:00")
        saturday_12pm = self.day_with_time(saturdays, " 12:00:00")
        sunday_12pm = self.day_with_time(sundays, " 12:00:00")

        monday_1pm = self.day_with_time(mondays, " 13:00:00")
        tuesday_1pm = self.day_with_time(tuesdays, " 13:00:00")
        wednesday_1pm = self.day_with_time(wednesdays, " 13:00:00")
        thursday_1pm = self.day_with_time(thursdays, " 13:00:00")
        friday_1pm = self.day_with_time(fridays, " 13:00:00")
        saturday_1pm = self.day_with_time(saturdays, " 13:00:00")
        sunday_1pm = self.day_with_time(sundays, " 13:00:00")

        monday_2pm = self.day_with_time(mondays, " 14:00:00")
        tuesday_2pm = self.day_with_time(tuesdays, " 14:00:00")
        wednesday_2pm = self.day_with_time(wednesdays, " 14:00:00")
        thursday_2pm = self.day_with_time(thursdays, " 14:00:00")
        friday_2pm = self.day_with_time(fridays, " 14:00:00")
        saturday_2pm = self.day_with_time(saturdays, " 14:00:00")
        sunday_2pm = self.day_with_time(sundays, " 14:00:00")

        monday_3pm = self.day_with_time(mondays, " 15:00:00")
        tuesday_3pm = self.day_with_time(tuesdays, " 15:00:00")
        wednesday_3pm = self.day_with_time(wednesdays, " 15:00:00")
        thursday_3pm = self.day_with_time(thursdays, " 15:00:00")
        friday_3pm = self.day_with_time(fridays, " 15:00:00")
        saturday_3pm = self.day_with_time(saturdays, " 15:00:00")
        sunday_3pm = self.day_with_time(sundays, " 15:00:00")

        monday_4pm = self.day_with_time(mondays, " 16:00:00")
        tuesday_4pm = self.day_with_time(tuesdays, " 16:00:00")
        wednesday_4pm = self.day_with_time(wednesdays, " 16:00:00")
        thursday_4pm = self.day_with_time(thursdays, " 16:00:00")
        friday_4pm = self.day_with_time(fridays, " 16:00:00")
        saturday_4pm = self.day_with_time(saturdays, " 16:00:00")
        sunday_4pm = self.day_with_time(sundays, " 16:00:00")

        monday_5pm = self.day_with_time(mondays, " 17:00:00")
        tuesday_5pm = self.day_with_time(tuesdays, " 17:00:00")
        wednesday_5pm = self.day_with_time(wednesdays, " 17:00:00")
        thursday_5pm = self.day_with_time(thursdays, " 17:00:00")
        friday_5pm = self.day_with_time(fridays, " 17:00:00")
        saturday_5pm = self.day_with_time(saturdays, " 17:00:00")
        sunday_5pm = self.day_with_time(sundays, " 17:00:00")

        monday_6pm = self.day_with_time(mondays, " 18:00:00")
        tuesday_6pm = self.day_with_time(tuesdays, " 18:00:00")
        wednesday_6pm = self.day_with_time(wednesdays, " 18:00:00")
        thursday_6pm = self.day_with_time(thursdays, " 18:00:00")
        friday_6pm = self.day_with_time(fridays, " 18:00:00")
        saturday_6pm = self.day_with_time(saturdays, " 18:00:00")
        sunday_6pm = self.day_with_time(sundays, " 18:00:00")

        monday_7pm = self.day_with_time(mondays, " 19:00:00")
        tuesday_7pm = self.day_with_time(tuesdays, " 19:00:00")
        wednesday_7pm = self.day_with_time(wednesdays, " 19:00:00")
        thursday_7pm = self.day_with_time(thursdays, " 19:00:00")
        friday_7pm = self.day_with_time(fridays, " 19:00:00")
        saturday_7pm = self.day_with_time(saturdays, " 19:00:00")
        sunday_7pm = self.day_with_time(sundays, " 19:00:00")

        monday_8pm = self.day_with_time(mondays, " 20:00:00")
        tuesday_8pm = self.day_with_time(tuesdays, " 20:00:00")
        wednesday_8pm = self.day_with_time(wednesdays, " 20:00:00")
        thursday_8pm = self.day_with_time(thursdays, " 20:00:00")
        friday_8pm = self.day_with_time(fridays, " 20:00:00")
        saturday_8pm = self.day_with_time(saturdays, " 20:00:00")
        sunday_8pm = self.day_with_time(sundays, " 20:00:00")

        monday_9pm = self.day_with_time(mondays, " 21:00:00")
        tuesday_9pm = self.day_with_time(tuesdays, " 21:00:00")
        wednesday_9pm = self.day_with_time(wednesdays, " 21:00:00")
        thursday_9pm = self.day_with_time(thursdays, " 21:00:00")
        friday_9pm = self.day_with_time(fridays, " 21:00:00")
        saturday_9pm = self.day_with_time(saturdays, " 21:00:00")
        sunday_9pm = self.day_with_time(sundays, " 21:00:00")

        monday_10pm = self.day_with_time(mondays, " 22:00:00")
        tuesday_10pm = self.day_with_time(tuesdays, " 22:00:00")
        wednesday_10pm = self.day_with_time(wednesdays, " 22:00:00")
        thursday_10pm = self.day_with_time(thursdays, " 22:00:00")
        friday_10pm = self.day_with_time(fridays, " 22:00:00")
        saturday_10pm = self.day_with_time(saturdays, " 22:00:00")
        sunday_10pm = self.day_with_time(sundays, " 22:00:00")

        monday_11pm = self.day_with_time(mondays, " 23:00:00")
        tuesday_11pm = self.day_with_time(tuesdays, " 23:00:00")
        wednesday_11pm = self.day_with_time(wednesdays, " 23:00:00")
        thursday_11pm = self.day_with_time(thursdays, " 23:00:00")
        friday_11pm = self.day_with_time(fridays, " 23:00:00")
        saturday_11pm = self.day_with_time(saturdays, " 23:00:00")
        sunday_11pm = self.day_with_time(sundays, " 23:00:00")

        # monday sales
        monday_9am_sales = self.day_sales_with_time(monday_10am, monday_9am, all_company_ids)
        monday_9am_pos = self.day_pos_with_time(monday_10am, monday_9am, all_company_ids)
        monday_10am_sales = self.day_sales_with_time(monday_11am, monday_10am, all_company_ids)
        monday_10am_pos = self.day_pos_with_time(monday_11am, monday_10am, all_company_ids)
        monday_11am_sales = self.day_sales_with_time(monday_12pm, monday_11am, all_company_ids)
        monday_11am_pos = self.day_pos_with_time(monday_12pm, monday_11am, all_company_ids)
        monday_12pm_sales = self.day_sales_with_time(monday_1pm, monday_12pm, all_company_ids)
        monday_12pm_pos = self.day_pos_with_time(monday_1pm, monday_12pm, all_company_ids)
        monday_1pm_sales = self.day_sales_with_time(monday_2pm, monday_1pm, all_company_ids)
        monday_1pm_pos = self.day_pos_with_time(monday_2pm, monday_1pm, all_company_ids)
        monday_2pm_sales = self.day_sales_with_time(monday_3pm, monday_2pm, all_company_ids)
        monday_2pm_pos = self.day_pos_with_time(monday_3pm, monday_2pm, all_company_ids)
        monday_3pm_sales = self.day_sales_with_time(monday_4pm, monday_3pm, all_company_ids)
        monday_3pm_pos = self.day_pos_with_time(monday_4pm, monday_3pm, all_company_ids)
        monday_4pm_sales = self.day_sales_with_time(monday_5pm, monday_4pm, all_company_ids)
        monday_4pm_pos = self.day_pos_with_time(monday_5pm, monday_4pm, all_company_ids)
        monday_5pm_sales = self.day_sales_with_time(monday_6pm, monday_5pm, all_company_ids)
        monday_5pm_pos = self.day_pos_with_time(monday_6pm, monday_5pm, all_company_ids)
        monday_6pm_sales = self.day_sales_with_time(monday_7pm, monday_6pm, all_company_ids)
        monday_6pm_pos = self.day_pos_with_time(monday_7pm, monday_6pm, all_company_ids)
        monday_7pm_sales = self.day_sales_with_time(monday_8pm, monday_7pm, all_company_ids)
        monday_7pm_pos = self.day_pos_with_time(monday_8pm, monday_7pm, all_company_ids)
        monday_8pm_sales = self.day_sales_with_time(monday_9pm, monday_8pm, all_company_ids)
        monday_8pm_pos = self.day_pos_with_time(monday_9pm, monday_8pm, all_company_ids)
        monday_9pm_sales = self.day_sales_with_time(monday_10pm, monday_9pm, all_company_ids)
        monday_9pm_pos = self.day_pos_with_time(monday_10pm, monday_9pm, all_company_ids)
        monday_10pm_sales = self.day_sales_with_time(monday_11pm, monday_10pm, all_company_ids)
        monday_10pm_pos = self.day_pos_with_time(monday_11pm, monday_10pm, all_company_ids)

        # tuesdays

        tuesday_9am_sales = self.day_sales_with_time(tuesday_10am, tuesday_9am, all_company_ids)
        tuesday_9am_pos = self.day_pos_with_time(tuesday_10am, tuesday_9am, all_company_ids)
        tuesday_10am_sales = self.day_sales_with_time(tuesday_11am, tuesday_10am, all_company_ids)
        tuesday_10am_pos = self.day_pos_with_time(tuesday_11am, tuesday_10am, all_company_ids)
        tuesday_11am_sales = self.day_sales_with_time(tuesday_12pm, tuesday_11am, all_company_ids)
        tuesday_11am_pos = self.day_pos_with_time(tuesday_12pm, tuesday_11am, all_company_ids)
        tuesday_12pm_sales = self.day_sales_with_time(tuesday_1pm, tuesday_12pm, all_company_ids)
        tuesday_12pm_pos = self.day_pos_with_time(tuesday_1pm, tuesday_12pm, all_company_ids)
        tuesday_1pm_sales = self.day_sales_with_time(tuesday_2pm, tuesday_1pm, all_company_ids)
        tuesday_1pm_pos = self.day_pos_with_time(tuesday_2pm, tuesday_1pm, all_company_ids)
        tuesday_2pm_sales = self.day_sales_with_time(tuesday_3pm, tuesday_2pm, all_company_ids)
        tuesday_2pm_pos = self.day_pos_with_time(tuesday_3pm, tuesday_2pm, all_company_ids)
        tuesday_3pm_sales = self.day_sales_with_time(tuesday_4pm, tuesday_3pm, all_company_ids)
        tuesday_3pm_pos = self.day_pos_with_time(tuesday_4pm, tuesday_3pm, all_company_ids)
        tuesday_4pm_sales = self.day_sales_with_time(tuesday_5pm, tuesday_4pm, all_company_ids)
        tuesday_4pm_pos = self.day_pos_with_time(tuesday_5pm, tuesday_4pm, all_company_ids)
        tuesday_5pm_sales = self.day_sales_with_time(tuesday_6pm, tuesday_5pm, all_company_ids)
        tuesday_5pm_pos = self.day_pos_with_time(tuesday_6pm, tuesday_5pm, all_company_ids)
        tuesday_6pm_sales = self.day_sales_with_time(tuesday_7pm, tuesday_6pm, all_company_ids)
        tuesday_6pm_pos = self.day_pos_with_time(tuesday_7pm, tuesday_6pm, all_company_ids)
        tuesday_7pm_sales = self.day_sales_with_time(tuesday_8pm, tuesday_7pm, all_company_ids)
        tuesday_7pm_pos = self.day_pos_with_time(tuesday_8pm, tuesday_7pm, all_company_ids)
        tuesday_8pm_sales = self.day_sales_with_time(tuesday_9pm, tuesday_8pm, all_company_ids)
        tuesday_8pm_pos = self.day_pos_with_time(tuesday_9pm, tuesday_8pm, all_company_ids)
        tuesday_9pm_sales = self.day_sales_with_time(tuesday_10pm, tuesday_9pm, all_company_ids)
        tuesday_9pm_pos = self.day_pos_with_time(tuesday_10pm, tuesday_9pm, all_company_ids)
        tuesday_10pm_sales = self.day_sales_with_time(tuesday_11pm, tuesday_10pm, all_company_ids)
        tuesday_10pm_pos = self.day_pos_with_time(tuesday_11pm, tuesday_10pm, all_company_ids)

        #wednesday

        wednesday_9am_sales = self.day_sales_with_time(wednesday_10am, wednesday_9am, all_company_ids)
        wednesday_9am_pos = self.day_pos_with_time(wednesday_10am, wednesday_9am, all_company_ids)
        wednesday_10am_sales = self.day_sales_with_time(wednesday_11am, wednesday_10am, all_company_ids)
        wednesday_10am_pos = self.day_pos_with_time(wednesday_11am, wednesday_10am, all_company_ids)
        wednesday_11am_sales = self.day_sales_with_time(wednesday_12pm, wednesday_11am, all_company_ids)
        wednesday_11am_pos = self.day_pos_with_time(wednesday_12pm, wednesday_11am, all_company_ids)
        wednesday_12pm_sales = self.day_sales_with_time(wednesday_1pm, wednesday_12pm, all_company_ids)
        wednesday_12pm_pos = self.day_pos_with_time(wednesday_1pm, wednesday_12pm, all_company_ids)
        wednesday_1pm_sales = self.day_sales_with_time(wednesday_2pm, wednesday_1pm, all_company_ids)
        wednesday_1pm_pos = self.day_pos_with_time(wednesday_2pm, wednesday_1pm, all_company_ids)
        wednesday_2pm_sales = self.day_sales_with_time(wednesday_3pm, wednesday_2pm, all_company_ids)
        wednesday_2pm_pos = self.day_pos_with_time(wednesday_3pm, wednesday_2pm, all_company_ids)
        wednesday_3pm_sales = self.day_sales_with_time(wednesday_4pm, wednesday_3pm, all_company_ids)
        wednesday_3pm_pos = self.day_pos_with_time(wednesday_4pm, wednesday_3pm, all_company_ids)
        wednesday_4pm_sales = self.day_sales_with_time(wednesday_5pm, wednesday_4pm, all_company_ids)
        wednesday_4pm_pos = self.day_pos_with_time(wednesday_5pm, wednesday_4pm, all_company_ids)
        wednesday_5pm_sales = self.day_sales_with_time(wednesday_6pm, wednesday_5pm, all_company_ids)
        wednesday_5pm_pos = self.day_pos_with_time(wednesday_6pm, wednesday_5pm, all_company_ids)
        wednesday_6pm_sales = self.day_sales_with_time(wednesday_7pm, wednesday_6pm, all_company_ids)
        wednesday_6pm_pos = self.day_pos_with_time(wednesday_7pm, wednesday_6pm, all_company_ids)
        wednesday_7pm_sales = self.day_sales_with_time(wednesday_8pm, wednesday_7pm, all_company_ids)
        wednesday_7pm_pos = self.day_pos_with_time(wednesday_8pm, wednesday_7pm, all_company_ids)
        wednesday_8pm_sales = self.day_sales_with_time(wednesday_9pm, wednesday_8pm, all_company_ids)
        wednesday_8pm_pos = self.day_pos_with_time(wednesday_9pm, wednesday_8pm, all_company_ids)
        wednesday_9pm_sales = self.day_sales_with_time(wednesday_10pm, wednesday_9pm, all_company_ids)
        wednesday_9pm_pos = self.day_pos_with_time(wednesday_10pm, wednesday_9pm, all_company_ids)
        wednesday_10pm_sales = self.day_sales_with_time(wednesday_11pm, wednesday_10pm, all_company_ids)
        wednesday_10pm_pos = self.day_pos_with_time(wednesday_11pm, wednesday_10pm, all_company_ids)

        # thursdays

        thursday_9am_sales = self.day_sales_with_time(thursday_10am, thursday_9am, all_company_ids)
        thursday_9am_pos = self.day_pos_with_time(thursday_10am, thursday_9am, all_company_ids)
        thursday_10am_sales = self.day_sales_with_time(thursday_11am, thursday_10am, all_company_ids)
        thursday_10am_pos = self.day_pos_with_time(thursday_11am, thursday_10am, all_company_ids)
        thursday_11am_sales = self.day_sales_with_time(thursday_12pm, thursday_11am, all_company_ids)
        thursday_11am_pos = self.day_pos_with_time(thursday_12pm, thursday_11am, all_company_ids)
        thursday_12pm_sales = self.day_sales_with_time(thursday_1pm, thursday_12pm, all_company_ids)
        thursday_12pm_pos = self.day_pos_with_time(thursday_1pm, thursday_12pm, all_company_ids)
        thursday_1pm_sales = self.day_sales_with_time(thursday_2pm, thursday_1pm, all_company_ids)
        thursday_1pm_pos = self.day_pos_with_time(thursday_2pm, thursday_1pm, all_company_ids)
        thursday_2pm_sales = self.day_sales_with_time(thursday_3pm, thursday_2pm, all_company_ids)
        thursday_2pm_pos = self.day_pos_with_time(thursday_3pm, thursday_2pm, all_company_ids)
        thursday_3pm_sales = self.day_sales_with_time(thursday_4pm, thursday_3pm, all_company_ids)
        thursday_3pm_pos = self.day_pos_with_time(thursday_4pm, thursday_3pm, all_company_ids)
        thursday_4pm_sales = self.day_sales_with_time(thursday_5pm, thursday_4pm, all_company_ids)
        thursday_4pm_pos = self.day_pos_with_time(thursday_5pm, thursday_4pm, all_company_ids)
        thursday_5pm_sales = self.day_sales_with_time(thursday_6pm, thursday_5pm, all_company_ids)
        thursday_5pm_pos = self.day_pos_with_time(thursday_6pm, thursday_5pm, all_company_ids)
        thursday_6pm_sales = self.day_sales_with_time(thursday_7pm, thursday_6pm, all_company_ids)
        thursday_6pm_pos = self.day_pos_with_time(thursday_7pm, thursday_6pm, all_company_ids)
        thursday_7pm_sales = self.day_sales_with_time(thursday_8pm, thursday_7pm, all_company_ids)
        thursday_7pm_pos = self.day_pos_with_time(thursday_8pm, thursday_7pm, all_company_ids)
        thursday_8pm_sales = self.day_sales_with_time(thursday_9pm, thursday_8pm, all_company_ids)
        thursday_8pm_pos = self.day_pos_with_time(thursday_9pm, thursday_8pm, all_company_ids)
        thursday_9pm_sales = self.day_sales_with_time(thursday_10pm, thursday_9pm, all_company_ids)
        thursday_9pm_pos = self.day_pos_with_time(thursday_10pm, thursday_9pm, all_company_ids)
        thursday_10pm_sales = self.day_sales_with_time(thursday_11pm, thursday_10pm, all_company_ids)
        thursday_10pm_pos = self.day_pos_with_time(thursday_11pm, thursday_10pm, all_company_ids)

        # fridays

        friday_9am_sales = self.day_sales_with_time(friday_10am, friday_9am, all_company_ids)
        friday_9am_pos = self.day_pos_with_time(friday_10am, friday_9am, all_company_ids)
        friday_10am_sales = self.day_sales_with_time(friday_11am, friday_10am, all_company_ids)
        friday_10am_pos = self.day_pos_with_time(friday_11am, friday_10am, all_company_ids)
        friday_11am_sales = self.day_sales_with_time(friday_12pm, friday_11am, all_company_ids)
        friday_11am_pos = self.day_pos_with_time(friday_12pm, friday_11am, all_company_ids)
        friday_12pm_sales = self.day_sales_with_time(friday_1pm, friday_12pm, all_company_ids)
        friday_12pm_pos = self.day_pos_with_time(friday_1pm, friday_12pm, all_company_ids)
        friday_1pm_sales = self.day_sales_with_time(friday_2pm, friday_1pm, all_company_ids)
        friday_1pm_pos = self.day_pos_with_time(friday_2pm, friday_1pm, all_company_ids)
        friday_2pm_sales = self.day_sales_with_time(friday_3pm, friday_2pm, all_company_ids)
        friday_2pm_pos = self.day_pos_with_time(friday_3pm, friday_2pm, all_company_ids)
        friday_3pm_sales = self.day_sales_with_time(friday_4pm, friday_3pm, all_company_ids)
        friday_3pm_pos = self.day_pos_with_time(friday_4pm, friday_3pm, all_company_ids)
        friday_4pm_sales = self.day_sales_with_time(friday_5pm, friday_4pm, all_company_ids)
        friday_4pm_pos = self.day_pos_with_time(friday_5pm, friday_4pm, all_company_ids)
        friday_5pm_sales = self.day_sales_with_time(friday_6pm, friday_5pm, all_company_ids)
        friday_5pm_pos = self.day_pos_with_time(friday_6pm, friday_5pm, all_company_ids)
        friday_6pm_sales = self.day_sales_with_time(friday_7pm, friday_6pm, all_company_ids)
        friday_6pm_pos = self.day_pos_with_time(friday_7pm, friday_6pm, all_company_ids)
        friday_7pm_sales = self.day_sales_with_time(friday_8pm, friday_7pm, all_company_ids)
        friday_7pm_pos = self.day_pos_with_time(friday_8pm, friday_7pm, all_company_ids)
        friday_8pm_sales = self.day_sales_with_time(friday_9pm, friday_8pm, all_company_ids)
        friday_8pm_pos = self.day_pos_with_time(friday_9pm, friday_8pm, all_company_ids)
        friday_9pm_sales = self.day_sales_with_time(friday_10pm, friday_9pm, all_company_ids)
        friday_9pm_pos = self.day_pos_with_time(friday_10pm, friday_9pm, all_company_ids)
        friday_10pm_sales = self.day_sales_with_time(friday_11pm, friday_10pm, all_company_ids)
        friday_10pm_pos = self.day_pos_with_time(friday_11pm, friday_10pm, all_company_ids)

        #saturday

        saturday_9am_sales = self.day_sales_with_time(saturday_10am, saturday_9am, all_company_ids)
        saturday_9am_pos = self.day_pos_with_time(saturday_10am, saturday_9am, all_company_ids)
        saturday_10am_sales = self.day_sales_with_time(saturday_11am, saturday_10am, all_company_ids)
        saturday_10am_pos = self.day_pos_with_time(saturday_11am, saturday_10am, all_company_ids)
        saturday_11am_sales = self.day_sales_with_time(saturday_12pm, saturday_11am, all_company_ids)
        saturday_11am_pos = self.day_pos_with_time(saturday_12pm, saturday_11am, all_company_ids)
        saturday_12pm_sales = self.day_sales_with_time(saturday_1pm, saturday_12pm, all_company_ids)
        saturday_12pm_pos = self.day_pos_with_time(saturday_1pm, saturday_12pm, all_company_ids)
        saturday_1pm_sales = self.day_sales_with_time(saturday_2pm, saturday_1pm, all_company_ids)
        saturday_1pm_pos = self.day_pos_with_time(saturday_2pm, saturday_1pm, all_company_ids)
        saturday_2pm_sales = self.day_sales_with_time(saturday_3pm, saturday_2pm, all_company_ids)
        saturday_2pm_pos = self.day_pos_with_time(saturday_3pm, saturday_2pm, all_company_ids)
        saturday_3pm_sales = self.day_sales_with_time(saturday_4pm, saturday_3pm, all_company_ids)
        saturday_3pm_pos = self.day_pos_with_time(saturday_4pm, saturday_3pm, all_company_ids)
        saturday_4pm_sales = self.day_sales_with_time(saturday_5pm, saturday_4pm, all_company_ids)
        saturday_4pm_pos = self.day_pos_with_time(saturday_5pm, saturday_4pm, all_company_ids)
        saturday_5pm_sales = self.day_sales_with_time(saturday_6pm, saturday_5pm, all_company_ids)
        saturday_5pm_pos = self.day_pos_with_time(saturday_6pm, saturday_5pm, all_company_ids)
        saturday_6pm_sales = self.day_sales_with_time(saturday_7pm, saturday_6pm, all_company_ids)
        saturday_6pm_pos = self.day_pos_with_time(saturday_7pm, saturday_6pm, all_company_ids)
        saturday_7pm_sales = self.day_sales_with_time(saturday_8pm, saturday_7pm, all_company_ids)
        saturday_7pm_pos = self.day_pos_with_time(saturday_8pm, saturday_7pm, all_company_ids)
        saturday_8pm_sales = self.day_sales_with_time(saturday_9pm, saturday_8pm, all_company_ids)
        saturday_8pm_pos = self.day_pos_with_time(saturday_9pm, saturday_8pm, all_company_ids)
        saturday_9pm_sales = self.day_sales_with_time(saturday_10pm, saturday_9pm, all_company_ids)
        saturday_9pm_pos = self.day_pos_with_time(saturday_10pm, saturday_9pm, all_company_ids)
        saturday_10pm_sales = self.day_sales_with_time(saturday_11pm, saturday_10pm, all_company_ids)
        saturday_10pm_pos = self.day_pos_with_time(saturday_11pm, saturday_10pm, all_company_ids)

        # sunday

        sunday_9am_sales = self.day_sales_with_time(sunday_10am, sunday_9am, all_company_ids)
        sunday_9am_pos = self.day_pos_with_time(sunday_10am, sunday_9am, all_company_ids)
        sunday_10am_sales = self.day_sales_with_time(sunday_11am, sunday_10am, all_company_ids)
        sunday_10am_pos = self.day_pos_with_time(sunday_11am, sunday_10am, all_company_ids)
        sunday_11am_sales = self.day_sales_with_time(sunday_12pm, sunday_11am, all_company_ids)
        sunday_11am_pos = self.day_pos_with_time(sunday_12pm, sunday_11am, all_company_ids)
        sunday_12pm_sales = self.day_sales_with_time(sunday_1pm, sunday_12pm, all_company_ids)
        sunday_12pm_pos = self.day_pos_with_time(sunday_1pm, sunday_12pm, all_company_ids)
        sunday_1pm_sales = self.day_sales_with_time(sunday_2pm, sunday_1pm, all_company_ids)
        sunday_1pm_pos = self.day_pos_with_time(sunday_2pm, sunday_1pm, all_company_ids)
        sunday_2pm_sales = self.day_sales_with_time(sunday_3pm, sunday_2pm, all_company_ids)
        sunday_2pm_pos = self.day_pos_with_time(sunday_3pm, sunday_2pm, all_company_ids)
        sunday_3pm_sales = self.day_sales_with_time(sunday_4pm, sunday_3pm, all_company_ids)
        sunday_3pm_pos = self.day_pos_with_time(sunday_4pm, sunday_3pm, all_company_ids)
        sunday_4pm_sales = self.day_sales_with_time(sunday_5pm, sunday_4pm, all_company_ids)
        sunday_4pm_pos = self.day_pos_with_time(sunday_5pm, sunday_4pm, all_company_ids)
        sunday_5pm_sales = self.day_sales_with_time(sunday_6pm, sunday_5pm, all_company_ids)
        sunday_5pm_pos = self.day_pos_with_time(sunday_6pm, sunday_5pm, all_company_ids)
        sunday_6pm_sales = self.day_sales_with_time(sunday_7pm, sunday_6pm, all_company_ids)
        sunday_6pm_pos = self.day_pos_with_time(sunday_7pm, sunday_6pm, all_company_ids)
        sunday_7pm_sales = self.day_sales_with_time(sunday_8pm, sunday_7pm, all_company_ids)
        sunday_7pm_pos = self.day_pos_with_time(sunday_8pm, sunday_7pm, all_company_ids)
        sunday_8pm_sales = self.day_sales_with_time(sunday_9pm, sunday_8pm, all_company_ids)
        sunday_8pm_pos = self.day_pos_with_time(sunday_9pm, sunday_8pm, all_company_ids)
        sunday_9pm_sales = self.day_sales_with_time(sunday_10pm, sunday_9pm, all_company_ids)
        sunday_9pm_pos = self.day_pos_with_time(sunday_10pm, sunday_9pm, all_company_ids)
        sunday_10pm_sales = self.day_sales_with_time(sunday_11pm, sunday_10pm, all_company_ids)
        sunday_10pm_pos = self.day_pos_with_time(sunday_11pm, sunday_10pm, all_company_ids)

        print("sunday_9pm_sales", sunday_9pm_sales)


        # mondays

        monday_9am_sale_transactions = len(monday_9am_sales)
        monday_9am_pos_transactions = len(monday_9am_pos)
        monday_9am_sale_net_sales = self.day_with_net_sales(monday_9am_sales)
        monday_9am_pos_net_pos = self.day_with_net_pos(monday_9am_pos)

        monday_10am_sale_transactions = len(monday_10am_sales)
        monday_10am_pos_transactions = len(monday_10am_pos)
        monday_10am_sale_net_sales = self.day_with_net_sales(monday_10am_sales)
        monday_10am_pos_net_pos = self.day_with_net_pos(monday_10am_pos)

        monday_11am_sale_transactions = len(monday_11am_sales)
        monday_11am_pos_transactions = len(monday_11am_pos)
        monday_11am_sale_net_sales = self.day_with_net_sales(monday_11am_sales)
        monday_11am_pos_net_pos = self.day_with_net_pos(monday_11am_pos)

        monday_12pm_sale_transactions = len(monday_12pm_sales)
        monday_12pm_pos_transactions = len(monday_12pm_pos)
        monday_12pm_sale_net_sales = self.day_with_net_sales(monday_12pm_sales)
        monday_12pm_pos_net_pos = self.day_with_net_pos(monday_12pm_pos)

        monday_1pm_sale_transactions = len(monday_1pm_sales)
        monday_1pm_pos_transactions = len(monday_1pm_pos)
        monday_1pm_sale_net_sales = self.day_with_net_sales(monday_1pm_sales)
        monday_1pm_pos_net_pos = self.day_with_net_pos(monday_1pm_pos)

        monday_2pm_sale_transactions = len(monday_2pm_sales)
        monday_2pm_pos_transactions = len(monday_2pm_pos)
        monday_2pm_sale_net_sales = self.day_with_net_sales(monday_2pm_sales)
        monday_2pm_pos_net_pos = self.day_with_net_pos(monday_2pm_pos)

        monday_3pm_sale_transactions = len(monday_3pm_sales)
        monday_3pm_pos_transactions = len(monday_3pm_pos)
        monday_3pm_sale_net_sales = self.day_with_net_sales(monday_3pm_sales)
        monday_3pm_pos_net_pos = self.day_with_net_pos(monday_3pm_pos)

        monday_4pm_sale_transactions = len(monday_4pm_sales)
        monday_4pm_pos_transactions = len(monday_4pm_pos)
        monday_4pm_sale_net_sales = self.day_with_net_sales(monday_4pm_sales)
        monday_4pm_pos_net_pos = self.day_with_net_pos(monday_4pm_pos)

        monday_5pm_sale_transactions = len(monday_5pm_sales)
        monday_5pm_pos_transactions = len(monday_5pm_pos)
        monday_5pm_sale_net_sales = self.day_with_net_sales(monday_5pm_sales)
        monday_5pm_pos_net_pos = self.day_with_net_pos(monday_5pm_pos)

        monday_6pm_sale_transactions = len(monday_6pm_sales)
        monday_6pm_pos_transactions = len(monday_6pm_pos)
        monday_6pm_sale_net_sales = self.day_with_net_sales(monday_6pm_sales)
        monday_6pm_pos_net_pos = self.day_with_net_pos(monday_6pm_pos)

        monday_7pm_sale_transactions = len(monday_7pm_sales)
        monday_7pm_pos_transactions = len(monday_7pm_pos)
        monday_7pm_sale_net_sales = self.day_with_net_sales(monday_7pm_sales)
        monday_7pm_pos_net_pos = self.day_with_net_pos(monday_7pm_pos)

        monday_8pm_sale_transactions = len(monday_8pm_sales)
        monday_8pm_pos_transactions = len(monday_8pm_pos)
        monday_8pm_sale_net_sales = self.day_with_net_sales(monday_8pm_sales)
        monday_8pm_pos_net_pos = self.day_with_net_pos(monday_8pm_pos)

        monday_9pm_sale_transactions = len(monday_9pm_sales)
        monday_9pm_pos_transactions = len(monday_9pm_pos)
        monday_9pm_sale_net_sales = self.day_with_net_sales(monday_9pm_sales)
        monday_9pm_pos_net_pos = self.day_with_net_pos(monday_9pm_pos)

        monday_10pm_sale_transactions = len(monday_10pm_sales)
        monday_10pm_pos_transactions = len(monday_10pm_pos)
        monday_10pm_sale_net_sales = self.day_with_net_sales(monday_10pm_sales)
        monday_10pm_pos_net_pos = self.day_with_net_pos(monday_10pm_pos)


        # tuesdays

        tuesday_9am_sale_transactions = len(tuesday_9am_sales)
        tuesday_9am_pos_transactions = len(tuesday_9am_pos)
        tuesday_9am_sale_net_sales = self.day_with_net_sales(tuesday_9am_sales)
        tuesday_9am_pos_net_pos = self.day_with_net_pos(tuesday_9am_pos)

        tuesday_10am_sale_transactions = len(tuesday_10am_sales)
        tuesday_10am_pos_transactions = len(tuesday_10am_pos)
        tuesday_10am_sale_net_sales = self.day_with_net_sales(tuesday_10am_sales)
        tuesday_10am_pos_net_pos = self.day_with_net_pos(tuesday_10am_pos)

        tuesday_11am_sale_transactions = len(tuesday_11am_sales)
        tuesday_11am_pos_transactions = len(tuesday_11am_pos)
        tuesday_11am_sale_net_sales = self.day_with_net_sales(tuesday_11am_sales)
        tuesday_11am_pos_net_pos = self.day_with_net_pos(tuesday_11am_pos)

        tuesday_12pm_sale_transactions = len(tuesday_12pm_sales)
        tuesday_12pm_pos_transactions = len(tuesday_12pm_pos)
        tuesday_12pm_sale_net_sales = self.day_with_net_sales(tuesday_12pm_sales)
        tuesday_12pm_pos_net_pos = self.day_with_net_pos(tuesday_12pm_pos)

        tuesday_1pm_sale_transactions = len(tuesday_1pm_sales)
        tuesday_1pm_pos_transactions = len(tuesday_1pm_pos)
        tuesday_1pm_sale_net_sales = self.day_with_net_sales(tuesday_1pm_sales)
        tuesday_1pm_pos_net_pos = self.day_with_net_pos(tuesday_1pm_pos)

        tuesday_2pm_sale_transactions = len(tuesday_2pm_sales)
        tuesday_2pm_pos_transactions = len(tuesday_2pm_pos)
        tuesday_2pm_sale_net_sales = self.day_with_net_sales(tuesday_2pm_sales)
        tuesday_2pm_pos_net_pos = self.day_with_net_pos(tuesday_2pm_pos)

        tuesday_3pm_sale_transactions = len(tuesday_3pm_sales)
        tuesday_3pm_pos_transactions = len(tuesday_3pm_pos)
        tuesday_3pm_sale_net_sales = self.day_with_net_sales(tuesday_3pm_sales)
        tuesday_3pm_pos_net_pos = self.day_with_net_pos(tuesday_3pm_pos)

        tuesday_4pm_sale_transactions = len(tuesday_4pm_sales)
        tuesday_4pm_pos_transactions = len(tuesday_4pm_pos)
        tuesday_4pm_sale_net_sales = self.day_with_net_sales(tuesday_4pm_sales)
        tuesday_4pm_pos_net_pos = self.day_with_net_pos(tuesday_4pm_pos)

        tuesday_5pm_sale_transactions = len(tuesday_5pm_sales)
        tuesday_5pm_pos_transactions = len(tuesday_5pm_pos)
        tuesday_5pm_sale_net_sales = self.day_with_net_sales(tuesday_5pm_sales)
        tuesday_5pm_pos_net_pos = self.day_with_net_pos(tuesday_5pm_pos)

        tuesday_6pm_sale_transactions = len(tuesday_6pm_sales)
        tuesday_6pm_pos_transactions = len(tuesday_6pm_pos)
        tuesday_6pm_sale_net_sales = self.day_with_net_sales(tuesday_6pm_sales)
        tuesday_6pm_pos_net_pos = self.day_with_net_pos(tuesday_6pm_pos)

        tuesday_7pm_sale_transactions = len(tuesday_7pm_sales)
        tuesday_7pm_pos_transactions = len(tuesday_7pm_pos)
        tuesday_7pm_sale_net_sales = self.day_with_net_sales(tuesday_7pm_sales)
        tuesday_7pm_pos_net_pos = self.day_with_net_pos(tuesday_7pm_pos)

        tuesday_8pm_sale_transactions = len(tuesday_8pm_sales)
        tuesday_8pm_pos_transactions = len(tuesday_8pm_pos)
        tuesday_8pm_sale_net_sales = self.day_with_net_sales(tuesday_8pm_sales)
        tuesday_8pm_pos_net_pos = self.day_with_net_pos(tuesday_8pm_pos)

        tuesday_9pm_sale_transactions = len(tuesday_9pm_sales)
        tuesday_9pm_pos_transactions = len(tuesday_9pm_pos)
        tuesday_9pm_sale_net_sales = self.day_with_net_sales(tuesday_9pm_sales)
        tuesday_9pm_pos_net_pos = self.day_with_net_pos(tuesday_9pm_pos)

        tuesday_10pm_sale_transactions = len(tuesday_10pm_sales)
        tuesday_10pm_pos_transactions = len(tuesday_10pm_pos)
        tuesday_10pm_sale_net_sales = self.day_with_net_sales(tuesday_10pm_sales)
        tuesday_10pm_pos_net_pos = self.day_with_net_pos(tuesday_10pm_pos)

        # wednesdays

        wednesday_9am_sale_transactions = len(wednesday_9am_sales)
        wednesday_9am_pos_transactions = len(wednesday_9am_pos)
        wednesday_9am_sale_net_sales = self.day_with_net_sales(wednesday_9am_sales)
        wednesday_9am_pos_net_pos = self.day_with_net_pos(wednesday_9am_pos)

        wednesday_10am_sale_transactions = len(wednesday_10am_sales)
        wednesday_10am_pos_transactions = len(wednesday_10am_pos)
        wednesday_10am_sale_net_sales = self.day_with_net_sales(wednesday_10am_sales)
        wednesday_10am_pos_net_pos = self.day_with_net_pos(wednesday_10am_pos)

        wednesday_11am_sale_transactions = len(wednesday_11am_sales)
        wednesday_11am_pos_transactions = len(wednesday_11am_pos)
        wednesday_11am_sale_net_sales = self.day_with_net_sales(wednesday_11am_sales)
        wednesday_11am_pos_net_pos = self.day_with_net_pos(wednesday_11am_pos)

        wednesday_12pm_sale_transactions = len(wednesday_12pm_sales)
        wednesday_12pm_pos_transactions = len(wednesday_12pm_pos)
        wednesday_12pm_sale_net_sales = self.day_with_net_sales(wednesday_12pm_sales)
        wednesday_12pm_pos_net_pos = self.day_with_net_pos(wednesday_12pm_pos)

        wednesday_1pm_sale_transactions = len(wednesday_1pm_sales)
        wednesday_1pm_pos_transactions = len(wednesday_1pm_pos)
        wednesday_1pm_sale_net_sales = self.day_with_net_sales(wednesday_1pm_sales)
        wednesday_1pm_pos_net_pos = self.day_with_net_pos(wednesday_1pm_pos)

        wednesday_2pm_sale_transactions = len(wednesday_2pm_sales)
        wednesday_2pm_pos_transactions = len(wednesday_2pm_pos)
        wednesday_2pm_sale_net_sales = self.day_with_net_sales(wednesday_2pm_sales)
        wednesday_2pm_pos_net_pos = self.day_with_net_pos(wednesday_2pm_pos)

        wednesday_3pm_sale_transactions = len(wednesday_3pm_sales)
        wednesday_3pm_pos_transactions = len(wednesday_3pm_pos)
        wednesday_3pm_sale_net_sales = self.day_with_net_sales(wednesday_3pm_sales)
        wednesday_3pm_pos_net_pos = self.day_with_net_pos(wednesday_3pm_pos)

        wednesday_4pm_sale_transactions = len(wednesday_4pm_sales)
        wednesday_4pm_pos_transactions = len(wednesday_4pm_pos)
        wednesday_4pm_sale_net_sales = self.day_with_net_sales(wednesday_4pm_sales)
        wednesday_4pm_pos_net_pos = self.day_with_net_pos(wednesday_4pm_pos)

        wednesday_5pm_sale_transactions = len(wednesday_5pm_sales)
        wednesday_5pm_pos_transactions = len(wednesday_5pm_pos)
        wednesday_5pm_sale_net_sales = self.day_with_net_sales(wednesday_5pm_sales)
        wednesday_5pm_pos_net_pos = self.day_with_net_pos(wednesday_5pm_pos)

        wednesday_6pm_sale_transactions = len(wednesday_6pm_sales)
        wednesday_6pm_pos_transactions = len(wednesday_6pm_pos)
        wednesday_6pm_sale_net_sales = self.day_with_net_sales(wednesday_6pm_sales)
        wednesday_6pm_pos_net_pos = self.day_with_net_pos(wednesday_6pm_pos)

        wednesday_7pm_sale_transactions = len(wednesday_7pm_sales)
        wednesday_7pm_pos_transactions = len(wednesday_7pm_pos)
        wednesday_7pm_sale_net_sales = self.day_with_net_sales(wednesday_7pm_sales)
        wednesday_7pm_pos_net_pos = self.day_with_net_pos(wednesday_7pm_pos)

        wednesday_8pm_sale_transactions = len(wednesday_8pm_sales)
        wednesday_8pm_pos_transactions = len(wednesday_8pm_pos)
        wednesday_8pm_sale_net_sales = self.day_with_net_sales(wednesday_8pm_sales)
        wednesday_8pm_pos_net_pos = self.day_with_net_pos(wednesday_8pm_pos)

        wednesday_9pm_sale_transactions = len(wednesday_9pm_sales)
        wednesday_9pm_pos_transactions = len(wednesday_9pm_pos)
        wednesday_9pm_sale_net_sales = self.day_with_net_sales(wednesday_9pm_sales)
        wednesday_9pm_pos_net_pos = self.day_with_net_pos(wednesday_9pm_pos)

        wednesday_10pm_sale_transactions = len(wednesday_10pm_sales)
        wednesday_10pm_pos_transactions = len(wednesday_10pm_pos)
        wednesday_10pm_sale_net_sales = self.day_with_net_sales(wednesday_10pm_sales)
        wednesday_10pm_pos_net_pos = self.day_with_net_pos(wednesday_10pm_pos)

        # thursdays
        thursday_9am_sale_transactions = len(thursday_9am_sales)
        thursday_9am_pos_transactions = len(thursday_9am_pos)
        thursday_9am_sale_net_sales = self.day_with_net_sales(thursday_9am_sales)
        thursday_9am_pos_net_pos = self.day_with_net_pos(thursday_9am_pos)

        thursday_10am_sale_transactions = len(thursday_10am_sales)
        thursday_10am_pos_transactions = len(thursday_10am_pos)
        thursday_10am_sale_net_sales = self.day_with_net_sales(thursday_10am_sales)
        thursday_10am_pos_net_pos = self.day_with_net_pos(thursday_10am_pos)

        thursday_11am_sale_transactions = len(thursday_11am_sales)
        thursday_11am_pos_transactions = len(thursday_11am_pos)
        thursday_11am_sale_net_sales = self.day_with_net_sales(thursday_11am_sales)
        thursday_11am_pos_net_pos = self.day_with_net_pos(thursday_11am_pos)

        thursday_12pm_sale_transactions = len(thursday_12pm_sales)
        thursday_12pm_pos_transactions = len(thursday_12pm_pos)
        thursday_12pm_sale_net_sales = self.day_with_net_sales(thursday_12pm_sales)
        thursday_12pm_pos_net_pos = self.day_with_net_pos(thursday_12pm_pos)

        thursday_1pm_sale_transactions = len(thursday_1pm_sales)
        thursday_1pm_pos_transactions = len(thursday_1pm_pos)
        thursday_1pm_sale_net_sales = self.day_with_net_sales(thursday_1pm_sales)
        thursday_1pm_pos_net_pos = self.day_with_net_pos(thursday_1pm_pos)

        thursday_2pm_sale_transactions = len(thursday_2pm_sales)
        thursday_2pm_pos_transactions = len(thursday_2pm_pos)
        thursday_2pm_sale_net_sales = self.day_with_net_sales(thursday_2pm_sales)
        thursday_2pm_pos_net_pos = self.day_with_net_pos(thursday_2pm_pos)

        thursday_3pm_sale_transactions = len(thursday_3pm_sales)
        thursday_3pm_pos_transactions = len(thursday_3pm_pos)
        thursday_3pm_sale_net_sales = self.day_with_net_sales(thursday_3pm_sales)
        thursday_3pm_pos_net_pos = self.day_with_net_pos(thursday_3pm_pos)

        thursday_4pm_sale_transactions = len(thursday_4pm_sales)
        thursday_4pm_pos_transactions = len(thursday_4pm_pos)
        thursday_4pm_sale_net_sales = self.day_with_net_sales(thursday_4pm_sales)
        thursday_4pm_pos_net_pos = self.day_with_net_pos(thursday_4pm_pos)

        thursday_5pm_sale_transactions = len(thursday_5pm_sales)
        thursday_5pm_pos_transactions = len(thursday_5pm_pos)
        thursday_5pm_sale_net_sales = self.day_with_net_sales(thursday_5pm_sales)
        thursday_5pm_pos_net_pos = self.day_with_net_pos(thursday_5pm_pos)

        thursday_6pm_sale_transactions = len(thursday_6pm_sales)
        thursday_6pm_pos_transactions = len(thursday_6pm_pos)
        thursday_6pm_sale_net_sales = self.day_with_net_sales(thursday_6pm_sales)
        thursday_6pm_pos_net_pos = self.day_with_net_pos(thursday_6pm_pos)

        thursday_7pm_sale_transactions = len(thursday_7pm_sales)
        thursday_7pm_pos_transactions = len(thursday_7pm_pos)
        thursday_7pm_sale_net_sales = self.day_with_net_sales(thursday_7pm_sales)
        thursday_7pm_pos_net_pos = self.day_with_net_pos(thursday_7pm_pos)

        thursday_8pm_sale_transactions = len(thursday_8pm_sales)
        thursday_8pm_pos_transactions = len(thursday_8pm_pos)
        thursday_8pm_sale_net_sales = self.day_with_net_sales(thursday_8pm_sales)
        thursday_8pm_pos_net_pos = self.day_with_net_pos(thursday_8pm_pos)

        thursday_9pm_sale_transactions = len(thursday_9pm_sales)
        thursday_9pm_pos_transactions = len(thursday_9pm_pos)
        thursday_9pm_sale_net_sales = self.day_with_net_sales(thursday_9pm_sales)
        thursday_9pm_pos_net_pos = self.day_with_net_pos(thursday_9pm_pos)

        thursday_10pm_sale_transactions = len(thursday_10pm_sales)
        thursday_10pm_pos_transactions = len(thursday_10pm_pos)
        thursday_10pm_sale_net_sales = self.day_with_net_sales(thursday_10pm_sales)
        thursday_10pm_pos_net_pos = self.day_with_net_pos(thursday_10pm_pos)

        friday_9am_sale_transactions = len(friday_9am_sales)
        friday_9am_pos_transactions = len(friday_9am_pos)
        friday_9am_sale_net_sales = self.day_with_net_sales(friday_9am_sales)
        friday_9am_pos_net_pos = self.day_with_net_pos(friday_9am_pos)

        friday_10am_sale_transactions = len(friday_10am_sales)
        friday_10am_pos_transactions = len(friday_10am_pos)
        friday_10am_sale_net_sales = self.day_with_net_sales(friday_10am_sales)
        friday_10am_pos_net_pos = self.day_with_net_pos(friday_10am_pos)

        friday_11am_sale_transactions = len(friday_11am_sales)
        friday_11am_pos_transactions = len(friday_11am_pos)
        friday_11am_sale_net_sales = self.day_with_net_sales(friday_11am_sales)
        friday_11am_pos_net_pos = self.day_with_net_pos(friday_11am_pos)

        friday_12pm_sale_transactions = len(friday_12pm_sales)
        friday_12pm_pos_transactions = len(friday_12pm_pos)
        friday_12pm_sale_net_sales = self.day_with_net_sales(friday_12pm_sales)
        friday_12pm_pos_net_pos = self.day_with_net_pos(friday_12pm_pos)

        friday_1pm_sale_transactions = len(friday_1pm_sales)
        friday_1pm_pos_transactions = len(friday_1pm_pos)
        friday_1pm_sale_net_sales = self.day_with_net_sales(friday_1pm_sales)
        friday_1pm_pos_net_pos = self.day_with_net_pos(friday_1pm_pos)

        friday_2pm_sale_transactions = len(friday_2pm_sales)
        friday_2pm_pos_transactions = len(friday_2pm_pos)
        friday_2pm_sale_net_sales = self.day_with_net_sales(friday_2pm_sales)
        friday_2pm_pos_net_pos = self.day_with_net_pos(friday_2pm_pos)

        friday_3pm_sale_transactions = len(friday_3pm_sales)
        friday_3pm_pos_transactions = len(friday_3pm_pos)
        friday_3pm_sale_net_sales = self.day_with_net_sales(friday_3pm_sales)
        friday_3pm_pos_net_pos = self.day_with_net_pos(friday_3pm_pos)

        friday_4pm_sale_transactions = len(friday_4pm_sales)
        friday_4pm_pos_transactions = len(friday_4pm_pos)
        friday_4pm_sale_net_sales = self.day_with_net_sales(friday_4pm_sales)
        friday_4pm_pos_net_pos = self.day_with_net_pos(friday_4pm_pos)

        friday_5pm_sale_transactions = len(friday_5pm_sales)
        friday_5pm_pos_transactions = len(friday_5pm_pos)
        friday_5pm_sale_net_sales = self.day_with_net_sales(friday_5pm_sales)
        friday_5pm_pos_net_pos = self.day_with_net_pos(friday_5pm_pos)

        friday_6pm_sale_transactions = len(friday_6pm_sales)
        friday_6pm_pos_transactions = len(friday_6pm_pos)
        friday_6pm_sale_net_sales = self.day_with_net_sales(friday_6pm_sales)
        friday_6pm_pos_net_pos = self.day_with_net_pos(friday_6pm_pos)

        friday_7pm_sale_transactions = len(friday_7pm_sales)
        friday_7pm_pos_transactions = len(friday_7pm_pos)
        friday_7pm_sale_net_sales = self.day_with_net_sales(friday_7pm_sales)
        friday_7pm_pos_net_pos = self.day_with_net_pos(friday_7pm_pos)

        friday_8pm_sale_transactions = len(friday_8pm_sales)
        friday_8pm_pos_transactions = len(friday_8pm_pos)
        friday_8pm_sale_net_sales = self.day_with_net_sales(friday_8pm_sales)
        friday_8pm_pos_net_pos = self.day_with_net_pos(friday_8pm_pos)

        friday_9pm_sale_transactions = len(friday_9pm_sales)
        friday_9pm_pos_transactions = len(friday_9pm_pos)
        friday_9pm_sale_net_sales = self.day_with_net_sales(friday_9pm_sales)
        friday_9pm_pos_net_pos = self.day_with_net_pos(friday_9pm_pos)

        friday_10pm_sale_transactions = len(friday_10pm_sales)
        friday_10pm_pos_transactions = len(friday_10pm_pos)
        friday_10pm_sale_net_sales = self.day_with_net_sales(friday_10pm_sales)
        friday_10pm_pos_net_pos = self.day_with_net_pos(friday_10pm_pos)

        this_week_sale_transactions = len(this_week_sale_data)
        this_week_pos_transactions = len(this_week_pos_data)
        this_week_net_sales = 0
        this_week_net_pos = 0

        for i in this_week_sale_data:
            this_week_net_sales += i.amount_untaxed
        for i in this_week_pos_data:
            this_week_net_pos += i.amount_paid

        saturday_9am_sale_transactions = len(saturday_9am_sales)
        saturday_9am_pos_transactions = len(saturday_9am_pos)
        saturday_9am_sale_net_sales = self.day_with_net_sales(saturday_9am_sales)
        saturday_9am_pos_net_pos = self.day_with_net_pos(saturday_9am_pos)

        saturday_10am_sale_transactions = len(saturday_10am_sales)
        saturday_10am_pos_transactions = len(saturday_10am_pos)
        saturday_10am_sale_net_sales = self.day_with_net_sales(saturday_10am_sales)
        saturday_10am_pos_net_pos = self.day_with_net_pos(saturday_10am_pos)

        saturday_11am_sale_transactions = len(saturday_11am_sales)
        saturday_11am_pos_transactions = len(saturday_11am_pos)
        saturday_11am_sale_net_sales = self.day_with_net_sales(saturday_11am_sales)
        saturday_11am_pos_net_pos = self.day_with_net_pos(saturday_11am_pos)

        saturday_12pm_sale_transactions = len(saturday_12pm_sales)
        saturday_12pm_pos_transactions = len(saturday_12pm_pos)
        saturday_12pm_sale_net_sales = self.day_with_net_sales(saturday_12pm_sales)
        saturday_12pm_pos_net_pos = self.day_with_net_pos(saturday_12pm_pos)

        saturday_1pm_sale_transactions = len(saturday_1pm_sales)
        saturday_1pm_pos_transactions = len(saturday_1pm_pos)
        saturday_1pm_sale_net_sales = self.day_with_net_sales(saturday_1pm_sales)
        saturday_1pm_pos_net_pos = self.day_with_net_pos(saturday_1pm_pos)

        saturday_2pm_sale_transactions = len(saturday_2pm_sales)
        saturday_2pm_pos_transactions = len(saturday_2pm_pos)
        saturday_2pm_sale_net_sales = self.day_with_net_sales(saturday_2pm_sales)
        saturday_2pm_pos_net_pos = self.day_with_net_pos(saturday_2pm_pos)

        saturday_3pm_sale_transactions = len(saturday_3pm_sales)
        saturday_3pm_pos_transactions = len(saturday_3pm_pos)
        saturday_3pm_sale_net_sales = self.day_with_net_sales(saturday_3pm_sales)
        saturday_3pm_pos_net_pos = self.day_with_net_pos(saturday_3pm_pos)

        saturday_4pm_sale_transactions = len(saturday_4pm_sales)
        saturday_4pm_pos_transactions = len(saturday_4pm_pos)
        saturday_4pm_sale_net_sales = self.day_with_net_sales(saturday_4pm_sales)
        saturday_4pm_pos_net_pos = self.day_with_net_pos(saturday_4pm_pos)

        saturday_5pm_sale_transactions = len(saturday_5pm_sales)
        saturday_5pm_pos_transactions = len(saturday_5pm_pos)
        saturday_5pm_sale_net_sales = self.day_with_net_sales(saturday_5pm_sales)
        saturday_5pm_pos_net_pos = self.day_with_net_pos(saturday_5pm_pos)

        saturday_6pm_sale_transactions = len(saturday_6pm_sales)
        saturday_6pm_pos_transactions = len(saturday_6pm_pos)
        saturday_6pm_sale_net_sales = self.day_with_net_sales(saturday_6pm_sales)
        saturday_6pm_pos_net_pos = self.day_with_net_pos(saturday_6pm_pos)

        saturday_7pm_sale_transactions = len(saturday_7pm_sales)
        saturday_7pm_pos_transactions = len(saturday_7pm_pos)
        saturday_7pm_sale_net_sales = self.day_with_net_sales(saturday_7pm_sales)
        saturday_7pm_pos_net_pos = self.day_with_net_pos(saturday_7pm_pos)

        saturday_8pm_sale_transactions = len(saturday_8pm_sales)
        saturday_8pm_pos_transactions = len(saturday_8pm_pos)
        saturday_8pm_sale_net_sales = self.day_with_net_sales(saturday_8pm_sales)
        saturday_8pm_pos_net_pos = self.day_with_net_pos(saturday_8pm_pos)

        saturday_9pm_sale_transactions = len(saturday_9pm_sales)
        saturday_9pm_pos_transactions = len(saturday_9pm_pos)
        saturday_9pm_sale_net_sales = self.day_with_net_sales(saturday_9pm_sales)
        saturday_9pm_pos_net_pos = self.day_with_net_pos(saturday_9pm_pos)

        saturday_10pm_sale_transactions = len(saturday_10pm_sales)
        saturday_10pm_pos_transactions = len(saturday_10pm_pos)
        saturday_10pm_sale_net_sales = self.day_with_net_sales(saturday_10pm_sales)
        saturday_10pm_pos_net_pos = self.day_with_net_pos(saturday_10pm_pos)

        # sundays

        sunday_9am_sale_transactions = len(sunday_9am_sales)
        sunday_9am_pos_transactions = len(sunday_9am_pos)
        sunday_9am_sale_net_sales = self.day_with_net_sales(sunday_9am_sales)
        sunday_9am_pos_net_pos = self.day_with_net_pos(sunday_9am_pos)

        sunday_10am_sale_transactions = len(sunday_10am_sales)
        sunday_10am_pos_transactions = len(sunday_10am_pos)
        sunday_10am_sale_net_sales = self.day_with_net_sales(sunday_10am_sales)
        sunday_10am_pos_net_pos = self.day_with_net_pos(sunday_10am_pos)

        sunday_11am_sale_transactions = len(sunday_11am_sales)
        sunday_11am_pos_transactions = len(sunday_11am_pos)
        sunday_11am_sale_net_sales = self.day_with_net_sales(sunday_11am_sales)
        sunday_11am_pos_net_pos = self.day_with_net_pos(sunday_11am_pos)

        sunday_12pm_sale_transactions = len(sunday_12pm_sales)
        sunday_12pm_pos_transactions = len(sunday_12pm_pos)
        sunday_12pm_sale_net_sales = self.day_with_net_sales(sunday_12pm_sales)
        sunday_12pm_pos_net_pos = self.day_with_net_pos(sunday_12pm_pos)

        sunday_1pm_sale_transactions = len(sunday_1pm_sales)
        sunday_1pm_pos_transactions = len(sunday_1pm_pos)
        sunday_1pm_sale_net_sales = self.day_with_net_sales(sunday_1pm_sales)
        sunday_1pm_pos_net_pos = self.day_with_net_pos(sunday_1pm_pos)

        sunday_2pm_sale_transactions = len(sunday_2pm_sales)
        sunday_2pm_pos_transactions = len(sunday_2pm_pos)
        sunday_2pm_sale_net_sales = self.day_with_net_sales(sunday_2pm_sales)
        sunday_2pm_pos_net_pos = self.day_with_net_pos(sunday_2pm_pos)

        sunday_3pm_sale_transactions = len(sunday_3pm_sales)
        sunday_3pm_pos_transactions = len(sunday_3pm_pos)
        sunday_3pm_sale_net_sales = self.day_with_net_sales(sunday_3pm_sales)
        sunday_3pm_pos_net_pos = self.day_with_net_pos(sunday_3pm_pos)

        sunday_4pm_sale_transactions = len(sunday_4pm_sales)
        sunday_4pm_pos_transactions = len(sunday_4pm_pos)
        sunday_4pm_sale_net_sales = self.day_with_net_sales(sunday_4pm_sales)
        sunday_4pm_pos_net_pos = self.day_with_net_pos(sunday_4pm_pos)

        sunday_5pm_sale_transactions = len(sunday_5pm_sales)
        sunday_5pm_pos_transactions = len(sunday_5pm_pos)
        sunday_5pm_sale_net_sales = self.day_with_net_sales(sunday_5pm_sales)
        sunday_5pm_pos_net_pos = self.day_with_net_pos(sunday_5pm_pos)

        sunday_6pm_sale_transactions = len(sunday_6pm_sales)
        sunday_6pm_pos_transactions = len(sunday_6pm_pos)
        sunday_6pm_sale_net_sales = self.day_with_net_sales(sunday_6pm_sales)
        sunday_6pm_pos_net_pos = self.day_with_net_pos(sunday_6pm_pos)

        sunday_7pm_sale_transactions = len(sunday_7pm_sales)
        sunday_7pm_pos_transactions = len(sunday_7pm_pos)
        sunday_7pm_sale_net_sales = self.day_with_net_sales(sunday_7pm_sales)
        sunday_7pm_pos_net_pos = self.day_with_net_pos(sunday_7pm_pos)

        sunday_8pm_sale_transactions = len(sunday_8pm_sales)
        sunday_8pm_pos_transactions = len(sunday_8pm_pos)
        sunday_8pm_sale_net_sales = self.day_with_net_sales(sunday_8pm_sales)
        sunday_8pm_pos_net_pos = self.day_with_net_pos(sunday_8pm_pos)

        sunday_9pm_sale_transactions = len(sunday_9pm_sales)
        sunday_9pm_pos_transactions = len(sunday_9pm_pos)
        sunday_9pm_sale_net_sales = self.day_with_net_sales(sunday_9pm_sales)
        sunday_9pm_pos_net_pos = self.day_with_net_pos(sunday_9pm_pos)

        sunday_10pm_sale_transactions = len(sunday_10pm_sales)
        sunday_10pm_pos_transactions = len(sunday_10pm_pos)
        sunday_10pm_sale_net_sales = self.day_with_net_sales(sunday_10pm_sales)
        sunday_10pm_pos_net_pos = self.day_with_net_pos(sunday_10pm_pos)

        # if time_from and time_to:
        #     for i in time_sale_data:
        #         time_net_sales += i.amount_total
        #     for i in time_pos_data:
        #         time_net_pos += i.amount_paid

        this_week_total_transactions = this_week_sale_transactions + this_week_pos_transactions
        this_week_total_sales = this_week_net_sales + this_week_net_pos
        this_week_average_sale = 0
        if this_week_total_sales > 0:
            this_week_average_sale = this_week_total_sales / this_week_total_transactions

        # if time_from and time_to:
        #     time_total_transactions = time_sale_transactions + time_pos_transactions
        #     time_total_sales = time_net_sales + time_net_pos
        #     time_average_sale = 0
        #     if time_total_sales > 0:
        #         time_average_sale = time_total_sales / time_total_transactions
        # else:
        #     time_total_transactions = 0
        #     time_total_sales = 0
        #     time_average_sale = 0
        last_week_sale_data = self.env['sale.order'].sudo().search(
            [('state', '=', 'sale'), ('date_order', '<=', last_week_end),
             ('date_order', '>=', last_week_start), ('company_id', 'in', all_company_ids)])
        last_week_pos_data = self.env['pos.order'].sudo().search(
            [('state', '=', 'paid'), ('date_order', '<=', last_week_end),
             ('date_order', '>=', last_week_start), ('company_id', 'in', all_company_ids)])

        last_week_sale_transactions = len(last_week_sale_data)
        last_week_pos_transactions = len(last_week_pos_data)
        last_week_net_sales = 0
        last_week_net_pos = 0
        for i in last_week_sale_data:
            last_week_net_sales += i.amount_untaxed
        for i in last_week_pos_data:
            last_week_net_pos += i.amount_paid

        last_week_total_transactions = last_week_sale_transactions + last_week_pos_transactions
        last_week_total_sales = last_week_net_sales + last_week_net_pos
        last_week_average_sale = 0
        if last_week_total_sales > 0:
            last_week_average_sale = last_week_total_sales / last_week_total_transactions
        variance = 0
        if this_week_total_sales > last_week_total_sales:
            variance = 1
        elif this_week_total_sales < last_week_total_sales:
            variance = 2

        variance = 0
        if this_week_total_sales > last_week_total_sales:
            variance = 1
        elif this_week_total_sales < last_week_total_sales:
            variance = 2

        # company_name = self.env['res.company'].sudo().search([('id', '=', company_id)])


        date_diff = timedelta(days=1)
        this_week_order_data = []
        last_week_order_data = []
        while this_week_start <= this_week_end:
            this_week_sale_data_graph = self.env['sale.order'].sudo().search(
                [('state', '=', 'sale'), ('date_order', '<=', this_week_start.date()),
                 ('date_order', '>=', this_week_start.date()), ('company_id', '=', all_company_ids)])
            this_week_pos_data_graph = self.env['pos.order'].sudo().search(
                [('state', '=', 'paid'), ('date_order', '<=', this_week_start.date()),
                 ('date_order', '>=', this_week_start.date()), ('company_id', '=', all_company_ids)])

            this_week_order_data.append(round(sum([i.amount_untaxed for i in this_week_sale_data_graph]) + sum(
                [i.amount_total for i in this_week_pos_data_graph]), 2))
            this_week_start += date_diff
        while last_week_start <= last_week_end:
            last_week_sale_data_graph = self.env['sale.order'].sudo().search(
                [('state', '=', 'sale'), ('date_order', '<=', last_week_start.date()),
                 ('date_order', '>=', last_week_start.date()), ('company_id', '=', all_company_ids)])
            last_week_pos_data_graph = self.env['pos.order'].sudo().search(
                [('state', '=', 'paid'), ('date_order', '<=', last_week_start.date()),
                 ('date_order', '>=', last_week_start.date()), ('company_id', '=', all_company_ids)])
            last_week_order_data.append(round(sum([i.amount_untaxed for i in last_week_sale_data_graph]) + sum(
                [i.amount_total for i in last_week_pos_data_graph]), 2))
            last_week_start += date_diff
        company_dict = []
        company_ids = self.env['res.company'].search([])
        for i in company_ids:
            company_dict.append({'id': i.id, 'name': i.name})
        vals = {
            "company_ids": company_dict,

            "sunday_10pm_sale_transactions": sunday_10pm_sale_transactions + sunday_10pm_pos_transactions,
            "sunday_10pm_total" :round(int(sunday_10pm_sale_net_sales) + int(sunday_10pm_pos_net_pos)),

            "sunday_9pm_sale_transactions": sunday_9pm_sale_transactions + sunday_9pm_pos_transactions,
            "sunday_9pm_total": round(sunday_9pm_sale_net_sales + sunday_9pm_pos_net_pos),

            "sunday_8pm_sale_transactions": sunday_8pm_sale_transactions + sunday_8pm_pos_transactions,
            "sunday_8pm_total": round(sunday_8pm_sale_net_sales + sunday_8pm_pos_net_pos),

            "sunday_7pm_sale_transactions": sunday_7pm_sale_transactions + sunday_7pm_pos_transactions,
            "sunday_7pm_total": round(sunday_7pm_sale_net_sales + sunday_7pm_pos_net_pos),

            "sunday_6pm_sale_transactions": sunday_6pm_sale_transactions + sunday_6pm_pos_transactions,
            "sunday_6pm_total": round(sunday_6pm_sale_net_sales + sunday_6pm_pos_net_pos),

            "sunday_5pm_sale_transactions": sunday_5pm_sale_transactions + sunday_5pm_pos_transactions,
            "sunday_5pm_total": round(sunday_5pm_sale_net_sales + sunday_5pm_pos_net_pos),

            "sunday_4pm_sale_transactions": sunday_4pm_sale_transactions + sunday_4pm_pos_transactions,
            "sunday_4pm_total": round(sunday_4pm_sale_net_sales + sunday_4pm_pos_net_pos),

            "sunday_3pm_sale_transactions": sunday_3pm_sale_transactions + sunday_3pm_pos_transactions,
            "sunday_3pm_total": round(sunday_3pm_sale_net_sales + sunday_3pm_pos_net_pos),

            "sunday_2pm_sale_transactions": sunday_2pm_sale_transactions + sunday_2pm_pos_transactions,
            "sunday_2pm_total": round(sunday_2pm_sale_net_sales + sunday_2pm_pos_net_pos),

            "sunday_1pm_sale_transactions": sunday_1pm_sale_transactions + sunday_1pm_pos_transactions,
            "sunday_1pm_total": round(sunday_1pm_sale_net_sales + sunday_1pm_pos_net_pos),

            "sunday_12pm_sale_transactions": sunday_12pm_sale_transactions + sunday_12pm_pos_transactions,
            "sunday_12pm_total": round(sunday_12pm_sale_net_sales + sunday_12pm_pos_net_pos),

            "sunday_11am_sale_transactions": sunday_11am_sale_transactions + sunday_11am_pos_transactions,
            "sunday_11am_total": round(sunday_11am_sale_net_sales + sunday_11am_pos_net_pos),

            "sunday_10am_sale_transactions": sunday_10am_sale_transactions + sunday_10am_pos_transactions,
            "sunday_10am_total": round(sunday_10am_sale_net_sales + sunday_10am_pos_net_pos),

            "sunday_9am_sale_transactions": sunday_9am_sale_transactions + sunday_9am_pos_transactions,
            "sunday_9am_total": round(sunday_9am_sale_net_sales + sunday_9am_pos_net_pos),

            "net_sales_sunday_count": sunday_10pm_sale_transactions + sunday_10pm_pos_transactions +
                                      sunday_9pm_sale_transactions + sunday_9pm_pos_transactions +
                                      sunday_8pm_sale_transactions + sunday_8pm_pos_transactions +
                                      sunday_7pm_sale_transactions + sunday_7pm_pos_transactions +
                                      sunday_6pm_sale_transactions + sunday_6pm_pos_transactions +
                                      sunday_5pm_sale_transactions + sunday_5pm_pos_transactions +
                                      sunday_4pm_sale_transactions + sunday_4pm_pos_transactions +
                                      sunday_3pm_sale_transactions + sunday_3pm_pos_transactions +
                                      sunday_2pm_sale_transactions + sunday_2pm_pos_transactions +
                                      sunday_1pm_sale_transactions + sunday_1pm_pos_transactions +
                                      sunday_12pm_sale_transactions + sunday_12pm_pos_transactions +
                                      sunday_11am_sale_transactions + sunday_11am_pos_transactions +
                                      sunday_10am_sale_transactions + sunday_10am_pos_transactions +
                                      sunday_9am_sale_transactions + sunday_9am_pos_transactions,

            "net_sales_sunday": round(sunday_10pm_sale_net_sales + sunday_10pm_pos_net_pos) +
                                 round(sunday_9pm_sale_net_sales + sunday_9pm_pos_net_pos) +
                                 round(sunday_8pm_sale_net_sales + sunday_8pm_pos_net_pos) +
                                 round(sunday_7pm_sale_net_sales + sunday_7pm_pos_net_pos) +
                                 round(sunday_6pm_sale_net_sales + sunday_6pm_pos_net_pos) +
                                 round(sunday_5pm_sale_net_sales + sunday_5pm_pos_net_pos) +
                                 round(sunday_4pm_sale_net_sales + sunday_4pm_pos_net_pos)+
                                 round(sunday_3pm_sale_net_sales + sunday_3pm_pos_net_pos)+
                                 round(sunday_2pm_sale_net_sales + sunday_2pm_pos_net_pos)+
                                 round(sunday_1pm_sale_net_sales + sunday_1pm_pos_net_pos)+
                                 round(sunday_12pm_sale_net_sales + sunday_12pm_pos_net_pos)+
                                 round(sunday_11am_sale_net_sales + sunday_11am_pos_net_pos)+
                                 round(sunday_10am_sale_net_sales + sunday_10am_pos_net_pos)+
                                 round(sunday_9am_sale_net_sales + sunday_9am_pos_net_pos),


            "monday_10pm_sale_transactions": monday_10pm_sale_transactions + monday_10pm_pos_transactions,
            "monday_10pm_total": round(monday_10pm_sale_net_sales + monday_10pm_pos_net_pos),

            "monday_9pm_sale_transactions": monday_9pm_sale_transactions + monday_9pm_pos_transactions,
            "monday_9pm_total": round(monday_9pm_sale_net_sales + monday_9pm_pos_net_pos),

            "monday_8pm_sale_transactions": monday_8pm_sale_transactions + monday_8pm_pos_transactions,
            "monday_8pm_total": round(monday_8pm_sale_net_sales + monday_8pm_pos_net_pos),

            "monday_7pm_sale_transactions": monday_7pm_sale_transactions + monday_7pm_pos_transactions,
            "monday_7pm_total": round(monday_7pm_sale_net_sales + monday_7pm_pos_net_pos),

            "monday_6pm_sale_transactions": monday_6pm_sale_transactions + monday_6pm_pos_transactions,
            "monday_6pm_total": round(monday_6pm_sale_net_sales + monday_6pm_pos_net_pos),

            "monday_5pm_sale_transactions": monday_5pm_sale_transactions + monday_5pm_pos_transactions,
            "monday_5pm_total": round(monday_5pm_sale_net_sales + monday_5pm_pos_net_pos),

            "monday_4pm_sale_transactions": monday_4pm_sale_transactions + monday_4pm_pos_transactions,
            "monday_4pm_total": round(monday_4pm_sale_net_sales + monday_4pm_pos_net_pos),

            "monday_3pm_sale_transactions": monday_3pm_sale_transactions + monday_3pm_pos_transactions,
            "monday_3pm_total": round(monday_3pm_sale_net_sales + monday_3pm_pos_net_pos),

            "monday_2pm_sale_transactions": monday_2pm_sale_transactions + monday_2pm_pos_transactions,
            "monday_2pm_total": round(monday_2pm_sale_net_sales + monday_2pm_pos_net_pos),

            "monday_1pm_sale_transactions": monday_1pm_sale_transactions + monday_1pm_pos_transactions,
            "monday_1pm_total": round(monday_1pm_sale_net_sales + monday_1pm_pos_net_pos),

            "monday_12pm_sale_transactions": monday_12pm_sale_transactions + monday_12pm_pos_transactions,
            "monday_12pm_total": round(monday_12pm_sale_net_sales + monday_12pm_pos_net_pos),

            "monday_11am_sale_transactions": monday_11am_sale_transactions + monday_11am_pos_transactions,
            "monday_11am_total": round(monday_11am_sale_net_sales + monday_11am_pos_net_pos),

            "monday_10am_sale_transactions": monday_10am_sale_transactions + monday_10am_pos_transactions,
            "monday_10am_total": round(monday_10am_sale_net_sales + monday_10am_pos_net_pos),

            "monday_9am_sale_transactions": monday_9am_sale_transactions + monday_9am_pos_transactions,
            "monday_9am_total": round(monday_9am_sale_net_sales + monday_9am_pos_net_pos),

            "tuesday_10pm_sale_transactions": tuesday_10pm_sale_transactions + tuesday_10pm_pos_transactions,
            "tuesday_10pm_total": round(tuesday_10pm_sale_net_sales + tuesday_10pm_pos_net_pos),

            "tuesday_9pm_sale_transactions": tuesday_9pm_sale_transactions + tuesday_9pm_pos_transactions,
            "tuesday_9pm_total": round(tuesday_9pm_sale_net_sales + tuesday_9pm_pos_net_pos),

            "tuesday_8pm_sale_transactions": tuesday_8pm_sale_transactions + tuesday_8pm_pos_transactions,
            "tuesday_8pm_total": round(tuesday_8pm_sale_net_sales + tuesday_8pm_pos_net_pos),

            "tuesday_7pm_sale_transactions": tuesday_7pm_sale_transactions + tuesday_7pm_pos_transactions,
            "tuesday_7pm_total": round(tuesday_7pm_sale_net_sales + tuesday_7pm_pos_net_pos),

            "tuesday_6pm_sale_transactions": tuesday_6pm_sale_transactions + tuesday_6pm_pos_transactions,
            "tuesday_6pm_total": round(tuesday_6pm_sale_net_sales + tuesday_6pm_pos_net_pos),

            "tuesday_5pm_sale_transactions": tuesday_5pm_sale_transactions + tuesday_5pm_pos_transactions,
            "tuesday_5pm_total": round(tuesday_5pm_sale_net_sales + tuesday_5pm_pos_net_pos),

            "tuesday_4pm_sale_transactions": tuesday_4pm_sale_transactions + tuesday_4pm_pos_transactions,
            "tuesday_4pm_total": round(tuesday_4pm_sale_net_sales + tuesday_4pm_pos_net_pos),

            "tuesday_3pm_sale_transactions": tuesday_3pm_sale_transactions + tuesday_3pm_pos_transactions,
            "tuesday_3pm_total": round(tuesday_3pm_sale_net_sales + tuesday_3pm_pos_net_pos),

            "tuesday_2pm_sale_transactions": tuesday_2pm_sale_transactions + tuesday_2pm_pos_transactions,
            "tuesday_2pm_total": round(tuesday_2pm_sale_net_sales + tuesday_2pm_pos_net_pos),

            "tuesday_1pm_sale_transactions": tuesday_1pm_sale_transactions + tuesday_1pm_pos_transactions,
            "tuesday_1pm_total": round(tuesday_1pm_sale_net_sales + tuesday_1pm_pos_net_pos),

            "tuesday_12pm_sale_transactions": tuesday_12pm_sale_transactions + tuesday_12pm_pos_transactions,
            "tuesday_12pm_total": round(tuesday_12pm_sale_net_sales + tuesday_12pm_pos_net_pos),

            "tuesday_11am_sale_transactions": tuesday_11am_sale_transactions + tuesday_11am_pos_transactions,
            "tuesday_11am_total": round(tuesday_11am_sale_net_sales + tuesday_11am_pos_net_pos),

            "tuesday_10am_sale_transactions": tuesday_10am_sale_transactions + tuesday_10am_pos_transactions,
            "tuesday_10am_total": round(tuesday_10am_sale_net_sales + tuesday_10am_pos_net_pos),

            "tuesday_9am_sale_transactions": tuesday_9am_sale_transactions + tuesday_9am_pos_transactions,
            "tuesday_9am_total": round(tuesday_9am_sale_net_sales + tuesday_9am_pos_net_pos),

            "wednesday_10pm_sale_transactions": wednesday_10pm_sale_transactions + wednesday_10pm_pos_transactions,
            "wednesday_10pm_total": round(wednesday_10pm_sale_net_sales + wednesday_10pm_pos_net_pos),

            "wednesday_9pm_sale_transactions": wednesday_9pm_sale_transactions + wednesday_9pm_pos_transactions,
            "wednesday_9pm_total": round(wednesday_9pm_sale_net_sales + wednesday_9pm_pos_net_pos),

            "wednesday_8pm_sale_transactions": wednesday_8pm_sale_transactions + wednesday_8pm_pos_transactions,
            "wednesday_8pm_total": round(wednesday_8pm_sale_net_sales + wednesday_8pm_pos_net_pos),

            "wednesday_7pm_sale_transactions": wednesday_7pm_sale_transactions + wednesday_7pm_pos_transactions,
            "wednesday_7pm_total": round(wednesday_7pm_sale_net_sales + wednesday_7pm_pos_net_pos),

            "wednesday_6pm_sale_transactions": wednesday_6pm_sale_transactions + wednesday_6pm_pos_transactions,
            "wednesday_6pm_total": round(wednesday_6pm_sale_net_sales + wednesday_6pm_pos_net_pos),

            "wednesday_5pm_sale_transactions": wednesday_5pm_sale_transactions + wednesday_5pm_pos_transactions,
            "wednesday_5pm_total": round(wednesday_5pm_sale_net_sales + wednesday_5pm_pos_net_pos),

            "wednesday_4pm_sale_transactions": wednesday_4pm_sale_transactions + wednesday_4pm_pos_transactions,
            "wednesday_4pm_total": round(wednesday_4pm_sale_net_sales + wednesday_4pm_pos_net_pos),

            "wednesday_3pm_sale_transactions": wednesday_3pm_sale_transactions + wednesday_3pm_pos_transactions,
            "wednesday_3pm_total": round(wednesday_3pm_sale_net_sales + wednesday_3pm_pos_net_pos),

            "wednesday_2pm_sale_transactions": wednesday_2pm_sale_transactions + wednesday_2pm_pos_transactions,
            "wednesday_2pm_total": round(wednesday_2pm_sale_net_sales + wednesday_2pm_pos_net_pos),

            "wednesday_1pm_sale_transactions": wednesday_1pm_sale_transactions + wednesday_1pm_pos_transactions,
            "wednesday_1pm_total": round(wednesday_1pm_sale_net_sales + wednesday_1pm_pos_net_pos),

            "wednesday_12pm_sale_transactions": wednesday_12pm_sale_transactions + wednesday_12pm_pos_transactions,
            "wednesday_12pm_total": round(wednesday_12pm_sale_net_sales + wednesday_12pm_pos_net_pos),

            "wednesday_11am_sale_transactions": wednesday_11am_sale_transactions + wednesday_11am_pos_transactions,
            "wednesday_11am_total": round(wednesday_11am_sale_net_sales + wednesday_11am_pos_net_pos),

            "wednesday_10am_sale_transactions": wednesday_10am_sale_transactions + wednesday_10am_pos_transactions,
            "wednesday_10am_total": round(wednesday_10am_sale_net_sales + wednesday_10am_pos_net_pos),

            "wednesday_9am_sale_transactions": wednesday_9am_sale_transactions + wednesday_9am_pos_transactions,
            "wednesday_9am_total": round(wednesday_9am_sale_net_sales + wednesday_9am_pos_net_pos),

            "thursday_10pm_sale_transactions": thursday_10pm_sale_transactions + thursday_10pm_pos_transactions,
            "thursday_10pm_total": round(thursday_10pm_sale_net_sales + thursday_10pm_pos_net_pos),

            "thursday_9pm_sale_transactions": thursday_9pm_sale_transactions + thursday_9pm_pos_transactions,
            "thursday_9pm_total": round(thursday_9pm_sale_net_sales + thursday_9pm_pos_net_pos),

            "thursday_8pm_sale_transactions": thursday_8pm_sale_transactions + thursday_8pm_pos_transactions,
            "thursday_8pm_total": round(thursday_8pm_sale_net_sales + thursday_8pm_pos_net_pos),

            "thursday_7pm_sale_transactions": thursday_7pm_sale_transactions + thursday_7pm_pos_transactions,
            "thursday_7pm_total": round(thursday_7pm_sale_net_sales + thursday_7pm_pos_net_pos),

            "thursday_6pm_sale_transactions": thursday_6pm_sale_transactions + thursday_6pm_pos_transactions,
            "thursday_6pm_total": round(thursday_6pm_sale_net_sales + thursday_6pm_pos_net_pos),

            "thursday_5pm_sale_transactions": thursday_5pm_sale_transactions + thursday_5pm_pos_transactions,
            "thursday_5pm_total": round(thursday_5pm_sale_net_sales + thursday_5pm_pos_net_pos),

            "thursday_4pm_sale_transactions": thursday_4pm_sale_transactions + thursday_4pm_pos_transactions,
            "thursday_4pm_total": round(thursday_4pm_sale_net_sales + thursday_4pm_pos_net_pos),

            "thursday_3pm_sale_transactions": thursday_3pm_sale_transactions + thursday_3pm_pos_transactions,
            "thursday_3pm_total": round(thursday_3pm_sale_net_sales + thursday_3pm_pos_net_pos),

            "thursday_2pm_sale_transactions": thursday_2pm_sale_transactions + thursday_2pm_pos_transactions,
            "thursday_2pm_total": round(thursday_2pm_sale_net_sales + thursday_2pm_pos_net_pos),

            "thursday_1pm_sale_transactions": thursday_1pm_sale_transactions + thursday_1pm_pos_transactions,
            "thursday_1pm_total": round(thursday_1pm_sale_net_sales + thursday_1pm_pos_net_pos),

            "thursday_12pm_sale_transactions": thursday_12pm_sale_transactions + thursday_12pm_pos_transactions,
            "thursday_12pm_total": round(thursday_12pm_sale_net_sales + thursday_12pm_pos_net_pos),

            "thursday_11am_sale_transactions": thursday_11am_sale_transactions + thursday_11am_pos_transactions,
            "thursday_11am_total": round(thursday_11am_sale_net_sales + thursday_11am_pos_net_pos),

            "thursday_10am_sale_transactions": thursday_10am_sale_transactions + thursday_10am_pos_transactions,
            "thursday_10am_total": round(thursday_10am_sale_net_sales + thursday_10am_pos_net_pos),

            "thursday_9am_sale_transactions": thursday_9am_sale_transactions + thursday_9am_pos_transactions,
            "thursday_9am_total": round(thursday_9am_sale_net_sales + thursday_9am_pos_net_pos),

            "friday_10pm_sale_transactions": friday_10pm_sale_transactions + friday_10pm_pos_transactions,
            "friday_10pm_total": round(friday_10pm_sale_net_sales + friday_10pm_pos_net_pos),

            "friday_9pm_sale_transactions": friday_9pm_sale_transactions + friday_9pm_pos_transactions,
            "friday_9pm_total": round(friday_9pm_sale_net_sales + friday_9pm_pos_net_pos),

            "friday_8pm_sale_transactions": friday_8pm_sale_transactions + friday_8pm_pos_transactions,
            "friday_8pm_total": round(friday_8pm_sale_net_sales + friday_8pm_pos_net_pos),

            "friday_7pm_sale_transactions": friday_7pm_sale_transactions + friday_7pm_pos_transactions,
            "friday_7pm_total": round(friday_7pm_sale_net_sales + friday_7pm_pos_net_pos),

            "friday_6pm_sale_transactions": friday_6pm_sale_transactions + friday_6pm_pos_transactions,
            "friday_6pm_total": round(friday_6pm_sale_net_sales + friday_6pm_pos_net_pos),

            "friday_5pm_sale_transactions": friday_5pm_sale_transactions + friday_5pm_pos_transactions,
            "friday_5pm_total": round(friday_5pm_sale_net_sales + friday_5pm_pos_net_pos),

            "friday_4pm_sale_transactions": friday_4pm_sale_transactions + friday_4pm_pos_transactions,
            "friday_4pm_total": round(friday_4pm_sale_net_sales + friday_4pm_pos_net_pos),

            "friday_3pm_sale_transactions": friday_3pm_sale_transactions + friday_3pm_pos_transactions,
            "friday_3pm_total": round(friday_3pm_sale_net_sales + friday_3pm_pos_net_pos),

            "friday_2pm_sale_transactions": friday_2pm_sale_transactions + friday_2pm_pos_transactions,
            "friday_2pm_total": round(friday_2pm_sale_net_sales + friday_2pm_pos_net_pos),

            "friday_1pm_sale_transactions": friday_1pm_sale_transactions + friday_1pm_pos_transactions,
            "friday_1pm_total": round(friday_1pm_sale_net_sales + friday_1pm_pos_net_pos),

            "friday_12pm_sale_transactions": friday_12pm_sale_transactions + friday_12pm_pos_transactions,
            "friday_12pm_total": round(friday_12pm_sale_net_sales + friday_12pm_pos_net_pos),

            "friday_11am_sale_transactions": friday_11am_sale_transactions + friday_11am_pos_transactions,
            "friday_11am_total": round(friday_11am_sale_net_sales + friday_11am_pos_net_pos),

            "friday_10am_sale_transactions": friday_10am_sale_transactions + friday_10am_pos_transactions,
            "friday_10am_total": round(friday_10am_sale_net_sales + friday_10am_pos_net_pos),

            "friday_9am_sale_transactions": friday_9am_sale_transactions + friday_9am_pos_transactions,
            "friday_9am_total": round(friday_9am_sale_net_sales + friday_9am_pos_net_pos),

            "saturday_10pm_sale_transactions": saturday_10pm_sale_transactions + saturday_10pm_pos_transactions,
            "saturday_10pm_total": round(saturday_10pm_sale_net_sales + saturday_10pm_pos_net_pos),

            "saturday_9pm_sale_transactions": saturday_9pm_sale_transactions + saturday_9pm_pos_transactions,
            "saturday_9pm_total": round(saturday_9pm_sale_net_sales + saturday_9pm_pos_net_pos),

            "saturday_8pm_sale_transactions": saturday_8pm_sale_transactions + saturday_8pm_pos_transactions,
            "saturday_8pm_total": round(saturday_8pm_sale_net_sales + saturday_8pm_pos_net_pos),

            "saturday_7pm_sale_transactions": saturday_7pm_sale_transactions + saturday_7pm_pos_transactions,
            "saturday_7pm_total": round(saturday_7pm_sale_net_sales + saturday_7pm_pos_net_pos),

            "saturday_6pm_sale_transactions": saturday_6pm_sale_transactions + saturday_6pm_pos_transactions,
            "saturday_6pm_total": round(saturday_6pm_sale_net_sales + saturday_6pm_pos_net_pos),

            "saturday_5pm_sale_transactions": saturday_5pm_sale_transactions + saturday_5pm_pos_transactions,
            "saturday_5pm_total": round(saturday_5pm_sale_net_sales + saturday_5pm_pos_net_pos),

            "saturday_4pm_sale_transactions": saturday_4pm_sale_transactions + saturday_4pm_pos_transactions,
            "saturday_4pm_total": round(saturday_4pm_sale_net_sales + saturday_4pm_pos_net_pos),

            "saturday_3pm_sale_transactions": saturday_3pm_sale_transactions + saturday_3pm_pos_transactions,
            "saturday_3pm_total": round(saturday_3pm_sale_net_sales + saturday_3pm_pos_net_pos),

            "saturday_2pm_sale_transactions": saturday_2pm_sale_transactions + saturday_2pm_pos_transactions,
            "saturday_2pm_total": round(saturday_2pm_sale_net_sales + saturday_2pm_pos_net_pos),

            "saturday_1pm_sale_transactions": saturday_1pm_sale_transactions + saturday_1pm_pos_transactions,
            "saturday_1pm_total": round(saturday_1pm_sale_net_sales + saturday_1pm_pos_net_pos),

            "saturday_12pm_sale_transactions": saturday_12pm_sale_transactions + saturday_12pm_pos_transactions,
            "saturday_12pm_total": round(saturday_12pm_sale_net_sales + saturday_12pm_pos_net_pos),

            "saturday_11am_sale_transactions": saturday_11am_sale_transactions + saturday_11am_pos_transactions,
            "saturday_11am_total": round(saturday_11am_sale_net_sales + saturday_11am_pos_net_pos),

            "saturday_10am_sale_transactions": saturday_10am_sale_transactions + saturday_10am_pos_transactions,
            "saturday_10am_total": round(saturday_10am_sale_net_sales + saturday_10am_pos_net_pos),

            "saturday_9am_sale_transactions": saturday_9am_sale_transactions + saturday_9am_pos_transactions,
            "saturday_9am_total": round(saturday_9am_sale_net_sales + saturday_9am_pos_net_pos),

            "net_sales_monday_count": monday_10pm_sale_transactions + monday_10pm_pos_transactions +
                                      monday_9pm_sale_transactions + monday_9pm_pos_transactions +
                                      monday_8pm_sale_transactions + monday_8pm_pos_transactions +
                                      monday_7pm_sale_transactions + monday_7pm_pos_transactions +
                                      monday_6pm_sale_transactions + monday_6pm_pos_transactions +
                                      monday_5pm_sale_transactions + monday_5pm_pos_transactions +
                                      monday_4pm_sale_transactions + monday_4pm_pos_transactions +
                                      monday_3pm_sale_transactions + monday_3pm_pos_transactions +
                                      monday_2pm_sale_transactions + monday_2pm_pos_transactions +
                                      monday_1pm_sale_transactions + monday_1pm_pos_transactions +
                                      monday_12pm_sale_transactions + monday_12pm_pos_transactions +
                                      monday_11am_sale_transactions + monday_11am_pos_transactions +
                                      monday_10am_sale_transactions + monday_10am_pos_transactions +
                                      monday_9am_sale_transactions + monday_9am_pos_transactions,

            "net_sales_monday": round(monday_10pm_sale_net_sales + monday_10pm_pos_net_pos) +
                                round(monday_9pm_sale_net_sales + monday_9pm_pos_net_pos) +
                                round(monday_8pm_sale_net_sales + monday_8pm_pos_net_pos) +
                                round(monday_7pm_sale_net_sales + monday_7pm_pos_net_pos) +
                                round(monday_6pm_sale_net_sales + monday_6pm_pos_net_pos) +
                                round(monday_5pm_sale_net_sales + monday_5pm_pos_net_pos) +
                                round(monday_4pm_sale_net_sales + monday_4pm_pos_net_pos) +
                                round(monday_3pm_sale_net_sales + monday_3pm_pos_net_pos) +
                                round(monday_2pm_sale_net_sales + monday_2pm_pos_net_pos) +
                                round(monday_1pm_sale_net_sales + monday_1pm_pos_net_pos) +
                                round(monday_12pm_sale_net_sales + monday_12pm_pos_net_pos) +
                                round(monday_11am_sale_net_sales + monday_11am_pos_net_pos) +
                                round(monday_10am_sale_net_sales + monday_10am_pos_net_pos) +
                                round(monday_9am_sale_net_sales + monday_9am_pos_net_pos),

            "net_sales_tuesday_count": tuesday_10pm_sale_transactions + tuesday_10pm_pos_transactions +
                                       tuesday_9pm_sale_transactions + tuesday_9pm_pos_transactions +
                                       tuesday_8pm_sale_transactions + tuesday_8pm_pos_transactions +
                                       tuesday_7pm_sale_transactions + tuesday_7pm_pos_transactions +
                                       tuesday_6pm_sale_transactions + tuesday_6pm_pos_transactions +
                                       tuesday_5pm_sale_transactions + tuesday_5pm_pos_transactions +
                                       tuesday_4pm_sale_transactions + tuesday_4pm_pos_transactions +
                                       tuesday_3pm_sale_transactions + tuesday_3pm_pos_transactions +
                                       tuesday_2pm_sale_transactions + tuesday_2pm_pos_transactions +
                                       tuesday_1pm_sale_transactions + tuesday_1pm_pos_transactions +
                                       tuesday_12pm_sale_transactions + tuesday_12pm_pos_transactions +
                                       tuesday_11am_sale_transactions + tuesday_11am_pos_transactions +
                                       tuesday_10am_sale_transactions + tuesday_10am_pos_transactions +
                                       tuesday_9am_sale_transactions + tuesday_9am_pos_transactions,

            "net_sales_tuesday": round(tuesday_10pm_sale_net_sales + tuesday_10pm_pos_net_pos) +
                                 round(tuesday_9pm_sale_net_sales + tuesday_9pm_pos_net_pos) +
                                 round(tuesday_8pm_sale_net_sales + tuesday_8pm_pos_net_pos) +
                                 round(tuesday_7pm_sale_net_sales + tuesday_7pm_pos_net_pos) +
                                 round(tuesday_6pm_sale_net_sales + tuesday_6pm_pos_net_pos) +
                                 round(tuesday_5pm_sale_net_sales + tuesday_5pm_pos_net_pos) +
                                 round(tuesday_4pm_sale_net_sales + tuesday_4pm_pos_net_pos) +
                                 round(tuesday_3pm_sale_net_sales + tuesday_3pm_pos_net_pos) +
                                 round(tuesday_2pm_sale_net_sales + tuesday_2pm_pos_net_pos) +
                                 round(tuesday_1pm_sale_net_sales + tuesday_1pm_pos_net_pos) +
                                 round(tuesday_12pm_sale_net_sales + tuesday_12pm_pos_net_pos) +
                                 round(tuesday_11am_sale_net_sales + tuesday_11am_pos_net_pos) +
                                 round(tuesday_10am_sale_net_sales + tuesday_10am_pos_net_pos) +
                                 round(tuesday_9am_sale_net_sales + tuesday_9am_pos_net_pos),

            "net_sales_wednesday_count": wednesday_10pm_sale_transactions + wednesday_10pm_pos_transactions +
                                         wednesday_9pm_sale_transactions + wednesday_9pm_pos_transactions +
                                         wednesday_8pm_sale_transactions + wednesday_8pm_pos_transactions +
                                         wednesday_7pm_sale_transactions + wednesday_7pm_pos_transactions +
                                         wednesday_6pm_sale_transactions + wednesday_6pm_pos_transactions +
                                         wednesday_5pm_sale_transactions + wednesday_5pm_pos_transactions +
                                         wednesday_4pm_sale_transactions + wednesday_4pm_pos_transactions +
                                         wednesday_3pm_sale_transactions + wednesday_3pm_pos_transactions +
                                         wednesday_2pm_sale_transactions + wednesday_2pm_pos_transactions +
                                         wednesday_1pm_sale_transactions + wednesday_1pm_pos_transactions +
                                         wednesday_12pm_sale_transactions + wednesday_12pm_pos_transactions +
                                         wednesday_11am_sale_transactions + wednesday_11am_pos_transactions +
                                         wednesday_10am_sale_transactions + wednesday_10am_pos_transactions +
                                         wednesday_9am_sale_transactions + wednesday_9am_pos_transactions,

            "net_sales_wednesday": round(wednesday_10pm_sale_net_sales + wednesday_10pm_pos_net_pos) +
                                   round(wednesday_9pm_sale_net_sales + wednesday_9pm_pos_net_pos) +
                                   round(wednesday_8pm_sale_net_sales + wednesday_8pm_pos_net_pos) +
                                   round(wednesday_7pm_sale_net_sales + wednesday_7pm_pos_net_pos) +
                                   round(wednesday_6pm_sale_net_sales + wednesday_6pm_pos_net_pos) +
                                   round(wednesday_5pm_sale_net_sales + wednesday_5pm_pos_net_pos) +
                                   round(wednesday_4pm_sale_net_sales + wednesday_4pm_pos_net_pos) +
                                   round(wednesday_3pm_sale_net_sales + wednesday_3pm_pos_net_pos) +
                                   round(wednesday_2pm_sale_net_sales + wednesday_2pm_pos_net_pos) +
                                   round(wednesday_1pm_sale_net_sales + wednesday_1pm_pos_net_pos) +
                                   round(wednesday_12pm_sale_net_sales + wednesday_12pm_pos_net_pos) +
                                   round(wednesday_11am_sale_net_sales + wednesday_11am_pos_net_pos) +
                                   round(wednesday_10am_sale_net_sales + wednesday_10am_pos_net_pos) +
                                   round(wednesday_9am_sale_net_sales + wednesday_9am_pos_net_pos),

            "net_sales_thursday_count": thursday_10pm_sale_transactions + thursday_10pm_pos_transactions +
                                        thursday_9pm_sale_transactions + thursday_9pm_pos_transactions +
                                        thursday_8pm_sale_transactions + thursday_8pm_pos_transactions +
                                        thursday_7pm_sale_transactions + thursday_7pm_pos_transactions +
                                        thursday_6pm_sale_transactions + thursday_6pm_pos_transactions +
                                        thursday_5pm_sale_transactions + thursday_5pm_pos_transactions +
                                        thursday_4pm_sale_transactions + thursday_4pm_pos_transactions +
                                        thursday_3pm_sale_transactions + thursday_3pm_pos_transactions +
                                        thursday_2pm_sale_transactions + thursday_2pm_pos_transactions +
                                        thursday_1pm_sale_transactions + thursday_1pm_pos_transactions +
                                        thursday_12pm_sale_transactions + thursday_12pm_pos_transactions +
                                        thursday_11am_sale_transactions + thursday_11am_pos_transactions +
                                        thursday_10am_sale_transactions + thursday_10am_pos_transactions +
                                        thursday_9am_sale_transactions + thursday_9am_pos_transactions,

            "net_sales_thursday": round(thursday_10pm_sale_net_sales + thursday_10pm_pos_net_pos) +
                                  round(thursday_9pm_sale_net_sales + thursday_9pm_pos_net_pos) +
                                  round(thursday_8pm_sale_net_sales + thursday_8pm_pos_net_pos) +
                                  round(thursday_7pm_sale_net_sales + thursday_7pm_pos_net_pos) +
                                  round(thursday_6pm_sale_net_sales + thursday_6pm_pos_net_pos) +
                                  round(thursday_5pm_sale_net_sales + thursday_5pm_pos_net_pos) +
                                  round(thursday_4pm_sale_net_sales + thursday_4pm_pos_net_pos) +
                                  round(thursday_3pm_sale_net_sales + thursday_3pm_pos_net_pos) +
                                  round(thursday_2pm_sale_net_sales + thursday_2pm_pos_net_pos) +
                                  round(thursday_1pm_sale_net_sales + thursday_1pm_pos_net_pos) +
                                  round(thursday_12pm_sale_net_sales + thursday_12pm_pos_net_pos) +
                                  round(thursday_11am_sale_net_sales + thursday_11am_pos_net_pos) +
                                  round(thursday_10am_sale_net_sales + thursday_10am_pos_net_pos) +
                                  round(thursday_9am_sale_net_sales + thursday_9am_pos_net_pos),

            "net_sales_friday_count": friday_10pm_sale_transactions + friday_10pm_pos_transactions +
                                      friday_9pm_sale_transactions + friday_9pm_pos_transactions +
                                      friday_8pm_sale_transactions + friday_8pm_pos_transactions +
                                      friday_7pm_sale_transactions + friday_7pm_pos_transactions +
                                      friday_6pm_sale_transactions + friday_6pm_pos_transactions +
                                      friday_5pm_sale_transactions + friday_5pm_pos_transactions +
                                      friday_4pm_sale_transactions + friday_4pm_pos_transactions +
                                      friday_3pm_sale_transactions + friday_3pm_pos_transactions +
                                      friday_2pm_sale_transactions + friday_2pm_pos_transactions +
                                      friday_1pm_sale_transactions + friday_1pm_pos_transactions +
                                      friday_12pm_sale_transactions + friday_12pm_pos_transactions +
                                      friday_11am_sale_transactions + friday_11am_pos_transactions +
                                      friday_10am_sale_transactions + friday_10am_pos_transactions +
                                      friday_9am_sale_transactions + friday_9am_pos_transactions,

            "net_sales_friday": round(friday_10pm_sale_net_sales + friday_10pm_pos_net_pos) +
                                round(friday_9pm_sale_net_sales + friday_9pm_pos_net_pos) +
                                round(friday_8pm_sale_net_sales + friday_8pm_pos_net_pos) +
                                round(friday_7pm_sale_net_sales + friday_7pm_pos_net_pos) +
                                round(friday_6pm_sale_net_sales + friday_6pm_pos_net_pos) +
                                round(friday_5pm_sale_net_sales + friday_5pm_pos_net_pos) +
                                round(friday_4pm_sale_net_sales + friday_4pm_pos_net_pos) +
                                round(friday_3pm_sale_net_sales + friday_3pm_pos_net_pos) +
                                round(friday_2pm_sale_net_sales + friday_2pm_pos_net_pos) +
                                round(friday_1pm_sale_net_sales + friday_1pm_pos_net_pos) +
                                round(friday_12pm_sale_net_sales + friday_12pm_pos_net_pos) +
                                round(friday_11am_sale_net_sales + friday_11am_pos_net_pos) +
                                round(friday_10am_sale_net_sales + friday_10am_pos_net_pos) +
                                round(friday_9am_sale_net_sales + friday_9am_pos_net_pos),

            "net_sales_saturday_count": saturday_10pm_sale_transactions + saturday_10pm_pos_transactions +
                                        saturday_9pm_sale_transactions + saturday_9pm_pos_transactions +
                                        saturday_8pm_sale_transactions + saturday_8pm_pos_transactions +
                                        saturday_7pm_sale_transactions + saturday_7pm_pos_transactions +
                                        saturday_6pm_sale_transactions + saturday_6pm_pos_transactions +
                                        saturday_5pm_sale_transactions + saturday_5pm_pos_transactions +
                                        saturday_4pm_sale_transactions + saturday_4pm_pos_transactions +
                                        saturday_3pm_sale_transactions + saturday_3pm_pos_transactions +
                                        saturday_2pm_sale_transactions + saturday_2pm_pos_transactions +
                                        saturday_1pm_sale_transactions + saturday_1pm_pos_transactions +
                                        saturday_12pm_sale_transactions + saturday_12pm_pos_transactions +
                                        saturday_11am_sale_transactions + saturday_11am_pos_transactions +
                                        saturday_10am_sale_transactions + saturday_10am_pos_transactions +
                                        saturday_9am_sale_transactions + saturday_9am_pos_transactions,

            "net_sales_saturday": round(saturday_10pm_sale_net_sales + saturday_10pm_pos_net_pos) +
                                  round(saturday_9pm_sale_net_sales + saturday_9pm_pos_net_pos) +
                                  round(saturday_8pm_sale_net_sales + saturday_8pm_pos_net_pos) +
                                  round(saturday_7pm_sale_net_sales + saturday_7pm_pos_net_pos) +
                                  round(saturday_6pm_sale_net_sales + saturday_6pm_pos_net_pos) +
                                  round(saturday_5pm_sale_net_sales + saturday_5pm_pos_net_pos) +
                                  round(saturday_4pm_sale_net_sales + saturday_4pm_pos_net_pos) +
                                  round(saturday_3pm_sale_net_sales + saturday_3pm_pos_net_pos) +
                                  round(saturday_2pm_sale_net_sales + saturday_2pm_pos_net_pos) +
                                  round(saturday_1pm_sale_net_sales + saturday_1pm_pos_net_pos) +
                                  round(saturday_12pm_sale_net_sales + saturday_12pm_pos_net_pos) +
                                  round(saturday_11am_sale_net_sales + saturday_11am_pos_net_pos) +
                                  round(saturday_10am_sale_net_sales + saturday_10am_pos_net_pos) +
                                  round(saturday_9am_sale_net_sales + saturday_9am_pos_net_pos),

            # "company_id": company_name.name,
            "this_week_total_sales": round(this_week_total_sales, 2),
            "this_week_total_transactions": this_week_total_transactions,
            "this_week_average_sale": round(this_week_average_sale, 2),

            "last_week_total_sales": round(last_week_total_sales, 2),
            "last_week_total_transactions": last_week_total_transactions,
            "last_week_average_sale": round(last_week_average_sale, 2),
            "variance": variance,
            # "company_name": company_name.name,
            "date_val": date_val,
            "date_val1": datetime.strptime(date_val, '%Y-%m-%d').strftime('%d/%m/%Y'),
            "this_week_order_data_graph": this_week_order_data,
            "last_week_order_data_graph": last_week_order_data,
        }
        return vals

    @api.model
    def get_order_report_values(self):
        uid = request.session.uid
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.utcnow()
        now = datetime.utcnow()
        utc = pytz.timezone('UTC')
        utc.localize(datetime.now())
        delta = utc.localize(now) - tz.localize(now)
        sec = delta.seconds
        total_minute = sec / 60
        order_time = today - timedelta(minutes=total_minute)
        order_time = order_time.replace(tzinfo=None)
        order_time = order_time.replace(microsecond=0)

        start_date = order_time
        end_date = order_time
        domain = [('date_order', '>=', start_date),
                  ('state', 'in', ['paid', 'done', 'invoiced'])]
        sale_domain = [('date_order', '>=', start_date), ('state', '=', 'sale')]
        sale_order = self.env['sale.order'].search(sale_domain)
        sale_order_obj = self.env['sale.order']
        pos_order = self.env['pos.order'].search(domain)
        pos_order_obj = self.env['pos.order']

        if sale_order or pos_order:
            pass
        else:
            uber_vals_dict = {'count': 0, 'amount': 0}
            menulog_vals_dict = {'count': 0, 'amount': 0}
            deliveroo_vals_dict = {'count': 0, 'amount': 0}
            door_dash_vals_dict = {'count': 0, 'amount': 0}
            total_amount = 0
            uber_vals_dict['percentage'] = 0
            menulog_vals_dict['percentage'] = 0
            deliveroo_vals_dict['percentage'] = 0
            door_dash_vals_dict['percentage'] = 0
            data = {'uber': uber_vals_dict, 'menulog': menulog_vals_dict, 'deliveroo': deliveroo_vals_dict,
                    'door_dash': door_dash_vals_dict, 'no_order': {'count': 0, 'amount': 0, 'percentage': 100}}
            return {'data': data}

        uber_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('ubereats') if r.friendly_id else  sale_order_obj)
        door_dash_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('doordash') if r.friendly_id else  sale_order_obj)
        menulog_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('menulog') if r.friendly_id else  sale_order_obj)
        deliveroo_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('deliveroo-web') if r.friendly_id else  sale_order_obj)
        # dine_in_sale = sale_order.filtered(lambda r: r.website_delivery_type == 'dine_in') or sale_order_obj
        # takeaway_sale = sale_order.filtered(lambda r: r.website_delivery_type == 'takeaway') or sale_order_obj

        uber_pos = pos_order.filtered(lambda r: r.delivery_type == 'uber') or pos_order_obj
        door_dash_pos = pos_order.filtered(lambda r: r.delivery_type == 'door') or pos_order_obj
        menulog_pos = pos_order.filtered(lambda r: r.delivery_type == 'menulog') or pos_order_obj
        deliveroo_pos = pos_order.filtered(lambda r: r.delivery_type == 'deliveroo') or pos_order_obj

        if uber_sale or menulog_sale or deliveroo_sale or door_dash_sale or uber_pos or menulog_pos or deliveroo_pos or door_dash_pos:
            uber_vals_dict = {'count': len(uber_sale) + len(uber_pos),
                              'amount': sum([i.amount_untaxed for i in uber_sale]) + sum(
                                  [pos.amount_total for pos in uber_pos])}
            menulog_vals_dict = {'count': len(menulog_sale) + len(menulog_pos),
                                 'amount': sum([i.amount_untaxed for i in menulog_sale]) + sum(
                                     [pos.amount_total for pos in menulog_pos])}
            deliveroo_vals_dict = {'count': len(deliveroo_sale) + len(deliveroo_pos),
                                   'amount': sum([i.amount_untaxed for i in deliveroo_sale]) + sum(
                                       [pos.amount_total for pos in deliveroo_pos])}
            door_dash_vals_dict = {'count': len(door_dash_sale) + len(door_dash_pos),
                                   'amount': sum([i.amount_untaxed for i in door_dash_sale]) + sum(
                                       [pos.amount_total for pos in door_dash_pos])}

            total_amount = uber_vals_dict.get('amount', 0) + menulog_vals_dict.get('amount',
                                                                                   0) + deliveroo_vals_dict.get(
                'amount', 0) + door_dash_vals_dict.get('amount', 0)
            uber_vals_dict['percentage'] = round((uber_vals_dict.get('amount', 0) / total_amount) * 100)
            menulog_vals_dict['percentage'] = round((menulog_vals_dict.get('amount', 0) / total_amount) * 100)
            deliveroo_vals_dict['percentage'] = round((deliveroo_vals_dict.get('amount', 0) / total_amount) * 100)
            door_dash_vals_dict['percentage'] = round((door_dash_vals_dict.get('amount', 0) / total_amount) * 100)
            data = {'uber': uber_vals_dict, 'menulog': menulog_vals_dict, 'deliveroo': deliveroo_vals_dict,
                    'door_dash': door_dash_vals_dict, 'no_order': {'count': 0, 'amount': 0, 'percentage': 0}}

            return {'data': data}
        else:
            uber_vals_dict = {'count': 0, 'amount': 0}
            menulog_vals_dict = {'count': 0, 'amount': 0}
            deliveroo_vals_dict = {'count': 0, 'amount': 0}
            door_dash_vals_dict = {'count': 0, 'amount': 0}
            total_amount = 0
            uber_vals_dict['percentage'] = 0
            menulog_vals_dict['percentage'] = 0
            deliveroo_vals_dict['percentage'] = 0
            door_dash_vals_dict['percentage'] = 0
            data = {'uber': uber_vals_dict, 'menulog': menulog_vals_dict, 'deliveroo': deliveroo_vals_dict,
                    'door_dash': door_dash_vals_dict, 'no_order': {'count': 0, 'amount': 0, 'percentage': 100}}
            return {'data': data}

    @api.model
    def get_order_report_change_date(self, start_date, end_date):
        uid = request.session.uid
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.utcnow()
        start_date = start_date
        end_date = end_date
        domain = [('date_order', '>=', start_date), ('date_order', '<=', end_date),
                  ('state', 'in', ['paid', 'done', 'invoiced'])]
        sale_domain = [('date_order', '>=', start_date), ('date_order', '<=', end_date), ('state', '=', 'sale')]
        sale_order = self.env['sale.order'].search(sale_domain)
        sale_order_obj = self.env['sale.order']
        pos_order = self.env['pos.order'].search(domain)
        pos_order_obj = self.env['pos.order']

        if sale_order or pos_order:
            pass
        else:
            uber_vals_dict = {'count': 0, 'amount': 0}
            menulog_vals_dict = {'count': 0, 'amount': 0}
            deliveroo_vals_dict = {'count': 0, 'amount': 0}
            door_dash_vals_dict = {'count': 0, 'amount': 0}
            total_amount = 0
            uber_vals_dict['percentage'] = 0
            menulog_vals_dict['percentage'] = 0
            deliveroo_vals_dict['percentage'] = 0
            door_dash_vals_dict['percentage'] = 0
            data = {'uber': uber_vals_dict, 'menulog': menulog_vals_dict, 'deliveroo': deliveroo_vals_dict,
                    'door_dash': door_dash_vals_dict, 'no_order': {'count': 0, 'amount': 0, 'percentage': 100}}
            return {'data': data, 'start_date': start_date, 'end_date': end_date}

        uber_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('ubereats') if r.friendly_id else  sale_order_obj)
        door_dash_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('doordash') if r.friendly_id else  sale_order_obj)
        menulog_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('menulog') if r.friendly_id else  sale_order_obj)
        deliveroo_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('deliveroo-web') if r.friendly_id else  sale_order_obj)
        dine_in_sale = sale_order.filtered(lambda r: r.website_delivery_type == 'dine_in') or sale_order_obj
        takeaway_sale = sale_order.filtered(lambda r: r.website_delivery_type == 'takeaway') or sale_order_obj

        uber_pos = pos_order.filtered(lambda r: r.delivery_type == 'uber') or pos_order_obj
        door_dash_pos = pos_order.filtered(lambda r: r.delivery_type == 'door') or pos_order_obj
        menulog_pos = pos_order.filtered(lambda r: r.delivery_type == 'menulog') or pos_order_obj
        deliveroo_pos = pos_order.filtered(lambda r: r.delivery_type == 'deliveroo') or pos_order_obj

        if uber_sale or menulog_sale or deliveroo_sale or door_dash_sale or uber_pos or menulog_pos or deliveroo_pos or door_dash_pos:
            uber_vals_dict = {'count': len(uber_sale) + len(uber_pos),
                              'amount': round(sum([i.amount_untaxed for i in uber_sale]) + sum(
                                  [pos.amount_total for pos in uber_pos]))}
            menulog_vals_dict = {'count': len(menulog_sale) + len(menulog_pos),
                                 'amount': round(sum([i.amount_untaxed for i in menulog_sale]) + sum(
                                     [pos.amount_total for pos in menulog_pos]))}
            deliveroo_vals_dict = {'count': len(deliveroo_sale) + len(deliveroo_pos),
                                   'amount': round(sum([i.amount_untaxed for i in deliveroo_sale]) + sum(
                                       [pos.amount_total for pos in deliveroo_pos]))}
            door_dash_vals_dict = {'count': len(door_dash_sale) + len(door_dash_pos),
                                   'amount': round(sum([i.amount_untaxed for i in door_dash_sale]) + sum(
                                       [pos.amount_total for pos in door_dash_pos]))}

            total_amount = uber_vals_dict.get('amount', 0) + menulog_vals_dict.get('amount',
                                                                                   0) + deliveroo_vals_dict.get(
                'amount', 0) + door_dash_vals_dict.get('amount', 0)
            uber_vals_dict['percentage'] = round((uber_vals_dict.get('amount', 0) / total_amount) * 100)
            menulog_vals_dict['percentage'] = round((menulog_vals_dict.get('amount', 0) / total_amount) * 100)
            deliveroo_vals_dict['percentage'] = round((deliveroo_vals_dict.get('amount', 0) / total_amount) * 100)
            door_dash_vals_dict['percentage'] = round((door_dash_vals_dict.get('amount', 0) / total_amount) * 100)
            data = {'uber': uber_vals_dict, 'menulog': menulog_vals_dict, 'deliveroo': deliveroo_vals_dict,
                    'door_dash': door_dash_vals_dict, 'no_order': {'count': 0, 'amount': 0, 'percentage': 0}}

            return {'data': data, 'start_date': start_date, 'end_date': end_date}
        else:
            uber_vals_dict = {'count': 0, 'amount': 0}
            menulog_vals_dict = {'count': 0, 'amount': 0}
            deliveroo_vals_dict = {'count': 0, 'amount': 0}
            door_dash_vals_dict = {'count': 0, 'amount': 0}
            total_amount = 0
            uber_vals_dict['percentage'] = 0
            menulog_vals_dict['percentage'] = 0
            deliveroo_vals_dict['percentage'] = 0
            door_dash_vals_dict['percentage'] = 0
            data = {'uber': uber_vals_dict, 'menulog': menulog_vals_dict, 'deliveroo': deliveroo_vals_dict,
                    'door_dash': door_dash_vals_dict, 'no_order': {'count': 0, 'amount': 0, 'percentage': 100}}
            return {'data': data, 'start_date': start_date, 'end_date': end_date}

    @api.model
    def get_top_selling_values(self):
        uid = request.session.uid
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.utcnow()
        now = datetime.utcnow()
        utc = pytz.timezone('UTC')
        utc.localize(datetime.now())
        delta = utc.localize(now) - tz.localize(now)
        sec = delta.seconds
        total_minute = sec / 60
        order_time = today - timedelta(minutes=total_minute)
        order_time = order_time.replace(tzinfo=None)
        order_time = order_time.replace(microsecond=0)
        start_date = order_time

        sale_order_data = self.env['sale.order.line'].sudo().search(
            [('order_id.date_order', '>=', start_date), ('order_id.state', '=', 'sale'),
             ('product_id.type', '!=', 'service')])
        pos_order_data = self.env['pos.order.line'].sudo().search(
            [('order_id.date_order', '>=', start_date), ('order_id.state', '=', 'paid'),
             ('product_id.type', '!=', 'service')])
        products = {}
        total_qty = sum([i.product_uom_qty for i in sale_order_data]) + sum([i.qty for i in pos_order_data])
        mapped_products = sale_order_data.mapped('product_id')
        for sale_pro in mapped_products:
            product = sale_order_data.filtered(lambda r: r.product_id.id == sale_pro.id)
            sale_qty = sum([i.product_uom_qty for i in product])
            data = {'product_uom_qty': sale_qty, 'name': sale_pro.name,
                    'amount': round(sum([i.price_total for i in product]), 2),
                    'percentage': round((sale_qty / total_qty) * 100, 2)
                    }
            products[sale_pro.id] = data

        pos_mapped_products = pos_order_data.mapped('product_id')
        sale_added_products = products.keys()
        for sale_pro in pos_mapped_products:
            product = pos_order_data.filtered(lambda r: r.product_id.id == sale_pro.id)
            pos_qty = sum([i.qty for i in product])

            if sale_pro.id in sale_added_products:
                sale_dict = products.get(sale_pro.id)
                sale_dict['product_uom_qty'] = sale_dict.get('product_uom_qty') + pos_qty
                sale_dict['amount'] = round(sale_dict.get('amount') + sum([i.price_subtotal_incl for i in product]), 2)
                sale_dict['percentage'] = round((sale_dict.get('product_uom_qty') + pos_qty / total_qty) * 100, 2)
                sale_dict['cogs'] = round(sale_pro.list_price, 2)
            else:
                data = {'product_uom_qty': pos_qty, 'name': sale_pro.name,
                        'amount': round(sum([i.price_subtotal_incl for i in product]), 2),
                        'percentage': round((pos_qty / total_qty) * 100, 2),
                        'cogs': round(sale_pro.list_price, 2)
                        }
                products[sale_pro.id] = data

        sorted_products1 = sorted(products.items(), key=lambda k: k[1]['product_uom_qty'], reverse=True)
        if len(sorted_products1) > 10:
            sorted_products = sorted_products1[0:9]
        else:
            sorted_products = sorted_products1
        return {"data": sorted_products}

    @api.model
    def get_top_selling_values_date_change(self, start_date, end_date):
        uid = request.session.uid
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.utcnow()

        start_date_str = start_date + " 00:00:00"
        end_date_str = end_date + " 00:00:00"
        start_date_val = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
        end_date_val = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
        uid = request.session.uid
        data = []
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.now(tz)
        start_date_obj = start_date_val.astimezone(tz)
        end_date_obj = end_date_val.astimezone(tz)

        sale_order_data = self.env['sale.order.line'].sudo().search(
            [('order_id.date_order', '>=', start_date_obj), ('order_id.date_order', '<=', end_date_obj),
             ('order_id.state', '=', 'sale'),
             ('product_id.type', '!=', 'service')])
        pos_order_data = self.env['pos.order.line'].sudo().search(
            [('order_id.date_order', '>=', start_date_obj), ('order_id.date_order', '<=', end_date_obj),
             ('order_id.state', '=', 'paid'),
             ('product_id.type', '!=', 'service')])
        # print("XXXXXXXX", sale_order_data)
        # print("ZZZZZZZZ", pos_order_data)
        products = {}
        total_qty = sum([i.product_uom_qty for i in sale_order_data]) + sum([i.qty for i in pos_order_data])
        mapped_products = sale_order_data.mapped('product_id')
        for sale_pro in mapped_products:
            product = sale_order_data.filtered(lambda r: r.product_id.id == sale_pro.id)
            sale_qty = sum([i.product_uom_qty for i in product])
            data = {'product_uom_qty': sale_qty, 'name': sale_pro.name,
                    'amount': round(sum([i.price_total for i in product]), 2),
                    'percentage': round((sale_qty / total_qty) * 100, 2)
                    }
            products[sale_pro.id] = data

        pos_mapped_products = pos_order_data.mapped('product_id')
        sale_added_products = products.keys()
        for sale_pro in pos_mapped_products:
            product = pos_order_data.filtered(lambda r: r.product_id.id == sale_pro.id)
            pos_qty = sum([i.qty for i in product])

            if sale_pro.id in sale_added_products:
                sale_dict = products.get(sale_pro.id)
                sale_dict['product_uom_qty'] = sale_dict.get('product_uom_qty') + pos_qty
                sale_dict['amount'] = round(sale_dict.get('amount') + sum([i.price_subtotal_incl for i in product]), 2)
                sale_dict['percentage'] = round((sale_dict.get('product_uom_qty') + pos_qty / total_qty) * 100, 2)
                sale_dict['cogs'] = sale_pro.list_price
            else:
                data = {'product_uom_qty': pos_qty, 'name': sale_pro.name,
                        'amount': round(sum([i.price_subtotal_incl for i in product]), 2),
                        'percentage': round((pos_qty / total_qty) * 100, 2),
                        'cogs': sale_pro.list_price
                        }
                products[sale_pro.id] = data

        sorted_products = []
        sorted_products1 = sorted(products.items(), key=lambda k: k[1]['product_uom_qty'], reverse=True)
        if len(sorted_products1) > 10:
            sorted_products = sorted_products1[0:9]
        else:
            sorted_products = sorted_products1
        return {"data": sorted_products, 'start_date': start_date, 'end_date': end_date}

    @api.model
    def get_top_paired(self,start_date, end_date):
        uid = request.session.uid
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.utcnow()
        start_date_str = start_date + " 00:00:00"
        end_date_str = end_date + " 00:00:00"
        start_date_val = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
        end_date_val = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
        uid = request.session.uid
        data = []
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.now(tz)
        start_date_obj = start_date_val.astimezone(tz)
        end_date_obj = end_date_val.astimezone(tz)

        data_val = {}

        sale_order_data = self.env['sale.order'].sudo().search(
            [('date_order', '>=', start_date_obj), ('date_order', '<=', end_date_obj),
             ('state', '=', 'sale')])

        pos_order_data = self.env['pos.order'].sudo().search(
            [('date_order', '>=', start_date_obj), ('date_order', '<=', end_date_obj),
             ('state', 'in', ['paid', 'done', 'invoiced'])])

        for sale in sale_order_data:
            cat= {}
            for line in sale.order_line.filtered(lambda r: r.product_id.type != 'service'):
                if line.product_id.pos_categ_id:
                    if line.product_id.pos_categ_id.name not in cat.keys():
                        cat[line.product_id.pos_categ_id.name] = line.product_uom_qty
                    else:
                        cat[line.product_id.pos_categ_id.name] = cat[line.product_id.pos_categ_id.name] + line.product_uom_qty
            name = ''
            qty = 0
            for catname in cat:
                if name != '':
                    name = name + ' & ' + catname
                    qty = qty + cat[catname]
                else:
                    name = catname
                    qty = qty + cat[catname]
            if qty>0:
                if name in data_val.keys():
                    data_val[name]={'qty':qty+data_val[name]['qty']}
                else:
                    if '&' in name:
                        data_val[name] = {'qty': qty}



        for pos in pos_order_data:
            cat = {}
            for line in pos.lines.filtered(lambda r:r.product_id.type!='service'):
                if line.product_id.pos_categ_id:
                    if line.product_id.pos_categ_id.name not in cat.keys():
                            cat[line.product_id.pos_categ_id.name]=line.qty
                    else:
                        cat[line.product_id.pos_categ_id.name] = cat[line.product_id.pos_categ_id.name] + line.qty
            name=''
            qty =0
            for catname in cat:
                if name != '':
                    name = name + ' & ' + catname
                    qty = qty + cat[catname]
                else:
                    name = catname
                    qty = qty + cat[catname]
            if qty>0:
                if name in data_val.keys():
                    data_val[name]={'qty':qty+data_val[name]['qty']}
                else:
                    if '&' in name:
                        data_val[name] = {'qty': qty}
        sorted_products1 = sorted(data_val.items(), key=lambda k: k[1]['qty'], reverse=True) or []
        if len(sorted_products1) > 20:
            sorted_products = sorted_products1[0:19]
        else:
            sorted_products = sorted_products1
        if len(sorted_products)>0:
            total_qty = sum([i[1]['qty'] for i in sorted_products])
        else:
            total_qty=1
        return {"data": sorted_products, 'start_date': start_date, 'end_date': end_date,'total_qty':total_qty}

    @api.model
    def get_top_paired_today(self):
        uid = request.session.uid
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.utcnow()
        now = datetime.utcnow()
        utc = pytz.timezone('UTC')
        utc.localize(datetime.now())
        delta = utc.localize(now) - tz.localize(now)
        sec = delta.seconds
        total_minute = sec / 60
        order_time = today - timedelta(minutes=total_minute)
        order_time = order_time.replace(tzinfo=None)
        order_time = order_time.replace(microsecond=0)
        start_date = order_time

        data_val = {}

        sale_order_data = self.env['sale.order'].sudo().search(
            [('date_order', '>=', start_date),('state', '=', 'sale')])

        pos_order_data = self.env['pos.order'].sudo().search(
            [('date_order', '>=', start_date),
             ('state', 'in', ['paid', 'done', 'invoiced'])])

        for sale in sale_order_data:
            cat= {}
            for line in sale.order_line.filtered(lambda r: r.product_id.type != 'service'):
                if line.product_id.pos_categ_id:
                    if line.product_id.pos_categ_id.name not in cat.keys():
                        cat[line.product_id.pos_categ_id.name] = line.product_uom_qty
                    else:
                        cat[line.product_id.pos_categ_id.name] = cat[line.product_id.pos_categ_id.name] + line.product_uom_qty
            name = ''
            qty = 0
            for catname in cat:
                if name != '':
                    name = name + ' & ' + catname
                    qty = qty + cat[catname]
                else:
                    name = catname
                    qty = qty + cat[catname]
            if qty>0:
                if name in data_val.keys():
                    data_val[name]={'qty':qty+data_val[name]['qty']}
                else:
                    if '&' in name:
                        data_val[name] = {'qty': qty}

        for pos in pos_order_data:
            cat = {}
            for line in pos.lines.filtered(lambda r:r.product_id.type!='service'):
                if line.product_id.pos_categ_id:
                    if line.product_id.pos_categ_id.name not in cat.keys():
                            cat[line.product_id.pos_categ_id.name]=line.qty
                    else:
                        cat[line.product_id.pos_categ_id.name] = cat[line.product_id.pos_categ_id.name] + line.qty
            name=''
            qty =0
            for catname in cat:
                if name != '':
                    name = name + ' & ' + catname
                    qty = qty + cat[catname]
                else:
                    name = catname
                    qty = qty + cat[catname]
            if qty>0:
                if name in data_val.keys():
                    data_val[name]={'qty':qty+data_val[name]['qty']}
                else:
                    if '&' in name:
                        data_val[name] = {'qty': qty}

        print(data_val)
        sorted_products1 = sorted(data_val.items(), key=lambda k: k[1]['qty'], reverse=True) or []
        if len(sorted_products1) > 20:
            sorted_products = sorted_products1[0:19]
        else:
            sorted_products = sorted_products1
        if len(sorted_products)>0:
            total_qty = sum([i[1]['qty'] for i in sorted_products])
        else:
            total_qty=1

        return {"data": sorted_products,'total_qty':total_qty}

    @api.model
    def get_optional_product(self):
        uid = request.session.uid
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.utcnow()
        now = datetime.utcnow()
        utc = pytz.timezone('UTC')
        utc.localize(datetime.now())
        delta = utc.localize(now) - tz.localize(now)
        sec = delta.seconds
        total_minute = sec / 60
        order_time = today - timedelta(minutes=total_minute)
        order_time = order_time.replace(tzinfo=None)
        order_time = order_time.replace(microsecond=0)
        start_date = order_time

        data_val = {}

        sale_order_data = self.env['sale.order'].sudo().search(
            [('date_order', '>=', start_date), ('state', '=', 'sale')])

        pos_order_data = self.env['pos.order'].sudo().search(
            [('date_order', '>=', start_date),
             ('state', 'in', ['paid', 'done', 'invoiced'])])
        optional_product = {}
        for sale in sale_order_data:
            previous_line = False
            for line in sale.order_line:
                if line.product_id.is_optional_product:
                    if line.product_id.id not in optional_product.keys():
                        vals = {'quantity':line.product_uom_qty,'main_qty':{},'product_name':line.product_id.name}
                        if previous_line!=False:
                            vals['main_qty']={previous_line.product_id.name:1}
                        optional_product[line.product_id.id] =vals
                    else:
                        vals = optional_product.get(line.product_id.id)
                        vals['quantity']=vals.get('quantity')+line.product_uom_qty
                        if previous_line != False:
                            if previous_line.product_id.name in vals['main_qty'].keys():
                                vals['main_qty'][previous_line.product_id.name]=vals['main_qty'][previous_line.product_id.name]+1
                            else:
                                vals['main_qty'] = {previous_line.product_id.name: 1}

                        optional_product[line.product_id.id] = vals
                else:
                    previous_line = line

        for pos in pos_order_data:
            previous_line = False
            for line in pos.lines:
                if line.product_id.is_optional_product:
                    if line.product_id.id not in optional_product.keys():
                        vals = {'quantity': line.qty, 'main_qty': {},'product_name':line.product_id.name}
                        if previous_line != False:
                            vals['main_qty'] = {previous_line.product_id.name: 1}
                        optional_product[line.product_id.id] = vals
                    else:
                        vals = optional_product.get(line.product_id.id)
                        vals['quantity'] = vals.get('quantity') + line.qty
                        if previous_line != False:
                            if previous_line.product_id.name in vals['main_qty'].keys():
                                vals['main_qty'][previous_line.product_id.name] = vals['main_qty'][
                                                                                      previous_line.product_id.name] + 1
                            else:
                                vals['main_qty'] = {previous_line.product_id.name: 1}

                        optional_product[line.product_id.id] = vals
                else:
                    previous_line = line
        if bool(optional_product):
            for k in optional_product:
                vals = optional_product.get(k)
                main_qty = sorted(vals['main_qty'],key=lambda x:vals['main_qty'][x],reverse=True)
                if bool(main_qty):
                    vals['parent']=next(iter(main_qty))
                else:
                    vals['parent']=' '

        return {'data':optional_product}

    @api.model
    def get_optional_product_change_date(self,start_date,end_date):
        uid = request.session.uid
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.utcnow()

        start_date_str = start_date + " 00:00:00"
        end_date_str = end_date + " 00:00:00"
        start_date_val = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
        end_date_val = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
        uid = request.session.uid
        data = []
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.now(tz)
        start_date_obj = start_date_val.astimezone(tz)
        end_date_obj = end_date_val.astimezone(tz)


        sale_order_data = self.env['sale.order'].sudo().search(
            [('date_order', '>=', start_date_obj), ('date_order', '<=', end_date_obj),
             ('state', '=', 'sale')])

        pos_order_data = self.env['pos.order'].sudo().search(
            [('date_order', '>=', start_date_obj), ('date_order', '<=', end_date_obj),
             ('state', 'in', ['paid', 'done', 'invoiced'])])


        optional_product = {}
        for sale in sale_order_data:
            previous_line = False
            for line in sale.order_line:
                if line.product_id.is_optional_product:
                    if line.product_id.id not in optional_product.keys():
                        vals = {'quantity':line.product_uom_qty,'main_qty':{},'product_name':line.product_id.name}
                        if previous_line!=False:
                            vals['main_qty']={previous_line.product_id.name:1}
                        optional_product[line.product_id.id] =vals
                    else:
                        vals = optional_product.get(line.product_id.id)
                        vals['quantity']=vals.get('quantity')+line.product_uom_qty
                        if previous_line != False:
                            if previous_line.product_id.name in vals['main_qty'].keys():
                                vals['main_qty'][previous_line.product_id.name]=vals['main_qty'][previous_line.product_id.name]+1
                            else:
                                vals['main_qty'] = {previous_line.product_id.name: 1}

                        optional_product[line.product_id.id] = vals
                else:
                    previous_line = line

        for pos in pos_order_data:
            previous_line = False
            for line in pos.lines:
                if line.product_id.is_optional_product:
                    if line.product_id.id not in optional_product.keys():
                        vals = {'quantity': line.qty, 'main_qty': {},'product_name':line.product_id.name}
                        if previous_line != False:
                            vals['main_qty'] = {previous_line.product_id.name: 1}
                        optional_product[line.product_id.id] = vals
                    else:
                        vals = optional_product.get(line.product_id.id)
                        vals['quantity'] = vals.get('quantity') + line.qty
                        if previous_line != False:
                            if previous_line.product_id.name in vals['main_qty'].keys():
                                vals['main_qty'][previous_line.product_id.name] = vals['main_qty'][
                                                                                      previous_line.product_id.name] + 1
                            else:
                                vals['main_qty'] = {previous_line.product_id.name: 1}

                        optional_product[line.product_id.id] = vals
                else:
                    previous_line = line
        if bool(optional_product):
            for k in optional_product:
                vals = optional_product.get(k)
                main_qty = sorted(vals['main_qty'],key=lambda x:vals['main_qty'][x],reverse=True)
                if bool(main_qty):
                    vals['parent']=next(iter(main_qty))
                else:
                    vals['parent']=' '

        return {'data':optional_product,'start_date':start_date,'end_date':end_date}

    @api.model
    def get_top_selling_channel_mix(self):



        uid = request.session.uid
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.utcnow()
        now = datetime.utcnow()
        utc = pytz.timezone('UTC')
        utc.localize(datetime.now())
        delta = utc.localize(now) - tz.localize(now)
        sec = delta.seconds
        total_minute = sec / 60
        order_time = today - timedelta(minutes=total_minute)
        order_time = order_time.replace(tzinfo=None)
        order_time = order_time.replace(microsecond=0)

        start_date = order_time
        end_date = order_time
        domain = [('date_order', '>=', start_date),
                  ('state', 'in', ['paid', 'done', 'invoiced'])]
        sale_domain = [('date_order', '>=', start_date), ('state', '=', 'sale')]
        sale_order = self.env['sale.order'].search(sale_domain)
        sale_order_obj = self.env['sale.order']
        pos_order = self.env['pos.order'].search(domain)
        pos_order_obj = self.env['pos.order']
        hubster_order = self.env['hubster.order'].search([ ('create_date', '>=', start_date), ('create_date', '<=', end_date)])

        hubster_order_obj = self.env['hubster.order']

        if sale_order or pos_order or hubster_order:
            pass
        else:
            uber_vals_dict = {'count': 0, 'amount': 0}
            menulog_vals_dict = {'count': 0, 'amount': 0}
            deliveroo_vals_dict = {'count': 0, 'amount': 0}
            door_dash_vals_dict = {'count': 0, 'amount': 0}
            dine_in_vals_dict = {'count': 0, 'amount': 0}
            takeaway_vals_dict = {'count': 0, 'amount': 0}
            total_amount = 0
            uber_vals_dict['percentage'] = 0
            menulog_vals_dict['percentage'] = 0
            deliveroo_vals_dict['percentage'] = 0
            door_dash_vals_dict['percentage'] = 0
            dine_in_vals_dict['percentage'] = 0
            takeaway_vals_dict['percentage'] = 0
            data = {'uber': uber_vals_dict, 'menulog': menulog_vals_dict, 'deliveroo': deliveroo_vals_dict,'dine_in': dine_in_vals_dict,'takeaway': takeaway_vals_dict,
                    'door_dash': door_dash_vals_dict, 'no_order': {'count': 0, 'amount': 0, 'percentage': 100}}
            return {'data': data}

        uber_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('ubereats') if r.friendly_id else  sale_order_obj)
        door_dash_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('doordash') if r.friendly_id else  sale_order_obj)
        menulog_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('menulog') if r.friendly_id else  sale_order_obj)
        deliveroo_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('deliveroo-web') if r.friendly_id else  sale_order_obj)
        dine_in_sale = sale_order.filtered(lambda r: r.website_delivery_type == 'dine_in') or sale_order_obj
        takeaway_sale = sale_order.filtered(lambda r: r.website_delivery_type == 'takeway') or sale_order_obj

        uber_pos = pos_order.filtered(lambda r: r.delivery_type == 'uber') or pos_order_obj
        door_dash_pos = pos_order.filtered(lambda r: r.delivery_type == 'door') or pos_order_obj
        menulog_pos = pos_order.filtered(lambda r: r.delivery_type == 'menulog') or pos_order_obj
        deliveroo_pos = pos_order.filtered(lambda r: r.delivery_type == 'deliveroo') or pos_order_obj
        dine_in_pos = pos_order.filtered(lambda r: r.delivery_type == 'dine_in') or pos_order_obj
        takeaway_pos = pos_order.filtered(lambda r: r.delivery_type == 'takeway') or pos_order_obj

        uber_hub = hubster_order.filtered(lambda r: r.source == 'ubereats') or pos_order_obj

        door_dash_hub = hubster_order.filtered(lambda r: r.source  == 'door') or pos_order_obj

        menulog_hub = hubster_order.filtered(lambda r: r.source  == 'menulog') or pos_order_obj

        deliveroo_hub = hubster_order.filtered(lambda r: r.source  == 'deliveroo-web') or pos_order_obj

        dine_in_hub = hubster_order.filtered(lambda r: r.source  == 'dine_in') or pos_order_obj
        takeaway_hub = hubster_order.filtered(lambda r: r.source  == 'takeaway') or pos_order_obj


        if uber_sale or menulog_sale or deliveroo_sale or door_dash_sale or dine_in_sale or takeaway_sale or  uber_pos or menulog_pos or deliveroo_pos or door_dash_pos or dine_in_pos or takeaway_pos or uber_hub or menulog_hub or deliveroo_hub or door_dash_hub or dine_in_hub or takeaway_hub :
            uber_vals_dict = {'count': len(uber_sale) + len(uber_pos),
                              'amount': round(sum([i.amount_untaxed for i in uber_sale]) + sum(
                                  [pos.amount_total for pos in uber_pos]))}
            menulog_vals_dict = {'count': len(menulog_sale) + len(menulog_pos),
                                 'amount': round(sum([i.amount_untaxed for i in menulog_sale]) + sum(
                                     [pos.amount_total for pos in menulog_pos]))}
            deliveroo_vals_dict = {'count': len(deliveroo_sale) + len(deliveroo_pos),
                                   'amount': round(sum([i.amount_untaxed for i in deliveroo_sale]) + sum(
                                       [pos.amount_total for pos in deliveroo_pos]))}

            door_dash_vals_dict = {'count': len(door_dash_sale) + len(door_dash_pos),
                                   'amount': round(sum([i.amount_untaxed for i in door_dash_sale]) + sum(
                                       [pos.amount_total for pos in door_dash_pos]))}

            dine_in_vals_dict = {'count': len(dine_in_sale) + len(dine_in_pos)+len(dine_in_hub),
                                 'amount': round(sum([i.amount_untaxed for i in dine_in_sale]) + sum(
                                     [pos.amount_total for pos in dine_in_pos])+sum(
                                     [hub.total for hub in dine_in_hub]))}
            takeaway_vals_dict = {'count': len(takeaway_sale) + len(takeaway_pos)+len(takeaway_hub),
                                  'amount': round(sum([i.amount_untaxed for i in takeaway_sale]) + sum(
                                      [pos.amount_total for pos in takeaway_pos])+sum(
                                      [hub.total for hub in takeaway_hub]))}

            total_amount = uber_vals_dict.get('amount', 0) + menulog_vals_dict.get('amount',
                                                                                   0) + deliveroo_vals_dict.get(
                'amount', 0) + door_dash_vals_dict.get('amount', 0) +dine_in_vals_dict.get('amount', 0) +takeaway_vals_dict.get('amount', 0)
            uber_vals_dict['percentage'] = round((uber_vals_dict.get('amount', 0) / total_amount) * 100)
            menulog_vals_dict['percentage'] = round((menulog_vals_dict.get('amount', 0) / total_amount) * 100)
            deliveroo_vals_dict['percentage'] = round((deliveroo_vals_dict.get('amount', 0) / total_amount) * 100)
            door_dash_vals_dict['percentage'] = round((door_dash_vals_dict.get('amount', 0) / total_amount) * 100)
            dine_in_vals_dict['percentage'] = round((dine_in_vals_dict.get('amount', 0) / total_amount) * 100)
            takeaway_vals_dict['percentage'] = round((takeaway_vals_dict.get('amount', 0) / total_amount) * 100)
            data = {'uber': uber_vals_dict, 'menulog': menulog_vals_dict, 'deliveroo': deliveroo_vals_dict,'dine_in': dine_in_vals_dict,'takeaway': takeaway_vals_dict,
                    'door_dash': door_dash_vals_dict, 'no_order': {'count': 0, 'amount': 0, 'percentage': 0}}

            return {'data': data, 'start_date': start_date, 'end_date': end_date}
        else:
            uber_vals_dict = {'count': 0, 'amount': 0}
            menulog_vals_dict = {'count': 0, 'amount': 0}
            deliveroo_vals_dict = {'count': 0, 'amount': 0}
            door_dash_vals_dict = {'count': 0, 'amount': 0}
            dine_in_vals_dict = {'count': 0, 'amount': 0}
            takeaway_vals_dict = {'count': 0, 'amount': 0}
            total_amount = 0
            uber_vals_dict['percentage'] = 0
            menulog_vals_dict['percentage'] = 0
            deliveroo_vals_dict['percentage'] = 0
            door_dash_vals_dict['percentage'] = 0
            dine_in_vals_dict['percentage'] = 0
            takeaway_vals_dict['percentage'] = 0
            data = {'uber': uber_vals_dict, 'menulog': menulog_vals_dict, 'deliveroo': deliveroo_vals_dict,'dine_in': dine_in_vals_dict,'takeaway': takeaway_vals_dict,
                    'door_dash': door_dash_vals_dict, 'no_order': {'count': 0, 'amount': 0, 'percentage': 100}}
            return {'data': data}

    @api.model
    def get_top_selling_values_date_change_channel(self, start_date, end_date):
        uid = request.session.uid
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.utcnow()
        start_date = start_date
        end_date = end_date
        domain = [('date_order', '>=', start_date), ('date_order', '<=', end_date),
                  ('state', 'in', ['paid', 'done', 'invoiced'])]
        sale_domain = [('date_order', '>=', start_date), ('date_order', '<=', end_date), ('state', '=', 'sale')]
        sale_order = self.env['sale.order'].search(sale_domain)
        sale_order_obj = self.env['sale.order']
        pos_order = self.env['pos.order'].search(domain)
        pos_order_obj = self.env['pos.order']
        hubster_order = self.env['hubster.order'].search([ ('create_date', '>=', start_date), ('create_date', '<=', end_date)])

        hubster_order_obj = self.env['hubster.order']

        if sale_order or pos_order or hubster_order:
            pass
        else:

            uber_vals_dict = {'count': 0, 'amount': 0}
            menulog_vals_dict = {'count': 0, 'amount': 0}
            deliveroo_vals_dict = {'count': 0, 'amount': 0}
            door_dash_vals_dict = {'count': 0, 'amount': 0}
            dine_in_vals_dict = {'count': 0, 'amount': 0}
            takeaway_vals_dict = {'count': 0, 'amount': 0}
            total_amount = 0
            uber_vals_dict['percentage'] = 0
            menulog_vals_dict['percentage'] = 0
            deliveroo_vals_dict['percentage'] = 0
            door_dash_vals_dict['percentage'] = 0
            dine_in_vals_dict['percentage'] = 0
            takeaway_vals_dict['percentage'] = 0
            data = {'uber': uber_vals_dict, 'menulog': menulog_vals_dict, 'deliveroo': deliveroo_vals_dict,'dine_in': dine_in_vals_dict,'takeaway': takeaway_vals_dict,
                    'door_dash': door_dash_vals_dict, 'no_order': {'count': 0, 'amount': 0, 'percentage': 100}}
            return {'data': data, 'start_date': start_date, 'end_date': end_date}



        uber_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('ubereats') if r.friendly_id else  sale_order_obj)
        door_dash_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('doordash') if r.friendly_id else  sale_order_obj)
        menulog_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('menulog') if r.friendly_id else  sale_order_obj)
        deliveroo_sale = sale_order.filtered(lambda r: r.friendly_id.__contains__('deliveroo-web') if r.friendly_id else  sale_order_obj)
        dine_in_sale = sale_order.filtered(lambda r: r.website_delivery_type == 'dine_in') or sale_order_obj
        takeaway_sale = sale_order.filtered(lambda r: r.website_delivery_type == 'takeway') or sale_order_obj

        uber_pos = pos_order.filtered(lambda r: r.delivery_type == 'uber') or pos_order_obj
        door_dash_pos = pos_order.filtered(lambda r: r.delivery_type == 'door') or pos_order_obj
        menulog_pos = pos_order.filtered(lambda r: r.delivery_type == 'menulog') or pos_order_obj
        deliveroo_pos = pos_order.filtered(lambda r: r.delivery_type == 'deliveroo') or pos_order_obj
        dine_in_pos = pos_order.filtered(lambda r: r.delivery_type == 'dine_in') or pos_order_obj
        takeaway_pos = pos_order.filtered(lambda r: r.delivery_type == 'takeway') or pos_order_obj

        uber_hub = hubster_order.filtered(lambda r: r.source == 'ubereats') or pos_order_obj

        door_dash_hub = hubster_order.filtered(lambda r: r.source  == 'door') or pos_order_obj

        menulog_hub = hubster_order.filtered(lambda r: r.source  == 'menulog') or pos_order_obj

        deliveroo_hub = hubster_order.filtered(lambda r: r.source  == 'deliveroo-web') or pos_order_obj

        dine_in_hub = hubster_order.filtered(lambda r: r.source  == 'dine_in') or pos_order_obj
        takeaway_hub = hubster_order.filtered(lambda r: r.source  == 'takeaway') or pos_order_obj


        if uber_sale or menulog_sale or deliveroo_sale or door_dash_sale or dine_in_sale or takeaway_sale or  uber_pos or menulog_pos or deliveroo_pos or door_dash_pos or dine_in_pos or takeaway_pos  or uber_hub or menulog_hub or deliveroo_hub or door_dash_hub or dine_in_hub or takeaway_hub :

            uber_vals_dict = {'count': len(uber_sale) + len(uber_pos),
                              'amount': round(sum([i.amount_untaxed for i in uber_sale]) + sum(
                                  [pos.amount_total for pos in uber_pos]))}
            menulog_vals_dict = {'count': len(menulog_sale) + len(menulog_pos),
                                 'amount': round(sum([i.amount_untaxed for i in menulog_sale]) + sum(
                                     [pos.amount_total for pos in menulog_pos]))}
            deliveroo_vals_dict = {'count': len(deliveroo_sale) + len(deliveroo_pos),
                                   'amount': round(sum([i.amount_untaxed for i in deliveroo_sale]) + sum(
                                       [pos.amount_total for pos in deliveroo_pos]))}

            door_dash_vals_dict = {'count': len(door_dash_sale) + len(door_dash_pos),
                                   'amount': round(sum([i.amount_untaxed for i in door_dash_sale]) + sum(
                                       [pos.amount_total for pos in door_dash_pos]))}

            dine_in_vals_dict = {'count': len(dine_in_sale) + len(dine_in_pos)+len(dine_in_hub),
                                 'amount': round(sum([i.amount_untaxed for i in dine_in_sale]) + sum(
                                     [pos.amount_total for pos in dine_in_pos])+sum(
                                     [hub.total for hub in dine_in_hub]))}

            takeaway_vals_dict = {'count': len(takeaway_sale) + len(takeaway_pos)+len(takeaway_hub),
                                  'amount': round(sum([i.amount_untaxed for i in takeaway_sale]) + sum(
                                      [pos.amount_total for pos in takeaway_pos])+sum(
                                      [hub.total for hub in takeaway_hub]))}

            total_amount = uber_vals_dict.get('amount', 0) + menulog_vals_dict.get('amount',
                                                                                   0) + deliveroo_vals_dict.get(
                'amount', 0) + door_dash_vals_dict.get('amount', 0) +dine_in_vals_dict.get('amount', 0) +takeaway_vals_dict.get('amount', 0)
            uber_vals_dict['percentage'] = round((uber_vals_dict.get('amount', 0) / total_amount) * 100)


            menulog_vals_dict['percentage'] = round((menulog_vals_dict.get('amount', 0) / total_amount) * 100)
            deliveroo_vals_dict['percentage'] = round((deliveroo_vals_dict.get('amount', 0) / total_amount) * 100)

            door_dash_vals_dict['percentage'] = round((door_dash_vals_dict.get('amount', 0) / total_amount) * 100)
            dine_in_vals_dict['percentage'] = round((dine_in_vals_dict.get('amount', 0) / total_amount) * 100)

            takeaway_vals_dict['percentage'] = round((takeaway_vals_dict.get('amount', 0) / total_amount) * 100)
            data = {'uber': uber_vals_dict, 'menulog': menulog_vals_dict, 'deliveroo': deliveroo_vals_dict,'dine_in': dine_in_vals_dict,'takeaway': takeaway_vals_dict,
                    'door_dash': door_dash_vals_dict, 'no_order': {'count': 0, 'amount': 0, 'percentage': 0}}

            return {'data': data, 'start_date': start_date, 'end_date': end_date}



        else:

            uber_vals_dict = {'count': 0, 'amount': 0}
            menulog_vals_dict = {'count': 0, 'amount': 0}
            deliveroo_vals_dict = {'count': 0, 'amount': 0}
            door_dash_vals_dict = {'count': 0, 'amount': 0}
            dine_in_vals_dict = {'count': 0, 'amount': 0}
            takeaway_vals_dict = {'count': 0, 'amount': 0}
            total_amount = 0
            uber_vals_dict['percentage'] = 0
            menulog_vals_dict['percentage'] = 0
            deliveroo_vals_dict['percentage'] = 0
            door_dash_vals_dict['percentage'] = 0
            dine_in_vals_dict['percentage'] = 0
            takeaway_vals_dict['percentage'] = 0
            data = {'uber': uber_vals_dict, 'menulog': menulog_vals_dict, 'deliveroo': deliveroo_vals_dict,'dine_in': dine_in_vals_dict,'takeaway': takeaway_vals_dict,
                    'door_dash': door_dash_vals_dict, 'no_order': {'count': 0, 'amount': 0, 'percentage': 100}}

            return {'data': data, 'start_date': start_date, 'end_date': end_date}

    @api.model
    def get_service_speed(self):
        pass
        uid = request.session.uid
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        tz = pytz.timezone(user_type.tz or 'UTC')
        today = datetime.utcnow()
        now = datetime.utcnow()
        utc = pytz.timezone('UTC')
        utc.localize(datetime.now())
        delta = utc.localize(now) - tz.localize(now)
        sec = delta.seconds
        total_minute = sec / 60
        order_time = today - timedelta(minutes=total_minute)
        order_time = order_time.replace(tzinfo=None)
        order_time = order_time.replace(microsecond=0)

        start_date = order_time
        end_date = order_time

        pos_data = self.env['pos.order'].sudo().search(
            [('date_order', '>=', start_date ), ('date_order', '<=', end_date),

             ])
        return {'data': pos_data}

    @api.model
    def get_service_speed_date_change(self, start_date, end_date, time_interval):
        uid = request.session.uid
        user_type = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        if int(time_interval) <= 0:
            raise ValidationError(_("Time interval should be greater than zero."))
        from datetime import datetime
        date1 = datetime.strptime(start_date, '%Y-%m-%d')
        date2 = datetime.strptime(end_date, '%Y-%m-%d')
        pos_data = self.env['pos.order'].sudo().search(
            [('date_order', '>=', start_date + " 00:00:00"), ('date_order', '<=', end_date + " 23:59:59"),
             ('state', 'in', ['paid', 'done', 'invoiced']), ('delivery_order_time', '!=', False),
             ('done_order_time', '!=', False), ('finish_order_time', '!=', False)
             ])
        # if not pos_data:
        #     raise ValidationError(_('No orders found'))
        intervals = []
        data = {}
        settings = self.env['res.config.settings'].sudo().get_values()
        from_list = [
            settings['monday_from'],
            settings['tuesday_from'], settings['wednesday_from'],
            settings['thursday_from'], settings['friday_from'],
            settings['saturday_from'], settings['sunday_from']
        ]
        to_list = [
            settings['monday_to'],
            settings['tuesday_to'], settings['wednesday_to'],
            settings['thursday_to'], settings['friday_to'],
            settings['saturday_to'], settings['sunday_to']
        ]
        llimit = math.floor(float(min(from_list)))
        ulimit = math.ceil(float(max(to_list)))
        flag = True
        ltime = date1 + timedelta(hours=llimit)
        u2_time = date2 + timedelta(hours=ulimit)
        u2time = u2_time - timedelta(minutes=10)

        utime = ltime + timedelta(minutes=int(time_interval))
        colours = []
        current_uid = request.env.user
        tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
        while flag:
            customer_count = 0
            customer = []
            net_sales = 0
            speed_list = []
            order_list = []
            late_time_list = []
            cook_time = []
            front_pass_list = []
            h, m, s = ['00', '00', '00']
            pos_avg2 = '00:00'
            cook_time_avg = '0:00'
            avg_cook_late = '0:00'
            front_pass_avg = '0:00'
            utimessss = u2_time + timedelta(hours=1)
            if utime.time() == u2_time.time() or utime.time() == utimessss.time() :
                flag = False
            else:
                llimit += int(time_interval)/60
                ltime = utime
                utime = ltime + timedelta(minutes=int(time_interval))
                i_orders = pos_data.filtered(lambda r: (ltime.time() <= r.date_order.time() <= utime.time())
                                             )

                for j in i_orders:
                    if j.partner_id:
                        if j.partner_id in customer:
                            pass
                        else:
                            customer.append(j.partner_id)
                    customer_count = len(customer)
                    average_cook_time = j.finish_order_time.time()
                    avg_cook_time = datetime.combine(date.min, average_cook_time) - datetime.min
                    cook_time.append(avg_cook_time)
                    cook_time_total = timedelta(minutes=int(0))
                    for x in cook_time:
                        cook_time_total += x
                    average = cook_time_total / len(cook_time)
                    h, m, s = [str(average).split(':')[0],
                               str(average).split(':')[1],
                               str(round(float(str(average).split(':')[-1])))]
                    cook_time_avg = h + ':' + m

                    average_pos_list = []
                    average_pos_speed = timedelta(minutes=int(0))
                    difference = relativedelta(j.order_set_time,
                                                             j.date_order.astimezone(tz).replace(tzinfo=None))
                    average_pos_list.append(difference)
                    for x in average_pos_list:
                        average_pos_speed += x
                    pos_average = average_pos_speed / len(i_orders)
                    h = str(abs(pos_average.hours))
                    m = str(abs(pos_average.minutes))
                    s = str(abs(pos_average.seconds))
                    pos_avg = h + ':' + m + ':' + s
                    pos_avg1 = datetime.strptime(pos_avg, "%H:%M:%S")
                    pos_avg2 = pos_avg1.time().strftime("%H:%M")

                    # print("here...................")
                    tz = pytz.timezone(j.company_id.tz or 'Australia/Brisbane')
                    estimation = j.date_order + timedelta(minutes=j.preparation_time)
                    late_time_total = timedelta(minutes=int(0))
                    delivery_time = j.delivery_order_time
                    if delivery_time > estimation:
                        late_time = delivery_time - estimation
                        late_time_list.append(late_time)
                        for x in late_time_list:
                            late_time_total += x
                    if len(late_time_list) != 0:
                        avg_cook_late = late_time_total / len(late_time_list)
                        h, m, s = [str(avg_cook_late).split(':')[0],
                                   str(avg_cook_late).split(':')[1],
                                   str(round(float(str(avg_cook_late).split(':')[-1])))]
                        avg_cook_late = h + ':' + m

                    average_front_pass = timedelta(minutes=int(0))
                    front_pass = j.done_order_time - j.delivery_order_time
                    front_pass_list.append(front_pass)
                    for x in front_pass_list:
                        average_front_pass += x
                    front_pass_average = average_front_pass / len(front_pass_list)
                    h, m, s = [str(front_pass_average).split(':')[0],
                               str(front_pass_average).split(':')[1],
                               str(round(float(str(front_pass_average).split(':')[-1])))]
                    front_pass_avg = h + ':' + m
                sa = round(sum(i_orders.mapped('amount_paid')),2)
                net_sales += sa
                cflag = True
                while cflag:
                    color = '#{:02x}{:02x}{:02x}'.format(*map(lambda x: random.randint(0, 255), range(3)))
                    if color in colours:
                        pass
                    else:
                        colours.append(color)
                        cflag = False
                i_orders_d = {
                    'sales': sa,
                    'customers': customer_count,
                    'speed': pos_avg2,
                    'count': len(i_orders.ids),
                    'late': avg_cook_late,
                    'time': cook_time_avg,
                    'pass': front_pass_avg}

                i_orders_null = {
                        'sales': 0,
                        'customers': 0,
                        'speed': 0,
                        'count': 0,
                        'late': 0,
                        'time': 0,
                        'pass': 0
                    }

                if int(llimit) < 10:
                    if len(str(((llimit-int(llimit))*60)/100)[2:]) > 2:
                        t_interval = '0' + str(int(llimit)) + ":" + str(((llimit - int(llimit)) * 60) / 100)[2:3] + '0'
                    elif len(str(((llimit-int(llimit))*60)/100)[2:]) < 2:
                        t_interval = '0' + str(int(llimit)) + ":" + str(((llimit-int(llimit))*60)/100)[2:] + '0'
                    else:
                        t_interval = '0' + str(int(llimit)) + ":" + str(((llimit-int(llimit))*60)/100)[2:]
                else:
                    if len(str(((llimit-int(llimit))*60)/100)[2:]) > 2:
                        t_interval = str(int(llimit)) + ":" + str(((llimit - int(llimit)) * 60) / 100)[2:3] + '0'
                    elif len(str(((llimit-int(llimit))*60)/100)[2:]) < 2:
                        t_interval = str(int(llimit)) + ":" + str(((llimit-int(llimit))*60)/100)[2:] + '0'
                    else:
                        t_interval = str(int(llimit)) + ":" + str(((llimit-int(llimit))*60)/100)[2:]
                if i_orders:
                    data[t_interval] = i_orders_d
                else:
                    data[t_interval] = i_orders_null
                intervals.append(t_interval)
        return {'data': data, 'intervals': sorted(list(set(intervals))), 'start_date': start_date,
                'end_date': end_date, 'time_interval': time_interval, 'colours': colours}

class PosCart(models.Model):
    _inherit = 'pos.order'

    order_set_time = fields.Datetime('Cart update time')

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosCart, self)._order_fields(ui_order)
        if 'order_set_time' in ui_order:
            res['order_set_time'] = ui_order.get('order_set_time')
        print(ui_order, 'order printing')
        return res
