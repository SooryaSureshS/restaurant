from odoo import api, fields, models, _
from datetime import date, datetime
import pytz
from datetime import timedelta
from odoo.osv.expression import AND
from odoo.exceptions import UserError, ValidationError

import time


class SalesDetailsReport(models.AbstractModel):
    _name = 'report.sales_report.report_pos_pdf'

    profit_loss = fields.Many2one('account.common.report')

    def get_days(self, this_week_start_time, this_week_end_time, day):
        return [this_week_start_time + timedelta(days=x) for x in
                range((this_week_end_time - this_week_start_time).days + 1) if
                (this_week_start_time + timedelta(days=x)).weekday() == time.strptime(day, '%A').tm_wday]

    def day_sales_with_time(self, date_order_frm, date_order_to):
        return self.env['sale.order'].sudo().search(
            [('state', '=', 'sale'), ('date_order', '=', date_order_frm), ('date_order', '>', date_order_to)])

    def day_pos_with_time(self, date_order_frm, date_order_to):
        return self.env['pos.order'].sudo().search(
            [('state', 'in', ['paid', 'done', 'invoiced']), ('date_order', '<=', date_order_frm),
             ('date_order', '>', date_order_to)])

    def _get_report_values(self, docids, data=None):
        sale_domain = [('state', 'in', ['sale'])]
        pos_domain = [('state', 'in', ['paid', 'done', 'invoiced'])]
        tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        if data.get('date_start'):
            date_start = fields.Datetime.from_string(data.get('date_start'))
        else:
            # start by default today 00:00:00
            user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
            date_start = today.astimezone(pytz.timezone('UTC'))

        if data.get('date_end'):
            date_stop = fields.Datetime.from_string(data.get('date_end'))
            # avoid a date_stop smaller than date_start
            if date_stop < date_start:
                date_stop = date_start + timedelta(days=1, seconds=-1)
        else:
            # stop by default today 23:59:59
            date_stop = date_start + timedelta(days=1, seconds=-1)

        domain = AND([sale_domain,
                      [('date_order', '>=', date_start.date()),
                       ('date_order', '<=', date_stop.date())]
                      ])
        domain_pos = AND([pos_domain,
                          [('date_order', '>=', date_start.date()),
                           ('date_order', '<=', date_stop.date())]
                          ])

        sales_orders = self.env['sale.order'].search(domain)
        pos_orders = self.env['pos.order'].search(domain_pos)
        pos_days = {}
        sale_days = {}
        day_list = [0, 1, 2, 3, 4, 5, 6]
        for i in day_list:
            pos_list = pos_orders.filtered(
                lambda line: line.date_order.astimezone(tz).weekday() == i)
            pos_days[i] = pos_list
        for k in day_list:
            sales_list = sales_orders.filtered(
                lambda line: line.date_order.astimezone(tz).weekday() == k
            )
            sale_days[k] = sales_list
        monday_sales_gross = 0.0
        tuesday_sales_gross = 0.0
        wednesday_sales_gross = 0.0
        thursday_sales_gross = 0.0
        friday_sales_gross = 0.0
        saturday_sales_gross = 0.0
        sunday_sales_gross = 0.0
        monday_transactions = len(pos_days.get(0)) + len(sale_days.get(0))
        tuesday_transactions = len(pos_days.get(1)) + len(sale_days.get(1))
        wednesday_transactions = len(pos_days.get(2)) + len(sale_days.get(2))
        thursday_transactions = len(pos_days.get(3)) + len(sale_days.get(3))
        friday_transactions = len(pos_days.get(4)) + len(sale_days.get(4))
        saturday_transactions = len(pos_days.get(5)) + len(sale_days.get(5))
        sunday_transactions = len(pos_days.get(6)) + len(sale_days.get(6))

        cash_monday_sales = 0.0
        cash_mo = []
        cash_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_monday_sales += rec.amount_total
                    cash_mo.append(rec)
                    cash_monday_transactions = len(cash_mo)
        cash_tuesday_sales = 0.0
        cash_tu = []
        cash_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_tuesday_sales += rec.amount_total
                    cash_tu.append(rec)
                    cash_tuesday_transactions = len(cash_tu)
        cash_wednesday_sales = 0.0
        cash_wed = []
        cash_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_wednesday_sales += rec.amount_total
                    cash_wed.append(rec)
                    cash_wednesday_transactions = len(cash_wed)
        cash_thursday_sales = 0.0
        cash_th = []
        cash_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_thursday_sales += rec.amount_total
                    cash_th.append(rec)
                    cash_thursday_transactions = len(cash_th)
        cash_friday_sales = 0.0
        cash_fri = []
        cash_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_friday_sales += rec.amount_total
                    cash_fri.append(rec)
                    cash_friday_transactions = len(cash_fri)
        cash_saturday_sales = 0.0
        cash_sat = []
        cash_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_saturday_sales += rec.amount_total
                    cash_sat.append(rec)
                    cash_saturday_transactions = len(cash_sat)
        cash_sunday_sales = 0.0
        cash_sun = []
        cash_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_sunday_sales += rec.amount_total
                    cash_sun.append(rec)
                    cash_sunday_transactions = len(cash_sun)

        credit_monday_sales = 0.0
        credit_mo = []
        credit_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_monday_sales += rec.amount_total
                    credit_mo.append(rec)
                    credit_monday_transactions = len(credit_mo)
        credit_tuesday_sales = 0.0
        credit_tu = []
        credit_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_tuesday_sales += rec.amount_total
                    credit_tu.append(rec)
                    credit_tuesday_transactions = len(credit_tu)
        credit_wednesday_sales = 0.0
        credit_wed = []
        credit_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_wednesday_sales += rec.amount_total
                    credit_wed.append(rec)
                    credit_wednesday_transactions = len(credit_wed)
        credit_thursday_sales = 0.0
        credit_th = []
        credit_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_thursday_sales += rec.amount_total
                    credit_th.append(rec)
                    credit_thursday_transactions = len(credit_th)
        credit_friday_sales = 0.0
        credit_fri = []
        credit_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_friday_sales += rec.amount_total
                    credit_fri.append(rec)
                    credit_friday_transactions = len(credit_fri)
        credit_saturday_sales = 0.0
        credit_sat = []
        credit_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_saturday_sales += rec.amount_total
                    credit_sat.append(rec)
                    credit_saturday_transactions = len(credit_sat)
        credit_sunday_sales = 0.0
        credit_sun = []
        credit_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_sunday_sales += rec.amount_total
                    credit_sun.append(rec)
                    credit_sunday_transactions = len(credit_sun)

        debit_monday_sales = 0.0
        debit_mo = []
        debit_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_monday_sales += rec.amount_total
                    debit_mo.append(rec)
                    debit_monday_transactions = len(debit_mo)
        debit_tuesday_sales = 0.0
        debit_tu = []
        debit_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_tuesday_sales += rec.amount_total
                    debit_tu.append(rec)
                    debit_tuesday_transactions = len(debit_tu)
        debit_wednesday_sales = 0.0
        debit_wed = []
        debit_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_wednesday_sales += rec.amount_total
                    debit_wed.append(rec)
                    debit_wednesday_transactions = len(debit_wed)
        debit_thursday_sales = 0.0
        debit_th = []
        debit_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_thursday_sales += rec.amount_total
                    debit_th.append(rec)
                    debit_thursday_transactions = len(debit_th)
        debit_friday_sales = 0.0
        debit_fri = []
        debit_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_friday_sales += rec.amount_total
                    debit_fri.append(rec)
                    debit_friday_transactions = len(debit_fri)
        debit_saturday_sales = 0.0
        debit_sat = []
        debit_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_saturday_sales += rec.amount_total
                    debit_sat.append(rec)
                    debit_saturday_transactions = len(debit_sat)
        debit_sunday_sales = 0.0
        debit_sun = []
        debit_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_sunday_sales += rec.amount_total
                    debit_sun.append(rec)
                    debit_sunday_transactions = len(debit_sun)

        upi_monday_sales = 0.0
        upi_mo = []
        upi_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_monday_sales += rec.amount_total
                    upi_mo.append(rec)
                    upi_monday_transactions = len(upi_mo)
        upi_tuesday_sales = 0.0
        upi_tu = []
        upi_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_tuesday_sales += rec.amount_total
                    upi_tu.append(rec)
                    cash_tuesday_transactions = len(upi_tu)
        upi_wednesday_sales = 0.0
        upi_wed = []
        upi_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_wednesday_sales += rec.amount_total
                    upi_wed.append(rec)
                    upi_wednesday_transactions = len(upi_wed)
        upi_thursday_sales = 0.0
        upi_th = []
        upi_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_thursday_sales += rec.amount_total
                    upi_th.append(rec)
                    upi_thursday_transactions = len(upi_th)
        upi_friday_sales = 0.0
        upi_fri = []
        upi_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_friday_sales += rec.amount_total
                    upi_fri.append(rec)
                    upi_friday_transactions = len(upi_fri)
        upi_saturday_sales = 0.0
        upi_sat = []
        upi_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_saturday_sales += rec.amount_total
                    upi_sat.append(rec)
                    upi_saturday_transactions = len(upi_sat)
        upi_sunday_sales = 0.0
        upi_sun = []
        upi_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_sunday_sales += rec.amount_total
                    upi_sun.append(rec)
                    upi_sunday_transactions = len(upi_sun)

        paytm_monday_sales = 0.0
        paytm_mo = []
        paytm_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_monday_sales += rec.amount_total
                    paytm_mo.append(rec)
                    paytm_monday_transactions = len(paytm_mo)
        paytm_tuesday_sales = 0.0
        paytm_tu = []
        paytm_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_tuesday_sales += rec.amount_total
                    paytm_tu.append(rec)
                    cash_tuesday_transactions = len(paytm_tu)
        paytm_wednesday_sales = 0.0
        paytm_wed = []
        paytm_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_wednesday_sales += rec.amount_total
                    paytm_wed.append(rec)
                    paytm_wednesday_transactions = len(paytm_wed)
        paytm_thursday_sales = 0.0
        paytm_th = []
        paytm_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_thursday_sales += rec.amount_total
                    paytm_th.append(rec)
                    paytm_thursday_transactions = len(paytm_th)
        paytm_friday_sales = 0.0
        paytm_fri = []
        paytm_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_friday_sales += rec.amount_total
                    paytm_fri.append(rec)
                    paytm_friday_transactions = len(paytm_fri)
        paytm_saturday_sales = 0.0
        paytm_sat = []
        paytm_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_saturday_sales += rec.amount_total
                    paytm_sat.append(rec)
                    paytm_saturday_transactions = len(paytm_sat)
        paytm_sunday_sales = 0.0
        paytm_sun = []
        paytm_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_sunday_sales += rec.amount_total
                    paytm_sun.append(rec)
                    paytm_sunday_transactions = len(paytm_sun)

        phone_monday_sales = 0.0
        phone_mo = []
        phone_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_monday_sales += rec.amount_total
                    phone_mo.append(rec)
                    phone_monday_transactions = len(phone_mo)
        phone_tuesday_sales = 0.0
        phone_tu = []
        phone_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_tuesday_sales += rec.amount_total
                    phone_tu.append(rec)
                    cash_tuesday_transactions = len(phone_tu)
        phone_wednesday_sales = 0.0
        phone_wed = []
        phone_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_wednesday_sales += rec.amount_total
                    phone_wed.append(rec)
                    phone_wednesday_transactions = len(phone_wed)
        phone_thursday_sales = 0.0
        phone_th = []
        phone_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_thursday_sales += rec.amount_total
                    phone_th.append(rec)
                    phone_thursday_transactions = len(phone_th)
        phone_friday_sales = 0.0
        phone_fri = []
        phone_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_friday_sales += rec.amount_total
                    phone_fri.append(rec)
                    phone_friday_transactions = len(phone_fri)
        phone_saturday_sales = 0.0
        phone_sat = []
        phone_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_saturday_sales += rec.amount_total
                    phone_sat.append(rec)
                    phone_saturday_transactions = len(phone_sat)
        phone_sunday_sales = 0.0
        phone_sun = []
        phone_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_sunday_sales += rec.amount_total
                    phone_sun.append(rec)
                    phone_sunday_transactions = len(phone_sun)

        free_monday_sales = 0.0
        free_mo = []
        free_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_monday_sales += rec.amount_total
                    free_mo.append(rec)
                    free_monday_transactions = len(free_mo)
        free_tuesday_sales = 0.0
        free_tu = []
        free_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_tuesday_sales += rec.amount_total
                    free_tu.append(rec)
                    cash_tuesday_transactions = len(free_tu)
        free_wednesday_sales = 0.0
        free_wed = []
        free_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_wednesday_sales += rec.amount_total
                    free_wed.append(rec)
                    free_wednesday_transactions = len(free_wed)
        free_thursday_sales = 0.0
        free_th = []
        free_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_thursday_sales += rec.amount_total
                    free_th.append(rec)
                    free_thursday_transactions = len(free_th)
        free_friday_sales = 0.0
        free_fri = []
        free_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_friday_sales += rec.amount_total
                    free_fri.append(rec)
                    free_friday_transactions = len(free_fri)
        free_saturday_sales = 0.0
        free_sat = []
        free_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_saturday_sales += rec.amount_total
                    free_sat.append(rec)
                    free_saturday_transactions = len(free_sat)
        free_sunday_sales = 0.0
        free_sun = []
        free_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_sunday_sales += rec.amount_total
                    free_sun.append(rec)
                    free_sunday_transactions = len(free_sun)

        sodexo_monday_sales = 0.0
        sodexo_mo = []
        sodexo_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_monday_sales += rec.amount_total
                    sodexo_mo.append(rec)
                    sodexo_monday_transactions = len(sodexo_mo)
        sodexo_tuesday_sales = 0.0
        sodexo_tu = []
        sodexo_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_tuesday_sales += rec.amount_total
                    sodexo_tu.append(rec)
                    cash_tuesday_transactions = len(sodexo_tu)
        sodexo_wednesday_sales = 0.0
        sodexo_wed = []
        sodexo_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_wednesday_sales += rec.amount_total
                    sodexo_wed.append(rec)
                    sodexo_wednesday_transactions = len(sodexo_wed)
        sodexo_thursday_sales = 0.0
        sodexo_th = []
        sodexo_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_thursday_sales += rec.amount_total
                    sodexo_th.append(rec)
                    sodexo_thursday_transactions = len(sodexo_th)
        sodexo_friday_sales = 0.0
        sodexo_fri = []
        sodexo_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_friday_sales += rec.amount_total
                    sodexo_fri.append(rec)
                    sodexo_friday_transactions = len(sodexo_fri)
        sodexo_saturday_sales = 0.0
        sodexo_sat = []
        sodexo_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_saturday_sales += rec.amount_total
                    sodexo_sat.append(rec)
                    sodexo_saturday_transactions = len(sodexo_sat)
        sodexo_sunday_sales = 0.0
        sodexo_sun = []
        sodexo_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_sunday_sales += rec.amount_total
                    sodexo_sun.append(rec)
                    sodexo_sunday_transactions = len(sodexo_sun)

        samsung_monday_sales = 0.0
        samsung_mo = []
        samsung_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_monday_sales += rec.amount_total
                    samsung_mo.append(rec)
                    samsung_monday_transactions = len(samsung_mo)
        samsung_tuesday_sales = 0.0
        samsung_tu = []
        samsung_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_tuesday_sales += rec.amount_total
                    samsung_tu.append(rec)
                    cash_tuesday_transactions = len(samsung_tu)
        samsung_wednesday_sales = 0.0
        samsung_wed = []
        samsung_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_wednesday_sales += rec.amount_total
                    samsung_wed.append(rec)
                    samsung_wednesday_transactions = len(samsung_wed)
        samsung_thursday_sales = 0.0
        samsung_th = []
        samsung_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_thursday_sales += rec.amount_total
                    samsung_th.append(rec)
                    samsung_thursday_transactions = len(samsung_th)
        samsung_friday_sales = 0.0
        samsung_fri = []
        samsung_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_friday_sales += rec.amount_total
                    samsung_fri.append(rec)
                    samsung_friday_transactions = len(samsung_fri)
        samsung_saturday_sales = 0.0
        samsung_sat = []
        samsung_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_saturday_sales += rec.amount_total
                    samsung_sat.append(rec)
                    samsung_saturday_transactions = len(samsung_sat)
        samsung_sunday_sales = 0.0
        samsung_sun = []
        samsung_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_sunday_sales += rec.amount_total
                    samsung_sun.append(rec)
                    samsung_sunday_transactions = len(samsung_sun)

        apple_monday_sales = 0.0
        apple_mo = []
        apple_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_monday_sales += rec.amount_total
                    apple_mo.append(rec)
                    apple_monday_transactions = len(apple_mo)
        apple_tuesday_sales = 0.0
        apple_tu = []
        apple_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_tuesday_sales += rec.amount_total
                    apple_tu.append(rec)
                    cash_tuesday_transactions = len(apple_tu)
        apple_wednesday_sales = 0.0
        apple_wed = []
        apple_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_wednesday_sales += rec.amount_total
                    apple_wed.append(rec)
                    apple_wednesday_transactions = len(apple_wed)
        apple_thursday_sales = 0.0
        apple_th = []
        apple_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_thursday_sales += rec.amount_total
                    apple_th.append(rec)
                    apple_thursday_transactions = len(apple_th)
        apple_friday_sales = 0.0
        apple_fri = []
        apple_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_friday_sales += rec.amount_total
                    apple_fri.append(rec)
                    apple_friday_transactions = len(apple_fri)
        apple_saturday_sales = 0.0
        apple_sat = []
        apple_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_saturday_sales += rec.amount_total
                    apple_sat.append(rec)
                    apple_saturday_transactions = len(apple_sat)
        apple_sunday_sales = 0.0
        apple_sun = []
        apple_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_sunday_sales += rec.amount_total
                    apple_sun.append(rec)
                    apple_sunday_transactions = len(apple_sun)

        organize_list = {}
        organize = self.env['organize.slot'].search([('create_date', '>=', date_start.date()),
                                                     ('create_date', '<=', date_stop.date())])
        for i in day_list:
            schedule_list = organize.filtered(
                lambda line: line.start_datetime.astimezone(tz).weekday() == i)
            organize_list[i] = schedule_list

        monday_employee_meals = 0.0
        tuesday_employee_meals = 0.0
        wednesday_employee_meals = 0.0
        thursday_employee_meals = 0.0
        friday_employee_meals = 0.0
        saturday_employee_meals = 0.0
        sunday_employee_meals = 0.0
        for emp in pos_days.get(0):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    monday_employee_meals += rec.amount
        for emp in pos_days.get(1):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    tuesday_employee_meals += rec.amount
        for emp in pos_days.get(2):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    wednesday_employee_meals += rec.amount
        for emp in pos_days.get(3):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    thursday_employee_meals += rec.amount
        for emp in pos_days.get(4):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    friday_employee_meals += rec.amount
        for emp in pos_days.get(5):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    saturday_employee_meals += rec.amount
        for emp in pos_days.get(6):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    sunday_employee_meals += rec.amount

        monday_refund_amount = 0.0
        tuesday_refund_amount = 0.0
        wednesday_refund_amount = 0.0
        thursday_refund_amount = 0.0
        friday_refund_amount = 0.0
        saturday_refund_amount = 0.0
        sunday_refund_amount = 0.0
        for recd in pos_days.get(0):
            if "REFUND" in recd.name:
                monday_refund_amount += recd.amount_total
        for recd in pos_days.get(1):
            if "REFUND" in recd.name:
                tuesday_refund_amount += recd.amount_total
        for recd in pos_days.get(2):
            if "REFUND" in recd.name:
                wednesday_refund_amount += recd.amount_total
        for recd in pos_days.get(3):
            if "REFUND" in recd.name:
                thursday_refund_amount += recd.amount_total
        for recd in pos_days.get(4):
            if "REFUND" in recd.name:
                friday_refund_amount += recd.amount_total
        for recd in pos_days.get(5):
            if "REFUND" in recd.name:
                saturday_refund_amount += recd.amount_total
        for recd in pos_days.get(6):
            if "REFUND" in recd.name:
                sunday_refund_amount += recd.amount_total

        monday_tax = 0.0
        tuesday_tax = 0.0
        wednesday_tax = 0.0
        thursday_tax = 0.0
        friday_tax = 0.0
        saturday_tax = 0.0
        sunday_tax = 0.0
        for rec in pos_days.get(0):
            monday_sales_gross += rec.amount_total
            monday_tax += rec.amount_tax
        for rec in sale_days.get(0):
            monday_sales_gross += rec.amount_total
        for rec in pos_days.get(1):
            tuesday_sales_gross += rec.amount_total
            tuesday_tax += rec.amount_tax
        for rec in sale_days.get(1):
            tuesday_sales_gross += rec.amount_total
        for rec in pos_days.get(2):
            wednesday_sales_gross += rec.amount_total
            wednesday_tax += rec.amount_tax
        for rec in sale_days.get(2):
            wednesday_sales_gross += rec.amount_total
        for rec in pos_days.get(3):
            thursday_sales_gross += rec.amount_total
            thursday_tax += rec.amount_tax
        for rec in sale_days.get(3):
            thursday_sales_gross += rec.amount_total
        for rec in pos_days.get(4):
            friday_sales_gross += rec.amount_total
            friday_tax += rec.amount_tax
        for rec in sale_days.get(4):
            friday_sales_gross += rec.amount_total
        for rec in pos_days.get(5):
            saturday_sales_gross += rec.amount_total
            saturday_tax += rec.amount_tax
        for rec in sale_days.get(5):
            saturday_sales_gross += rec.amount_total
        for rec in pos_days.get(6):
            sunday_sales_gross += rec.amount_total
            sunday_tax += rec.amount_tax
        for rec in sale_days.get(6):
            sunday_sales_gross += rec.amount_total

        monday_sales_net = monday_sales_gross - monday_tax
        tuesday_sales_net = tuesday_sales_gross - tuesday_tax
        wednesday_sales_net = wednesday_sales_gross - wednesday_tax
        thursday_sales_net = thursday_sales_gross - thursday_tax
        friday_sales_net = friday_sales_gross - friday_tax
        saturday_sales_net = saturday_sales_gross - saturday_tax
        sunday_sales_net = sunday_sales_gross - sunday_tax

        monday_employees = 0.0
        tuesday_employees = 0.0
        wednesday_employees = 0.0
        thursday_employees = 0.0
        friday_employees = 0.0
        saturday_employees = 0.0
        sunday_employees = 0.0

        if len(organize_list.get(0).employee_id.ids) != 0:
            monday_employees = monday_sales_gross / len(organize_list.get(0).employee_id.ids)
        if len(organize_list.get(1).employee_id.ids) != 0:
            tuesday_employees = tuesday_sales_gross / len(organize_list.get(1).employee_id.ids)
        if len(organize_list.get(2).employee_id.ids) != 0:
            wednesday_employees = wednesday_sales_gross / len(organize_list.get(2).employee_id.ids)
        if len(organize_list.get(3).employee_id.ids) != 0:
            thursday_employees = thursday_sales_gross / len(organize_list.get(3).employee_id.ids)
        if len(organize_list.get(4).employee_id.ids) != 0:
            friday_employees = friday_sales_gross / len(organize_list.get(4).employee_id.ids)
        if len(organize_list.get(5).employee_id.ids) != 0:
            saturday_employees = saturday_sales_gross / len(organize_list.get(6).employee_id.ids)
        if len(organize_list.get(6).employee_id.ids) != 0:
            sunday_employees = sunday_sales_gross / len(organize_list.get(6).employee_id.ids)

        sales_gross = 0.0
        tax = 0.0
        sales_net = 0.0
        transactions = 0.0
        refund_amount = 0.0
        promo_amount = 0.0
        employee_meals = 0.0
        total_sales_net = monday_sales_net + tuesday_sales_net + wednesday_sales_net + thursday_sales_net + friday_sales_net + saturday_sales_net + sunday_sales_net
        sales_gross_total = monday_sales_gross + tuesday_sales_gross + wednesday_sales_gross + thursday_sales_gross + friday_sales_gross + saturday_sales_gross + sunday_sales_gross
        total_transactions = monday_transactions + tuesday_transactions + wednesday_transactions + thursday_transactions + friday_transactions + saturday_employees + sunday_transactions
        total_spmh = monday_employees + tuesday_employees + wednesday_employees + thursday_employees + friday_employees + saturday_employees + sunday_employees
        total_refund = monday_refund_amount + tuesday_refund_amount + wednesday_refund_amount + thursday_refund_amount + friday_refund_amount + saturday_refund_amount + sunday_refund_amount
        total_employee_meals = monday_employee_meals + tuesday_employee_meals + wednesday_employee_meals + thursday_employee_meals + friday_employee_meals + saturday_refund_amount + sunday_employee_meals
        total_cash_sales = cash_monday_sales + cash_tuesday_sales + cash_wednesday_sales + cash_thursday_sales + cash_friday_sales + cash_saturday_sales + cash_sunday_sales
        total_cash_transactions = cash_monday_transactions + cash_tuesday_transactions + cash_wednesday_transactions + cash_thursday_transactions + cash_friday_transactions + cash_saturday_transactions + cash_sunday_transactions
        total_credit_sales = credit_monday_sales + credit_tuesday_sales + credit_wednesday_sales + credit_thursday_sales + credit_friday_sales + credit_saturday_sales + credit_sunday_sales
        total_credit_transactions = credit_monday_transactions + credit_tuesday_transactions + credit_wednesday_transactions + credit_thursday_transactions + credit_friday_transactions + credit_saturday_transactions + credit_sunday_transactions
        total_debit_sales = debit_monday_sales + debit_tuesday_sales + debit_wednesday_sales + debit_thursday_sales + debit_friday_sales + debit_saturday_sales + debit_sunday_sales
        total_debit_transactions = debit_monday_transactions + debit_tuesday_transactions + debit_wednesday_transactions + debit_thursday_transactions + debit_friday_transactions + debit_saturday_transactions + debit_sunday_transactions
        total_upi_sales = upi_monday_sales + upi_tuesday_sales + upi_wednesday_sales + upi_thursday_sales + upi_friday_sales + upi_saturday_sales + upi_sunday_sales
        total_upi_transactions = upi_monday_transactions + upi_tuesday_transactions + upi_wednesday_transactions + upi_thursday_transactions + upi_friday_transactions + upi_saturday_transactions + upi_sunday_transactions
        total_paytm_sales = paytm_monday_sales + paytm_tuesday_sales + paytm_wednesday_sales + paytm_thursday_sales + paytm_friday_sales + paytm_saturday_sales + paytm_sunday_sales
        total_paytm_transactions = paytm_monday_transactions + paytm_tuesday_transactions + paytm_wednesday_transactions + paytm_thursday_transactions + paytm_friday_transactions + paytm_saturday_transactions + paytm_sunday_transactions
        total_phone_sales = phone_monday_sales + phone_tuesday_sales + phone_wednesday_sales + phone_thursday_sales + phone_friday_sales + phone_saturday_sales + phone_sunday_sales
        total_phone_transactions = phone_monday_transactions + phone_tuesday_transactions + phone_wednesday_transactions + phone_thursday_transactions + phone_friday_transactions + phone_saturday_transactions + phone_sunday_transactions
        total_free_sales = free_monday_sales + free_tuesday_sales + free_wednesday_sales + free_thursday_sales + free_friday_sales + free_saturday_sales + free_sunday_sales
        total_free_transactions = free_monday_transactions + free_tuesday_transactions + free_wednesday_transactions + free_thursday_transactions + free_friday_transactions + free_saturday_transactions + free_sunday_transactions
        total_sodexo_sales = sodexo_monday_sales + sodexo_tuesday_sales + sodexo_wednesday_sales + sodexo_thursday_sales + sodexo_friday_sales + sodexo_saturday_sales + sodexo_sunday_sales
        total_sodexo_transactions = sodexo_monday_transactions + sodexo_tuesday_transactions + sodexo_wednesday_transactions + sodexo_thursday_transactions + sodexo_friday_transactions + sodexo_saturday_transactions + sodexo_sunday_transactions
        total_samsung_sales = samsung_monday_sales + samsung_tuesday_sales + samsung_wednesday_sales + samsung_thursday_sales + samsung_friday_sales + samsung_saturday_sales + samsung_sunday_sales
        total_samsung_transactions = samsung_monday_transactions + samsung_tuesday_transactions + samsung_wednesday_transactions + samsung_thursday_transactions + samsung_friday_transactions + samsung_saturday_transactions + samsung_sunday_transactions
        total_apple_sales = apple_monday_sales + apple_tuesday_sales + apple_wednesday_sales + apple_thursday_sales + apple_friday_sales + apple_saturday_sales + apple_sunday_sales
        total_apple_transactions = apple_monday_transactions + apple_tuesday_transactions + apple_wednesday_transactions + apple_thursday_transactions + apple_friday_transactions + apple_saturday_transactions + apple_sunday_transactions

        # report_lines = profit_loss.get_account_lines(data['form'])
        # report_lines = self.env['financial.report'].get_account_lines(data)
        data.update({'monday_sales_gross': round(monday_sales_gross, 2),
                     'tuesday_sales_gross': round(tuesday_sales_gross, 2),
                     'wednesday_sales_gross': round(wednesday_sales_gross, 2),
                     'thursday_sales_gross': round(thursday_sales_gross, 2),
                     'friday_sales_gross': round(friday_sales_gross, 2),
                     'saturday_sales_gross': round(saturday_sales_gross, 2),
                     'sunday_sales_gross': round(sunday_sales_gross, 2),
                     'sales_gross_total': round(sales_gross_total, 2),
                     'total_transactions': total_transactions,
                     'total_spmh': round(total_spmh, 2),
                     'total_refund': round(total_refund, 2),
                     'total_employee_meals': round(total_employee_meals, 2),
                     'monday_sales_net': monday_sales_net,
                     'tuesday_sales_net': tuesday_sales_net,
                     'wednesday_sales_net': wednesday_sales_net,
                     'thursday_sales_net': thursday_sales_net,
                     'friday_sales_net': friday_sales_net,
                     'saturday_sales_net': saturday_sales_net,
                     'sunday_sales_net': sunday_sales_net,
                     'total_sales_net': total_sales_net,
                     'monday_transactions': monday_transactions,
                     'tuesday_transactions': tuesday_transactions,
                     'wednesday_transactions': wednesday_transactions,
                     'thursday_transactions': thursday_transactions,
                     'friday_transactions': friday_transactions,
                     'saturday_transactions': saturday_transactions,
                     'sunday_transactions': sunday_transactions,
                     'monday_employees': round(monday_employees, 2),
                     'tuesday_employees': round(tuesday_employees, 2),
                     'wednesday_employees': round(wednesday_employees, 2),
                     'thursday_employees': round(thursday_employees, 2),
                     'friday_employees': round(friday_employees, 2),
                     'saturday_employees': round(saturday_employees, 2),
                     'sunday_employees': round(sunday_employees, 2),
                     'monday_refund_amount': round(monday_refund_amount, 2),
                     'tuesday_refund_amount': round(tuesday_refund_amount, 2),
                     'wednesday_refund_amount': round(wednesday_refund_amount, 2),
                     'thursday_refund_amount': round(thursday_refund_amount, 2),
                     'friday_refund_amount': round(friday_refund_amount, 2),
                     'saturday_refund_amount': round(saturday_refund_amount, 2),
                     'sunday_refund_amount': round(sunday_refund_amount, 2),
                     'promo_amount': promo_amount,
                     'monday_employee_meals': round(monday_employee_meals, 2),
                     'tuesday_employee_meals': round(tuesday_employee_meals, 2),
                     'wednesday_employee_meals': round(wednesday_employee_meals, 2),
                     'thursday_employee_meals': round(thursday_employee_meals, 2),
                     'friday_employee_meals': round(friday_employee_meals, 2),
                     'saturday_employee_meals': round(saturday_employee_meals, 2),
                     'sunday_employee_meals': round(sunday_employee_meals, 2),
                     'cash_monday_sales': round(cash_monday_sales, 2),
                     'cash_monday_transactions': cash_monday_transactions,
                     'cash_tuesday_sales': round(cash_tuesday_sales, 2),
                     'cash_tuesday_transactions': cash_tuesday_transactions,
                     'cash_wednesday_sales': round(cash_wednesday_sales, 2),
                     'cash_wednesday_transactions': cash_wednesday_transactions,
                     'cash_thursday_sales': round(cash_thursday_sales, 2),
                     'cash_thursday_transactions': cash_thursday_transactions,
                     'cash_friday_sales': round(cash_friday_sales, 2),
                     'cash_friday_transactions': cash_friday_transactions,
                     'cash_saturday_sales': round(cash_saturday_sales, 2),
                     'cash_saturday_transactions': cash_saturday_transactions,
                     'cash_sunday_sales': round(cash_sunday_sales, 2),
                     'cash_sunday_transactions': cash_sunday_transactions,
                     'credit_monday_sales': round(credit_monday_sales, 2),
                     'credit_monday_transactions': credit_monday_transactions,
                     'credit_tuesday_sales': round(credit_tuesday_sales, 2),
                     'credit_tuesday_transactions': credit_tuesday_transactions,
                     'credit_wednesday_sales': round(credit_wednesday_sales, 2),
                     'credit_wednesday_transactions': credit_wednesday_transactions,
                     'credit_thursday_sales': round(credit_thursday_sales, 2),
                     'credit_thursday_transactions': credit_thursday_transactions,
                     'credit_friday_sales': round(credit_friday_sales, 2),
                     'credit_friday_transactions': credit_friday_transactions,
                     'credit_saturday_sales': round(credit_saturday_sales, 2),
                     'credit_saturday_transactions': credit_saturday_transactions,
                     'credit_sunday_sales': round(credit_sunday_sales, 2),
                     'credit_sunday_transactions': credit_sunday_transactions,
                     'debit_monday_sales': round(debit_monday_sales, 2),
                     'debit_monday_transactions': debit_monday_transactions,
                     'debit_tuesday_sales': round(debit_tuesday_sales, 2),
                     'debit_tuesday_transactions': debit_tuesday_transactions,
                     'debit_wednesday_sales': round(debit_wednesday_sales, 2),
                     'debit_wednesday_transactions': debit_wednesday_transactions,
                     'debit_thursday_sales': round(debit_thursday_sales, 2),
                     'debit_thursday_transactions': debit_thursday_transactions,
                     'debit_friday_sales': round(debit_friday_sales, 2),
                     'debit_friday_transactions': debit_friday_transactions,
                     'debit_saturday_sales': round(debit_saturday_sales, 2),
                     'debit_saturday_transactions': debit_saturday_transactions,
                     'debit_sunday_sales': round(debit_sunday_sales, 2),
                     'debit_sunday_transactions': debit_sunday_transactions,
                     'upi_monday_sales': round(upi_monday_sales, 2),
                     'upi_monday_transactions': upi_monday_transactions,
                     'upi_tuesday_sales': round(upi_tuesday_sales, 2),
                     'upi_tuesday_transactions': upi_tuesday_transactions,
                     'upi_wednesday_sales': round(upi_wednesday_sales, 2),
                     'upi_wednesday_transactions': upi_wednesday_transactions,
                     'upi_thursday_sales': round(upi_thursday_sales, 2),
                     'upi_thursday_transactions': upi_thursday_transactions,
                     'upi_friday_sales': round(upi_friday_sales, 2),
                     'upi_friday_transactions': upi_friday_transactions,
                     'upi_saturday_sales': round(upi_saturday_sales, 2),
                     'upi_saturday_transactions': upi_saturday_transactions,
                     'upi_sunday_sales': round(upi_sunday_sales, 2),
                     'upi_sunday_transactions': upi_sunday_transactions,
                     'paytm_monday_sales': round(paytm_monday_sales, 2),
                     'paytm_monday_transactions': paytm_monday_transactions,
                     'paytm_tuesday_sales': round(paytm_tuesday_sales, 2),
                     'paytm_tuesday_transactions': paytm_tuesday_transactions,
                     'paytm_wednesday_sales': round(paytm_wednesday_sales, 2),
                     'paytm_wednesday_transactions': paytm_wednesday_transactions,
                     'paytm_thursday_sales': round(paytm_thursday_sales, 2),
                     'paytm_thursday_transactions': paytm_thursday_transactions,
                     'paytm_friday_sales': round(paytm_friday_sales, 2),
                     'paytm_friday_transactions': paytm_friday_transactions,
                     'paytm_saturday_sales': round(paytm_saturday_sales, 2),
                     'paytm_saturday_transactions': paytm_saturday_transactions,
                     'paytm_sunday_sales': round(paytm_sunday_sales, 2),
                     'paytm_sunday_transactions': paytm_sunday_transactions,
                     'phone_monday_sales': round(phone_monday_sales, 2),
                     'phone_monday_transactions': phone_monday_transactions,
                     'phone_tuesday_sales': round(phone_tuesday_sales, 2),
                     'phone_tuesday_transactions': phone_tuesday_transactions,
                     'phone_wednesday_sales': round(phone_wednesday_sales, 2),
                     'phone_wednesday_transactions': phone_wednesday_transactions,
                     'phone_thursday_sales': round(phone_thursday_sales, 2),
                     'phone_thursday_transactions': phone_thursday_transactions,
                     'phone_friday_sales': round(phone_friday_sales, 2),
                     'phone_friday_transactions': phone_friday_transactions,
                     'phone_saturday_sales': round(phone_saturday_sales, 2),
                     'phone_saturday_transactions': phone_saturday_transactions,
                     'phone_sunday_sales': round(phone_sunday_sales, 2),
                     'phone_sunday_transactions': phone_sunday_transactions,
                     'free_monday_sales': round(free_monday_sales, 2),
                     'free_monday_transactions': free_monday_transactions,
                     'free_tuesday_sales': round(free_tuesday_sales, 2),
                     'free_tuesday_transactions': free_tuesday_transactions,
                     'free_wednesday_sales': round(free_wednesday_sales, 2),
                     'free_wednesday_transactions': free_wednesday_transactions,
                     'free_thursday_sales': round(free_thursday_sales, 2),
                     'free_thursday_transactions': free_thursday_transactions,
                     'free_friday_sales': round(free_friday_sales, 2),
                     'free_friday_transactions': free_friday_transactions,
                     'free_saturday_sales': round(free_saturday_sales, 2),
                     'free_saturday_transactions': free_saturday_transactions,
                     'free_sunday_sales': round(free_sunday_sales, 2),
                     'free_sunday_transactions': free_sunday_transactions,
                     'sodexo_monday_sales': round(sodexo_monday_sales, 2),
                     'sodexo_monday_transactions': sodexo_monday_transactions,
                     'sodexo_tuesday_sales': round(sodexo_tuesday_sales, 2),
                     'sodexo_tuesday_transactions': sodexo_tuesday_transactions,
                     'sodexo_wednesday_sales': round(sodexo_wednesday_sales, 2),
                     'sodexo_wednesday_transactions': sodexo_wednesday_transactions,
                     'sodexo_thursday_sales': round(sodexo_thursday_sales, 2),
                     'sodexo_thursday_transactions': sodexo_thursday_transactions,
                     'sodexo_friday_sales': round(sodexo_friday_sales, 2),
                     'sodexo_friday_transactions': sodexo_friday_transactions,
                     'sodexo_saturday_sales': round(sodexo_saturday_sales, 2),
                     'sodexo_saturday_transactions': sodexo_saturday_transactions,
                     'sodexo_sunday_sales': round(sodexo_sunday_sales, 2),
                     'sodexo_sunday_transactions': sodexo_sunday_transactions,
                     'samsung_monday_sales': round(samsung_monday_sales, 2),
                     'samsung_monday_transactions': samsung_monday_transactions,
                     'samsung_tuesday_sales': round(samsung_tuesday_sales, 2),
                     'samsung_tuesday_transactions': samsung_tuesday_transactions,
                     'samsung_wednesday_sales': round(samsung_wednesday_sales, 2),
                     'samsung_wednesday_transactions': samsung_wednesday_transactions,
                     'samsung_thursday_sales': round(samsung_thursday_sales, 2),
                     'samsung_thursday_transactions': samsung_thursday_transactions,
                     'samsung_friday_sales': round(samsung_friday_sales, 2),
                     'samsung_friday_transactions': samsung_friday_transactions,
                     'samsung_saturday_sales': round(samsung_saturday_sales, 2),
                     'samsung_saturday_transactions': samsung_saturday_transactions,
                     'samsung_sunday_sales': round(samsung_sunday_sales, 2),
                     'samsung_sunday_transactions': samsung_sunday_transactions,
                     'apple_monday_sales': round(apple_monday_sales, 2),
                     'apple_monday_transactions': apple_monday_transactions,
                     'apple_tuesday_sales': round(apple_tuesday_sales, 2),
                     'apple_tuesday_transactions': apple_tuesday_transactions,
                     'apple_wednesday_sales': round(apple_wednesday_sales, 2),
                     'apple_wednesday_transactions': apple_wednesday_transactions,
                     'apple_thursday_sales': round(apple_thursday_sales, 2),
                     'apple_thursday_transactions': apple_thursday_transactions,
                     'apple_friday_sales': round(apple_friday_sales, 2),
                     'apple_friday_transactions': apple_friday_transactions,
                     'apple_saturday_sales': round(apple_saturday_sales, 2),
                     'apple_saturday_transactions': apple_saturday_transactions,
                     'apple_sunday_sales': round(apple_sunday_sales, 2),
                     'apple_sunday_transactions': apple_sunday_transactions,
                     'total_cash_sales': round(total_cash_sales, 2),
                     'total_cash_transactions': total_cash_transactions,
                     'total_credit_sales': round(total_credit_sales, 2),
                     'total_credit_transactions': total_credit_transactions,
                     'total_debit_sales': round(total_debit_sales, 2),
                     'total_debit_transactions': total_debit_transactions,
                     'total_upi_sales': round(total_upi_sales, 2),
                     'total_upi_transactions': total_upi_transactions,
                     'total_paytm_sales': round(total_paytm_sales, 2),
                     'total_paytm_transactions': total_paytm_transactions,
                     'total_phone_sales': round(total_phone_sales, 2),
                     'total_phone_transactions': total_phone_transactions,
                     'total_free_sales': round(total_free_sales, 2),
                     'total_free_transactions': total_free_transactions,
                     'total_sodexo_sales': round(total_sodexo_sales, 2),
                     'total_sodexo_transactions': total_sodexo_transactions,
                     'total_samsung_sales': round(total_samsung_sales, 2),
                     'total_samsung_transactions': total_samsung_transactions,
                     'total_apple_sales': round(total_apple_sales, 2),
                     'total_apple_transactions': total_apple_transactions,
                     })
        return data


class SalesReportXlsx(models.AbstractModel):
    _name = 'report.sales_report.report_pos_xlsx'
    _inherit = "report.report_xlsx.abstract"

    def get_days(self, this_week_start_time, this_week_end_time, day):
        return [this_week_start_time + timedelta(days=x) for x in
                range((this_week_end_time - this_week_start_time).days + 1) if
                (this_week_start_time + timedelta(days=x)).weekday() == time.strptime(day, '%A').tm_wday]

    def find_key(self, input_dict, value):
        for key, val in input_dict.items():
            if val == value:
                return key
        return "None"

    def generate_xlsx_report(self, workbook, data, records, session_ids=False):
        tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        worksheet = workbook.add_worksheet('Sales Report')
        start = records.start_date.strftime('%m-%d-%Y')
        end = records.end_date.strftime('%m-%d-%Y')
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
                                               'size': 12})
        heading_format3 = workbook.add_format({'align': 'right',
                                               'valign': 'right',
                                               'size': 10})
        heading_format4 = workbook.add_format({'align': 'center',
                                               'valign': 'vcenter',
                                               'bold': True, 'size': 10,
                                               'bg_color': '#7ecfd6'})
        format5 = workbook.add_format({'font_size': 10, 'align': 'center', 'bg_color': '#7ecfd6'})

        worksheet.set_column(0, 0, 30)
        worksheet.set_column(1, 1, 10)
        worksheet.set_column(2, 2, 10)
        worksheet.set_column(3, 3, 10)
        worksheet.set_column(4, 4, 10)
        worksheet.set_column(5, 5, 10)
        worksheet.set_column(6, 6, 10)
        worksheet.set_column(7, 7, 10)
        worksheet.set_column(8, 8, 10)

        worksheet.write(0, 1, "Monday", heading_format)
        worksheet.write(0, 2, "Tuesday", heading_format)
        worksheet.write(0, 3, "Wednesday", heading_format)
        worksheet.write(0, 4, "Thursday", heading_format)
        worksheet.write(0, 5, "Friday", heading_format)
        worksheet.write(0, 6, "Saturday", heading_format)
        worksheet.write(0, 7, "Sunday", heading_format)
        worksheet.write(0, 8, "Week Total", heading_format)

        worksheet.write(3, 0, "Sales Gross", heading_format2)
        worksheet.write(4, 0, "Sales NET", heading_format2)
        worksheet.write(5, 0, "Transactions", heading_format2)
        worksheet.write(6, 0, "SPMH", heading_format2)
        worksheet.write(7, 0, "Refund Amount", heading_format2)
        worksheet.write(8, 0, "Promo Amount", heading_format2)
        worksheet.write(9, 0, "Employee Meals", heading_format2)

        worksheet.write(12, 0, "", heading_format)
        worksheet.write(12, 1, "Monday", heading_format)
        worksheet.write(12, 2, "Tuesday", heading_format)
        worksheet.write(12, 3, "Wednesday", heading_format)
        worksheet.write(12, 4, "Thursday", heading_format)
        worksheet.write(12, 5, "Friday", heading_format)
        worksheet.write(12, 6, "Saturday", heading_format)
        worksheet.write(12, 7, "Sunday", heading_format)
        worksheet.write(12, 8, "Week Total", heading_format)

        worksheet.write(14, 0, "Cash", heading_format4)
        worksheet.write(15, 0, "Sales", heading_format3)
        worksheet.write(16, 0, "Transactions", heading_format3)
        worksheet.write(17, 0, "Credit Card", heading_format4)
        worksheet.write(18, 0, "Sales", heading_format3)
        worksheet.write(19, 0, "Transactions", heading_format3)
        worksheet.write(20, 0, "Debit Card", heading_format4)
        worksheet.write(21, 0, "Sales", heading_format3)
        worksheet.write(22, 0, "Transactions", heading_format3)
        worksheet.write(23, 0, "UPI", heading_format4)
        worksheet.write(24, 0, "Sales", heading_format3)
        worksheet.write(25, 0, "Transactions", heading_format3)
        worksheet.write(26, 0, "PayTM Wallet", heading_format4)
        worksheet.write(27, 0, "Sales", heading_format3)
        worksheet.write(28, 0, "Transactions", heading_format3)
        worksheet.write(29, 0, "PhonePay Wallet", heading_format4)
        worksheet.write(30, 0, "Sales", heading_format3)
        worksheet.write(31, 0, "Transactions", heading_format3)
        worksheet.write(32, 0, "Freecharge", heading_format4)
        worksheet.write(33, 0, "Sales", heading_format3)
        worksheet.write(34, 0, "Transactions", heading_format3)
        worksheet.write(35, 0, "Sodexo Cards", heading_format4)
        worksheet.write(36, 0, "Sales", heading_format3)
        worksheet.write(37, 0, "Transactions", heading_format3)
        worksheet.write(38, 0, "Samsung Pay", heading_format4)
        worksheet.write(39, 0, "Sales", heading_format3)
        worksheet.write(40, 0, "Transactions", heading_format3)
        worksheet.write(41, 0, "Apple Pay", heading_format4)
        worksheet.write(42, 0, "Sales", heading_format3)
        worksheet.write(43, 0, "Transactions", heading_format3)

        sale_domain = [('state', 'in', ['sale'])]
        pos_domain = [('state', 'in', ['paid', 'done', 'invoiced'])]
        tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        if data.get('date_start'):
            date_start = fields.Datetime.from_string(data.get('date_start'))
        else:
            # start by default today 00:00:00
            user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
            date_start = today.astimezone(pytz.timezone('UTC'))

        if data.get('date_end'):
            date_stop = fields.Datetime.from_string(data.get('date_end'))
            # avoid a date_stop smaller than date_start
            if date_stop < date_start:
                date_stop = date_start + timedelta(days=1, seconds=-1)
        else:
            # stop by default today 23:59:59
            date_stop = date_start + timedelta(days=1, seconds=-1)

        domain = AND([sale_domain,
                      [('date_order', '>=', date_start.date()),
                       ('date_order', '<=', date_stop.date())]
                      ])
        domain_pos = AND([pos_domain,
                          [('date_order', '>=', date_start.date()),
                           ('date_order', '<=', date_stop.date())]
                          ])

        # if (date_stop.date() - date_start.date()).days > 6:
        #     raise ValidationError(_("Incorrect Week Interval"))

        # if (date_start.date() - date_stop.date()).days < 0:
        #     raise ValidationError(_("Incorrect Week Interval"))

        sales_orders = self.env['sale.order'].search(domain)
        pos_orders = self.env['pos.order'].search(domain_pos)
        pos_days = {}
        sale_days = {}
        day_list = [0, 1, 2, 3, 4, 5, 6]
        for i in day_list:
            pos_list = pos_orders.filtered(
                lambda line: line.date_order.astimezone(tz).weekday() == i)
            pos_days[i] = pos_list
        for k in day_list:
            sales_list = sales_orders.filtered(
                lambda line: line.date_order.astimezone(tz).weekday() == k
            )
            sale_days[k] = sales_list
        monday_sales_gross = 0.0
        tuesday_sales_gross = 0.0
        wednesday_sales_gross = 0.0
        thursday_sales_gross = 0.0
        friday_sales_gross = 0.0
        saturday_sales_gross = 0.0
        sunday_sales_gross = 0.0
        monday_transactions = len(pos_days.get(0)) + len(sale_days.get(0))
        tuesday_transactions = len(pos_days.get(1)) + len(sale_days.get(1))
        wednesday_transactions = len(pos_days.get(2)) + len(sale_days.get(2))
        thursday_transactions = len(pos_days.get(3)) + len(sale_days.get(3))
        friday_transactions = len(pos_days.get(4)) + len(sale_days.get(4))
        saturday_transactions = len(pos_days.get(5)) + len(sale_days.get(5))
        sunday_transactions = len(pos_days.get(6)) + len(sale_days.get(6))

        cash_monday_sales = 0.0
        cash_mo = []
        cash_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_monday_sales += rec.amount_total
                    cash_mo.append(rec)
                    cash_monday_transactions = len(cash_mo)
        cash_tuesday_sales = 0.0
        cash_tu = []
        cash_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_tuesday_sales += rec.amount_total
                    cash_tu.append(rec)
                    cash_tuesday_transactions = len(cash_tu)
        cash_wednesday_sales = 0.0
        cash_wed = []
        cash_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_wednesday_sales += rec.amount_total
                    cash_wed.append(rec)
                    cash_wednesday_transactions = len(cash_wed)
        cash_thursday_sales = 0.0
        cash_th = []
        cash_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_thursday_sales += rec.amount_total
                    cash_th.append(rec)
                    cash_thursday_transactions = len(cash_th)
        cash_friday_sales = 0.0
        cash_fri = []
        cash_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_friday_sales += rec.amount_total
                    cash_fri.append(rec)
                    cash_friday_transactions = len(cash_fri)
        cash_saturday_sales = 0.0
        cash_sat = []
        cash_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_saturday_sales += rec.amount_total
                    cash_sat.append(rec)
                    cash_saturday_transactions = len(cash_sat)
        cash_sunday_sales = 0.0
        cash_sun = []
        cash_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Cash':
                    cash_sunday_sales += rec.amount_total
                    cash_sun.append(rec)
                    cash_sunday_transactions = len(cash_sun)

        credit_monday_sales = 0.0
        credit_mo = []
        credit_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_monday_sales += rec.amount_total
                    credit_mo.append(rec)
                    credit_monday_transactions = len(credit_mo)
        credit_tuesday_sales = 0.0
        credit_tu = []
        credit_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_tuesday_sales += rec.amount_total
                    credit_tu.append(rec)
                    credit_tuesday_transactions = len(credit_tu)
        credit_wednesday_sales = 0.0
        credit_wed = []
        credit_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_wednesday_sales += rec.amount_total
                    credit_wed.append(rec)
                    credit_wednesday_transactions = len(credit_wed)
        credit_thursday_sales = 0.0
        credit_th = []
        credit_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_thursday_sales += rec.amount_total
                    credit_th.append(rec)
                    credit_thursday_transactions = len(credit_th)
        credit_friday_sales = 0.0
        credit_fri = []
        credit_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_friday_sales += rec.amount_total
                    credit_fri.append(rec)
                    credit_friday_transactions = len(credit_fri)
        credit_saturday_sales = 0.0
        credit_sat = []
        credit_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_saturday_sales += rec.amount_total
                    credit_sat.append(rec)
                    credit_saturday_transactions = len(credit_sat)
        credit_sunday_sales = 0.0
        credit_sun = []
        credit_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Stripe':
                    credit_sunday_sales += rec.amount_total
                    credit_sun.append(rec)
                    credit_sunday_transactions = len(credit_sun)

        debit_monday_sales = 0.0
        debit_mo = []
        debit_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_monday_sales += rec.amount_total
                    debit_mo.append(rec)
                    debit_monday_transactions = len(debit_mo)
        debit_tuesday_sales = 0.0
        debit_tu = []
        debit_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_tuesday_sales += rec.amount_total
                    debit_tu.append(rec)
                    debit_tuesday_transactions = len(debit_tu)
        debit_wednesday_sales = 0.0
        debit_wed = []
        debit_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_wednesday_sales += rec.amount_total
                    debit_wed.append(rec)
                    debit_wednesday_transactions = len(debit_wed)
        debit_thursday_sales = 0.0
        debit_th = []
        debit_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_thursday_sales += rec.amount_total
                    debit_th.append(rec)
                    debit_thursday_transactions = len(debit_th)
        debit_friday_sales = 0.0
        debit_fri = []
        debit_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_friday_sales += rec.amount_total
                    debit_fri.append(rec)
                    debit_friday_transactions = len(debit_fri)
        debit_saturday_sales = 0.0
        debit_sat = []
        debit_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_saturday_sales += rec.amount_total
                    debit_sat.append(rec)
                    debit_saturday_transactions = len(debit_sat)
        debit_sunday_sales = 0.0
        debit_sun = []
        debit_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Debit Card':
                    debit_sunday_sales += rec.amount_total
                    debit_sun.append(rec)
                    debit_sunday_transactions = len(debit_sun)

        upi_monday_sales = 0.0
        upi_mo = []
        upi_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_monday_sales += rec.amount_total
                    upi_mo.append(rec)
                    upi_monday_transactions = len(upi_mo)
        upi_tuesday_sales = 0.0
        upi_tu = []
        upi_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_tuesday_sales += rec.amount_total
                    upi_tu.append(rec)
                    cash_tuesday_transactions = len(upi_tu)
        upi_wednesday_sales = 0.0
        upi_wed = []
        upi_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_wednesday_sales += rec.amount_total
                    upi_wed.append(rec)
                    upi_wednesday_transactions = len(upi_wed)
        upi_thursday_sales = 0.0
        upi_th = []
        upi_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_thursday_sales += rec.amount_total
                    upi_th.append(rec)
                    upi_thursday_transactions = len(upi_th)
        upi_friday_sales = 0.0
        upi_fri = []
        upi_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_friday_sales += rec.amount_total
                    upi_fri.append(rec)
                    upi_friday_transactions = len(upi_fri)
        upi_saturday_sales = 0.0
        upi_sat = []
        upi_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_saturday_sales += rec.amount_total
                    upi_sat.append(rec)
                    upi_saturday_transactions = len(upi_sat)
        upi_sunday_sales = 0.0
        upi_sun = []
        upi_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'UPI':
                    upi_sunday_sales += rec.amount_total
                    upi_sun.append(rec)
                    upi_sunday_transactions = len(upi_sun)

        paytm_monday_sales = 0.0
        paytm_mo = []
        paytm_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_monday_sales += rec.amount_total
                    paytm_mo.append(rec)
                    paytm_monday_transactions = len(paytm_mo)
        paytm_tuesday_sales = 0.0
        paytm_tu = []
        paytm_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_tuesday_sales += rec.amount_total
                    paytm_tu.append(rec)
                    cash_tuesday_transactions = len(paytm_tu)
        paytm_wednesday_sales = 0.0
        paytm_wed = []
        paytm_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_wednesday_sales += rec.amount_total
                    paytm_wed.append(rec)
                    paytm_wednesday_transactions = len(paytm_wed)
        paytm_thursday_sales = 0.0
        paytm_th = []
        paytm_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_thursday_sales += rec.amount_total
                    paytm_th.append(rec)
                    paytm_thursday_transactions = len(paytm_th)
        paytm_friday_sales = 0.0
        paytm_fri = []
        paytm_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_friday_sales += rec.amount_total
                    paytm_fri.append(rec)
                    paytm_friday_transactions = len(paytm_fri)
        paytm_saturday_sales = 0.0
        paytm_sat = []
        paytm_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_saturday_sales += rec.amount_total
                    paytm_sat.append(rec)
                    paytm_saturday_transactions = len(paytm_sat)
        paytm_sunday_sales = 0.0
        paytm_sun = []
        paytm_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PayTM Wallet':
                    paytm_sunday_sales += rec.amount_total
                    paytm_sun.append(rec)
                    paytm_sunday_transactions = len(paytm_sun)

        phone_monday_sales = 0.0
        phone_mo = []
        phone_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_monday_sales += rec.amount_total
                    phone_mo.append(rec)
                    phone_monday_transactions = len(phone_mo)
        phone_tuesday_sales = 0.0
        phone_tu = []
        phone_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_tuesday_sales += rec.amount_total
                    phone_tu.append(rec)
                    cash_tuesday_transactions = len(phone_tu)
        phone_wednesday_sales = 0.0
        phone_wed = []
        phone_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_wednesday_sales += rec.amount_total
                    phone_wed.append(rec)
                    phone_wednesday_transactions = len(phone_wed)
        phone_thursday_sales = 0.0
        phone_th = []
        phone_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_thursday_sales += rec.amount_total
                    phone_th.append(rec)
                    phone_thursday_transactions = len(phone_th)
        phone_friday_sales = 0.0
        phone_fri = []
        phone_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_friday_sales += rec.amount_total
                    phone_fri.append(rec)
                    phone_friday_transactions = len(phone_fri)
        phone_saturday_sales = 0.0
        phone_sat = []
        phone_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_saturday_sales += rec.amount_total
                    phone_sat.append(rec)
                    phone_saturday_transactions = len(phone_sat)
        phone_sunday_sales = 0.0
        phone_sun = []
        phone_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'PhonePe Wallet':
                    phone_sunday_sales += rec.amount_total
                    phone_sun.append(rec)
                    phone_sunday_transactions = len(phone_sun)

        free_monday_sales = 0.0
        free_mo = []
        free_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_monday_sales += rec.amount_total
                    free_mo.append(rec)
                    free_monday_transactions = len(free_mo)
        free_tuesday_sales = 0.0
        free_tu = []
        free_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_tuesday_sales += rec.amount_total
                    free_tu.append(rec)
                    cash_tuesday_transactions = len(free_tu)
        free_wednesday_sales = 0.0
        free_wed = []
        free_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_wednesday_sales += rec.amount_total
                    free_wed.append(rec)
                    free_wednesday_transactions = len(free_wed)
        free_thursday_sales = 0.0
        free_th = []
        free_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_thursday_sales += rec.amount_total
                    free_th.append(rec)
                    free_thursday_transactions = len(free_th)
        free_friday_sales = 0.0
        free_fri = []
        free_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_friday_sales += rec.amount_total
                    free_fri.append(rec)
                    free_friday_transactions = len(free_fri)
        free_saturday_sales = 0.0
        free_sat = []
        free_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_saturday_sales += rec.amount_total
                    free_sat.append(rec)
                    free_saturday_transactions = len(free_sat)
        free_sunday_sales = 0.0
        free_sun = []
        free_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Freecharge':
                    free_sunday_sales += rec.amount_total
                    free_sun.append(rec)
                    free_sunday_transactions = len(free_sun)

        sodexo_monday_sales = 0.0
        sodexo_mo = []
        sodexo_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_monday_sales += rec.amount_total
                    sodexo_mo.append(rec)
                    sodexo_monday_transactions = len(sodexo_mo)
        sodexo_tuesday_sales = 0.0
        sodexo_tu = []
        sodexo_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_tuesday_sales += rec.amount_total
                    sodexo_tu.append(rec)
                    cash_tuesday_transactions = len(sodexo_tu)
        sodexo_wednesday_sales = 0.0
        sodexo_wed = []
        sodexo_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_wednesday_sales += rec.amount_total
                    sodexo_wed.append(rec)
                    sodexo_wednesday_transactions = len(sodexo_wed)
        sodexo_thursday_sales = 0.0
        sodexo_th = []
        sodexo_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_thursday_sales += rec.amount_total
                    sodexo_th.append(rec)
                    sodexo_thursday_transactions = len(sodexo_th)
        sodexo_friday_sales = 0.0
        sodexo_fri = []
        sodexo_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_friday_sales += rec.amount_total
                    sodexo_fri.append(rec)
                    sodexo_friday_transactions = len(sodexo_fri)
        sodexo_saturday_sales = 0.0
        sodexo_sat = []
        sodexo_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_saturday_sales += rec.amount_total
                    sodexo_sat.append(rec)
                    sodexo_saturday_transactions = len(sodexo_sat)
        sodexo_sunday_sales = 0.0
        sodexo_sun = []
        sodexo_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Sodexo Cards':
                    sodexo_sunday_sales += rec.amount_total
                    sodexo_sun.append(rec)
                    sodexo_sunday_transactions = len(sodexo_sun)

        samsung_monday_sales = 0.0
        samsung_mo = []
        samsung_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_monday_sales += rec.amount_total
                    samsung_mo.append(rec)
                    samsung_monday_transactions = len(samsung_mo)
        samsung_tuesday_sales = 0.0
        samsung_tu = []
        samsung_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_tuesday_sales += rec.amount_total
                    samsung_tu.append(rec)
                    cash_tuesday_transactions = len(samsung_tu)
        samsung_wednesday_sales = 0.0
        samsung_wed = []
        samsung_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_wednesday_sales += rec.amount_total
                    samsung_wed.append(rec)
                    samsung_wednesday_transactions = len(samsung_wed)
        samsung_thursday_sales = 0.0
        samsung_th = []
        samsung_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_thursday_sales += rec.amount_total
                    samsung_th.append(rec)
                    samsung_thursday_transactions = len(samsung_th)
        samsung_friday_sales = 0.0
        samsung_fri = []
        samsung_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_friday_sales += rec.amount_total
                    samsung_fri.append(rec)
                    samsung_friday_transactions = len(samsung_fri)
        samsung_saturday_sales = 0.0
        samsung_sat = []
        samsung_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_saturday_sales += rec.amount_total
                    samsung_sat.append(rec)
                    samsung_saturday_transactions = len(samsung_sat)
        samsung_sunday_sales = 0.0
        samsung_sun = []
        samsung_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Samsung Pay':
                    samsung_sunday_sales += rec.amount_total
                    samsung_sun.append(rec)
                    samsung_sunday_transactions = len(samsung_sun)

        apple_monday_sales = 0.0
        apple_mo = []
        apple_monday_transactions = 0.0
        for rec in pos_days.get(0):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_monday_sales += rec.amount_total
                    apple_mo.append(rec)
                    apple_monday_transactions = len(apple_mo)
        apple_tuesday_sales = 0.0
        apple_tu = []
        apple_tuesday_transactions = 0.0
        for rec in pos_days.get(1):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_tuesday_sales += rec.amount_total
                    apple_tu.append(rec)
                    cash_tuesday_transactions = len(apple_tu)
        apple_wednesday_sales = 0.0
        apple_wed = []
        apple_wednesday_transactions = 0.0
        for rec in pos_days.get(2):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_wednesday_sales += rec.amount_total
                    apple_wed.append(rec)
                    apple_wednesday_transactions = len(apple_wed)
        apple_thursday_sales = 0.0
        apple_th = []
        apple_thursday_transactions = 0.0
        for rec in pos_days.get(3):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_thursday_sales += rec.amount_total
                    apple_th.append(rec)
                    apple_thursday_transactions = len(apple_th)
        apple_friday_sales = 0.0
        apple_fri = []
        apple_friday_transactions = 0.0
        for rec in pos_days.get(4):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_friday_sales += rec.amount_total
                    apple_fri.append(rec)
                    apple_friday_transactions = len(apple_fri)
        apple_saturday_sales = 0.0
        apple_sat = []
        apple_saturday_transactions = 0.0
        for rec in pos_days.get(5):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_saturday_sales += rec.amount_total
                    apple_sat.append(rec)
                    apple_saturday_transactions = len(apple_sat)
        apple_sunday_sales = 0.0
        apple_sun = []
        apple_sunday_transactions = 0.0
        for rec in pos_days.get(6):
            for pay in rec.payment_ids.payment_method_id:
                if pay.name == 'Apple Pay':
                    apple_sunday_sales += rec.amount_total
                    apple_sun.append(rec)
                    apple_sunday_transactions = len(apple_sun)

        organize_list = {}
        organize = self.env['organize.slot'].search([('create_date', '>=', date_start.date()),
                                                     ('create_date', '<=', date_stop.date())])
        for i in day_list:
            schedule_list = organize.filtered(
                lambda line: line.start_datetime.astimezone(tz).weekday() == i)
            organize_list[i] = schedule_list

        monday_employee_meals = 0.0
        tuesday_employee_meals = 0.0
        wednesday_employee_meals = 0.0
        thursday_employee_meals = 0.0
        friday_employee_meals = 0.0
        saturday_employee_meals = 0.0
        sunday_employee_meals = 0.0
        for emp in pos_days.get(0):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    monday_employee_meals += rec.amount
        for emp in pos_days.get(1):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    tuesday_employee_meals += rec.amount
        for emp in pos_days.get(2):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    wednesday_employee_meals += rec.amount
        for emp in pos_days.get(3):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    thursday_employee_meals += rec.amount
        for emp in pos_days.get(4):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    friday_employee_meals += rec.amount
        for emp in pos_days.get(5):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    saturday_employee_meals += rec.amount
        for emp in pos_days.get(6):
            for rec in emp.payment_ids:
                if rec.payment_method_id.name == 'Employee Meal':
                    sunday_employee_meals += rec.amount

        monday_refund_amount = 0.0
        tuesday_refund_amount = 0.0
        wednesday_refund_amount = 0.0
        thursday_refund_amount = 0.0
        friday_refund_amount = 0.0
        saturday_refund_amount = 0.0
        sunday_refund_amount = 0.0
        for recd in pos_days.get(0):
            if "REFUND" in recd.name:
                monday_refund_amount += recd.amount_total
        for recd in pos_days.get(1):
            if "REFUND" in recd.name:
                tuesday_refund_amount += recd.amount_total
        for recd in pos_days.get(2):
            if "REFUND" in recd.name:
                wednesday_refund_amount += recd.amount_total
        for recd in pos_days.get(3):
            if "REFUND" in recd.name:
                thursday_refund_amount += recd.amount_total
        for recd in pos_days.get(4):
            if "REFUND" in recd.name:
                friday_refund_amount += recd.amount_total
        for recd in pos_days.get(5):
            if "REFUND" in recd.name:
                saturday_refund_amount += recd.amount_total
        for recd in pos_days.get(6):
            if "REFUND" in recd.name:
                sunday_refund_amount += recd.amount_total

        monday_tax = 0.0
        tuesday_tax = 0.0
        wednesday_tax = 0.0
        thursday_tax = 0.0
        friday_tax = 0.0
        saturday_tax = 0.0
        sunday_tax = 0.0
        for rec in pos_days.get(0):
            monday_sales_gross += rec.amount_total
            monday_tax += rec.amount_tax
        for rec in sale_days.get(0):
            monday_sales_gross += rec.amount_total
        for rec in pos_days.get(1):
            tuesday_sales_gross += rec.amount_total
            tuesday_tax += rec.amount_tax
        for rec in sale_days.get(1):
            tuesday_sales_gross += rec.amount_total
        for rec in pos_days.get(2):
            wednesday_sales_gross += rec.amount_total
            wednesday_tax += rec.amount_tax
        for rec in sale_days.get(2):
            wednesday_sales_gross += rec.amount_total
        for rec in pos_days.get(3):
            thursday_sales_gross += rec.amount_total
            thursday_tax += rec.amount_tax
        for rec in sale_days.get(3):
            thursday_sales_gross += rec.amount_total
        for rec in pos_days.get(4):
            friday_sales_gross += rec.amount_total
            friday_tax += rec.amount_tax
        for rec in sale_days.get(4):
            friday_sales_gross += rec.amount_total
        for rec in pos_days.get(5):
            saturday_sales_gross += rec.amount_total
            saturday_tax += rec.amount_tax
        for rec in sale_days.get(5):
            saturday_sales_gross += rec.amount_total
        for rec in pos_days.get(6):
            sunday_sales_gross += rec.amount_total
            sunday_tax += rec.amount_tax
        for rec in sale_days.get(6):
            sunday_sales_gross += rec.amount_total

        monday_sales_net = monday_sales_gross - monday_tax
        tuesday_sales_net = tuesday_sales_gross - tuesday_tax
        wednesday_sales_net = wednesday_sales_gross - wednesday_tax
        thursday_sales_net = thursday_sales_gross - thursday_tax
        friday_sales_net = friday_sales_gross - friday_tax
        saturday_sales_net = saturday_sales_gross - saturday_tax
        sunday_sales_net = sunday_sales_gross - sunday_tax

        monday_employees = 0.0
        tuesday_employees = 0.0
        wednesday_employees = 0.0
        thursday_employees = 0.0
        friday_employees = 0.0
        saturday_employees = 0.0
        sunday_employees = 0.0

        if len(organize_list.get(0).employee_id.ids) != 0:
            monday_employees = monday_sales_gross / len(organize_list.get(0).employee_id.ids)
        if len(organize_list.get(1).employee_id.ids) != 0:
            tuesday_employees = tuesday_sales_gross / len(organize_list.get(1).employee_id.ids)
        if len(organize_list.get(2).employee_id.ids) != 0:
            wednesday_employees = wednesday_sales_gross / len(organize_list.get(2).employee_id.ids)
        if len(organize_list.get(3).employee_id.ids) != 0:
            thursday_employees = thursday_sales_gross / len(organize_list.get(3).employee_id.ids)
        if len(organize_list.get(4).employee_id.ids) != 0:
            friday_employees = friday_sales_gross / len(organize_list.get(4).employee_id.ids)
        if len(organize_list.get(5).employee_id.ids) != 0:
            saturday_employees = saturday_sales_gross / len(organize_list.get(6).employee_id.ids)
        if len(organize_list.get(6).employee_id.ids) != 0:
            sunday_employees = sunday_sales_gross / len(organize_list.get(6).employee_id.ids)

        sales_gross = 0.0
        tax = 0.0
        sales_net = 0.0
        transactions = 0.0
        refund_amount = 0.0
        promo_amount = 0.0
        employee_meals = 0.0
        total_sales_net = monday_sales_net + tuesday_sales_net + wednesday_sales_net + thursday_sales_net + friday_sales_net + saturday_sales_net + sunday_sales_net
        sales_gross_total = monday_sales_gross + tuesday_sales_gross + wednesday_sales_gross + thursday_sales_gross + friday_sales_gross + saturday_sales_gross + sunday_sales_gross
        total_transactions = monday_transactions + tuesday_transactions + wednesday_transactions + thursday_transactions + friday_transactions + saturday_employees + sunday_transactions
        total_spmh = monday_employees + tuesday_employees + wednesday_employees + thursday_employees + friday_employees + saturday_employees + sunday_employees
        total_refund = monday_refund_amount + tuesday_refund_amount + wednesday_refund_amount + thursday_refund_amount + friday_refund_amount + saturday_refund_amount + sunday_refund_amount
        total_employee_meals = monday_employee_meals + tuesday_employee_meals + wednesday_employee_meals + thursday_employee_meals + friday_employee_meals + saturday_refund_amount + sunday_employee_meals
        total_cash_sales = cash_monday_sales + cash_tuesday_sales + cash_wednesday_sales + cash_thursday_sales + cash_friday_sales + cash_saturday_sales + cash_sunday_sales
        total_cash_transactions = cash_monday_transactions + cash_tuesday_transactions + cash_wednesday_transactions + cash_thursday_transactions + cash_friday_transactions + cash_saturday_transactions + cash_sunday_transactions
        total_credit_sales = credit_monday_sales + credit_tuesday_sales + credit_wednesday_sales + credit_thursday_sales + credit_friday_sales + credit_saturday_sales + credit_sunday_sales
        total_credit_transactions = credit_monday_transactions + credit_tuesday_transactions + credit_wednesday_transactions + credit_thursday_transactions + credit_friday_transactions + credit_saturday_transactions + credit_sunday_transactions
        total_debit_sales = debit_monday_sales + debit_tuesday_sales + debit_wednesday_sales + debit_thursday_sales + debit_friday_sales + debit_saturday_sales + debit_sunday_sales
        total_debit_transactions = debit_monday_transactions + debit_tuesday_transactions + debit_wednesday_transactions + debit_thursday_transactions + debit_friday_transactions + debit_saturday_transactions + debit_sunday_transactions
        total_upi_sales = upi_monday_sales + upi_tuesday_sales + upi_wednesday_sales + upi_thursday_sales + upi_friday_sales + upi_saturday_sales + upi_sunday_sales
        total_upi_transactions = upi_monday_transactions + upi_tuesday_transactions + upi_wednesday_transactions + upi_thursday_transactions + upi_friday_transactions + upi_saturday_transactions + upi_sunday_transactions
        total_paytm_sales = paytm_monday_sales + paytm_tuesday_sales + paytm_wednesday_sales + paytm_thursday_sales + paytm_friday_sales + paytm_saturday_sales + paytm_sunday_sales
        total_paytm_transactions = paytm_monday_transactions + paytm_tuesday_transactions + paytm_wednesday_transactions + paytm_thursday_transactions + paytm_friday_transactions + paytm_saturday_transactions + paytm_sunday_transactions
        total_phone_sales = phone_monday_sales + phone_tuesday_sales + phone_wednesday_sales + phone_thursday_sales + phone_friday_sales + phone_saturday_sales + phone_sunday_sales
        total_phone_transactions = phone_monday_transactions + phone_tuesday_transactions + phone_wednesday_transactions + phone_thursday_transactions + phone_friday_transactions + phone_saturday_transactions + phone_sunday_transactions
        total_free_sales = free_monday_sales + free_tuesday_sales + free_wednesday_sales + free_thursday_sales + free_friday_sales + free_saturday_sales + free_sunday_sales
        total_free_transactions = free_monday_transactions + free_tuesday_transactions + free_wednesday_transactions + free_thursday_transactions + free_friday_transactions + free_saturday_transactions + free_sunday_transactions
        total_sodexo_sales = sodexo_monday_sales + sodexo_tuesday_sales + sodexo_wednesday_sales + sodexo_thursday_sales + sodexo_friday_sales + sodexo_saturday_sales + sodexo_sunday_sales
        total_sodexo_transactions = sodexo_monday_transactions + sodexo_tuesday_transactions + sodexo_wednesday_transactions + sodexo_thursday_transactions + sodexo_friday_transactions + sodexo_saturday_transactions + sodexo_sunday_transactions
        total_samsung_sales = samsung_monday_sales + samsung_tuesday_sales + samsung_wednesday_sales + samsung_thursday_sales + samsung_friday_sales + samsung_saturday_sales + samsung_sunday_sales
        total_samsung_transactions = samsung_monday_transactions + samsung_tuesday_transactions + samsung_wednesday_transactions + samsung_thursday_transactions + samsung_friday_transactions + samsung_saturday_transactions + samsung_sunday_transactions
        total_apple_sales = apple_monday_sales + apple_tuesday_sales + apple_wednesday_sales + apple_thursday_sales + apple_friday_sales + apple_saturday_sales + apple_sunday_sales
        total_apple_transactions = apple_monday_transactions + apple_tuesday_transactions + apple_wednesday_transactions + apple_thursday_transactions + apple_friday_transactions + apple_saturday_transactions + apple_sunday_transactions

        # report_lines = profit_loss.get_account_lines(data['form'])
        # report_lines = self.env['financial.report'].get_account_lines(data)
        data.update({'monday_sales_gross': round(monday_sales_gross, 2),
                     'tuesday_sales_gross': round(tuesday_sales_gross, 2),
                     'wednesday_sales_gross': round(wednesday_sales_gross, 2),
                     'thursday_sales_gross': round(thursday_sales_gross, 2),
                     'friday_sales_gross': round(friday_sales_gross, 2),
                     'saturday_sales_gross': round(saturday_sales_gross, 2),
                     'sunday_sales_gross': round(sunday_sales_gross, 2),
                     'sales_gross_total': round(sales_gross_total, 2),
                     'total_transactions': total_transactions,
                     'total_spmh': round(total_spmh, 2),
                     'total_refund': round(total_refund, 2),
                     'total_employee_meals': round(total_employee_meals, 2),
                     'monday_sales_net': monday_sales_net,
                     'tuesday_sales_net': tuesday_sales_net,
                     'wednesday_sales_net': wednesday_sales_net,
                     'thursday_sales_net': thursday_sales_net,
                     'friday_sales_net': friday_sales_net,
                     'saturday_sales_net': saturday_sales_net,
                     'sunday_sales_net': sunday_sales_net,
                     'total_sales_net': total_sales_net,
                     'monday_transactions': monday_transactions,
                     'tuesday_transactions': tuesday_transactions,
                     'wednesday_transactions': wednesday_transactions,
                     'thursday_transactions': thursday_transactions,
                     'friday_transactions': friday_transactions,
                     'saturday_transactions': saturday_transactions,
                     'sunday_transactions': sunday_transactions,
                     'monday_employees': round(monday_employees, 2),
                     'tuesday_employees': round(tuesday_employees, 2),
                     'wednesday_employees': round(wednesday_employees, 2),
                     'thursday_employees': round(thursday_employees, 2),
                     'friday_employees': round(friday_employees, 2),
                     'saturday_employees': round(saturday_employees, 2),
                     'sunday_employees': round(sunday_employees, 2),
                     'monday_refund_amount': round(monday_refund_amount, 2),
                     'tuesday_refund_amount': round(tuesday_refund_amount, 2),
                     'wednesday_refund_amount': round(wednesday_refund_amount, 2),
                     'thursday_refund_amount': round(thursday_refund_amount, 2),
                     'friday_refund_amount': round(friday_refund_amount, 2),
                     'saturday_refund_amount': round(saturday_refund_amount, 2),
                     'sunday_refund_amount': round(sunday_refund_amount, 2),
                     'promo_amount': promo_amount,
                     'monday_employee_meals': round(monday_employee_meals, 2),
                     'tuesday_employee_meals': round(tuesday_employee_meals, 2),
                     'wednesday_employee_meals': round(wednesday_employee_meals, 2),
                     'thursday_employee_meals': round(thursday_employee_meals, 2),
                     'friday_employee_meals': round(friday_employee_meals, 2),
                     'saturday_employee_meals': round(saturday_employee_meals, 2),
                     'sunday_employee_meals': round(sunday_employee_meals, 2),
                     'cash_monday_sales': round(cash_monday_sales, 2),
                     'cash_monday_transactions': cash_monday_transactions,
                     'cash_tuesday_sales': round(cash_tuesday_sales, 2),
                     'cash_tuesday_transactions': cash_tuesday_transactions,
                     'cash_wednesday_sales': round(cash_wednesday_sales, 2),
                     'cash_wednesday_transactions': cash_wednesday_transactions,
                     'cash_thursday_sales': round(cash_thursday_sales, 2),
                     'cash_thursday_transactions': cash_thursday_transactions,
                     'cash_friday_sales': round(cash_friday_sales, 2),
                     'cash_friday_transactions': cash_friday_transactions,
                     'cash_saturday_sales': round(cash_saturday_sales, 2),
                     'cash_saturday_transactions': cash_saturday_transactions,
                     'cash_sunday_sales': round(cash_sunday_sales, 2),
                     'cash_sunday_transactions': cash_sunday_transactions,
                     'credit_monday_sales': round(credit_monday_sales, 2),
                     'credit_monday_transactions': credit_monday_transactions,
                     'credit_tuesday_sales': round(credit_tuesday_sales, 2),
                     'credit_tuesday_transactions': credit_tuesday_transactions,
                     'credit_wednesday_sales': round(credit_wednesday_sales, 2),
                     'credit_wednesday_transactions': credit_wednesday_transactions,
                     'credit_thursday_sales': round(credit_thursday_sales, 2),
                     'credit_thursday_transactions': credit_thursday_transactions,
                     'credit_friday_sales': round(credit_friday_sales, 2),
                     'credit_friday_transactions': credit_friday_transactions,
                     'credit_saturday_sales': round(credit_saturday_sales, 2),
                     'credit_saturday_transactions': credit_saturday_transactions,
                     'credit_sunday_sales': round(credit_sunday_sales, 2),
                     'credit_sunday_transactions': credit_sunday_transactions,
                     'debit_monday_sales': round(debit_monday_sales, 2),
                     'debit_monday_transactions': debit_monday_transactions,
                     'debit_tuesday_sales': round(debit_tuesday_sales, 2),
                     'debit_tuesday_transactions': debit_tuesday_transactions,
                     'debit_wednesday_sales': round(debit_wednesday_sales, 2),
                     'debit_wednesday_transactions': debit_wednesday_transactions,
                     'debit_thursday_sales': round(debit_thursday_sales, 2),
                     'debit_thursday_transactions': debit_thursday_transactions,
                     'debit_friday_sales': round(debit_friday_sales, 2),
                     'debit_friday_transactions': debit_friday_transactions,
                     'debit_saturday_sales': round(debit_saturday_sales, 2),
                     'debit_saturday_transactions': debit_saturday_transactions,
                     'debit_sunday_sales': round(debit_sunday_sales, 2),
                     'debit_sunday_transactions': debit_sunday_transactions,
                     'upi_monday_sales': round(upi_monday_sales, 2),
                     'upi_monday_transactions': upi_monday_transactions,
                     'upi_tuesday_sales': round(upi_tuesday_sales, 2),
                     'upi_tuesday_transactions': upi_tuesday_transactions,
                     'upi_wednesday_sales': round(upi_wednesday_sales, 2),
                     'upi_wednesday_transactions': upi_wednesday_transactions,
                     'upi_thursday_sales': round(upi_thursday_sales, 2),
                     'upi_thursday_transactions': upi_thursday_transactions,
                     'upi_friday_sales': round(upi_friday_sales, 2),
                     'upi_friday_transactions': upi_friday_transactions,
                     'upi_saturday_sales': round(upi_saturday_sales, 2),
                     'upi_saturday_transactions': upi_saturday_transactions,
                     'upi_sunday_sales': round(upi_sunday_sales, 2),
                     'upi_sunday_transactions': upi_sunday_transactions,
                     'paytm_monday_sales': round(paytm_monday_sales, 2),
                     'paytm_monday_transactions': paytm_monday_transactions,
                     'paytm_tuesday_sales': round(paytm_tuesday_sales, 2),
                     'paytm_tuesday_transactions': paytm_tuesday_transactions,
                     'paytm_wednesday_sales': round(paytm_wednesday_sales, 2),
                     'paytm_wednesday_transactions': paytm_wednesday_transactions,
                     'paytm_thursday_sales': round(paytm_thursday_sales, 2),
                     'paytm_thursday_transactions': paytm_thursday_transactions,
                     'paytm_friday_sales': round(paytm_friday_sales, 2),
                     'paytm_friday_transactions': paytm_friday_transactions,
                     'paytm_saturday_sales': round(paytm_saturday_sales, 2),
                     'paytm_saturday_transactions': paytm_saturday_transactions,
                     'paytm_sunday_sales': round(paytm_sunday_sales, 2),
                     'paytm_sunday_transactions': paytm_sunday_transactions,
                     'phone_monday_sales': round(phone_monday_sales, 2),
                     'phone_monday_transactions': phone_monday_transactions,
                     'phone_tuesday_sales': round(phone_tuesday_sales, 2),
                     'phone_tuesday_transactions': phone_tuesday_transactions,
                     'phone_wednesday_sales': round(phone_wednesday_sales, 2),
                     'phone_wednesday_transactions': phone_wednesday_transactions,
                     'phone_thursday_sales': round(phone_thursday_sales, 2),
                     'phone_thursday_transactions': phone_thursday_transactions,
                     'phone_friday_sales': round(phone_friday_sales, 2),
                     'phone_friday_transactions': phone_friday_transactions,
                     'phone_saturday_sales': round(phone_saturday_sales, 2),
                     'phone_saturday_transactions': phone_saturday_transactions,
                     'phone_sunday_sales': round(phone_sunday_sales, 2),
                     'phone_sunday_transactions': phone_sunday_transactions,
                     'free_monday_sales': round(free_monday_sales, 2),
                     'free_monday_transactions': free_monday_transactions,
                     'free_tuesday_sales': round(free_tuesday_sales, 2),
                     'free_tuesday_transactions': free_tuesday_transactions,
                     'free_wednesday_sales': round(free_wednesday_sales, 2),
                     'free_wednesday_transactions': free_wednesday_transactions,
                     'free_thursday_sales': round(free_thursday_sales, 2),
                     'free_thursday_transactions': free_thursday_transactions,
                     'free_friday_sales': round(free_friday_sales, 2),
                     'free_friday_transactions': free_friday_transactions,
                     'free_saturday_sales': round(free_saturday_sales, 2),
                     'free_saturday_transactions': free_saturday_transactions,
                     'free_sunday_sales': round(free_sunday_sales, 2),
                     'free_sunday_transactions': free_sunday_transactions,
                     'sodexo_monday_sales': round(sodexo_monday_sales, 2),
                     'sodexo_monday_transactions': sodexo_monday_transactions,
                     'sodexo_tuesday_sales': round(sodexo_tuesday_sales, 2),
                     'sodexo_tuesday_transactions': sodexo_tuesday_transactions,
                     'sodexo_wednesday_sales': round(sodexo_wednesday_sales, 2),
                     'sodexo_wednesday_transactions': sodexo_wednesday_transactions,
                     'sodexo_thursday_sales': round(sodexo_thursday_sales, 2),
                     'sodexo_thursday_transactions': sodexo_thursday_transactions,
                     'sodexo_friday_sales': round(sodexo_friday_sales, 2),
                     'sodexo_friday_transactions': sodexo_friday_transactions,
                     'sodexo_saturday_sales': round(sodexo_saturday_sales, 2),
                     'sodexo_saturday_transactions': sodexo_saturday_transactions,
                     'sodexo_sunday_sales': round(sodexo_sunday_sales, 2),
                     'sodexo_sunday_transactions': sodexo_sunday_transactions,
                     'samsung_monday_sales': round(samsung_monday_sales, 2),
                     'samsung_monday_transactions': samsung_monday_transactions,
                     'samsung_tuesday_sales': round(samsung_tuesday_sales, 2),
                     'samsung_tuesday_transactions': samsung_tuesday_transactions,
                     'samsung_wednesday_sales': round(samsung_wednesday_sales, 2),
                     'samsung_wednesday_transactions': samsung_wednesday_transactions,
                     'samsung_thursday_sales': round(samsung_thursday_sales, 2),
                     'samsung_thursday_transactions': samsung_thursday_transactions,
                     'samsung_friday_sales': round(samsung_friday_sales, 2),
                     'samsung_friday_transactions': samsung_friday_transactions,
                     'samsung_saturday_sales': round(samsung_saturday_sales, 2),
                     'samsung_saturday_transactions': samsung_saturday_transactions,
                     'samsung_sunday_sales': round(samsung_sunday_sales, 2),
                     'samsung_sunday_transactions': samsung_sunday_transactions,
                     'apple_monday_sales': round(apple_monday_sales, 2),
                     'apple_monday_transactions': apple_monday_transactions,
                     'apple_tuesday_sales': round(apple_tuesday_sales, 2),
                     'apple_tuesday_transactions': apple_tuesday_transactions,
                     'apple_wednesday_sales': round(apple_wednesday_sales, 2),
                     'apple_wednesday_transactions': apple_wednesday_transactions,
                     'apple_thursday_sales': round(apple_thursday_sales, 2),
                     'apple_thursday_transactions': apple_thursday_transactions,
                     'apple_friday_sales': round(apple_friday_sales, 2),
                     'apple_friday_transactions': apple_friday_transactions,
                     'apple_saturday_sales': round(apple_saturday_sales, 2),
                     'apple_saturday_transactions': apple_saturday_transactions,
                     'apple_sunday_sales': round(apple_sunday_sales, 2),
                     'apple_sunday_transactions': apple_sunday_transactions,
                     'total_cash_sales': round(total_cash_sales, 2),
                     'total_cash_transactions': total_cash_transactions,
                     'total_credit_sales': round(total_credit_sales, 2),
                     'total_credit_transactions': total_credit_transactions,
                     'total_debit_sales': round(total_debit_sales, 2),
                     'total_debit_transactions': total_debit_transactions,
                     'total_upi_sales': round(total_upi_sales, 2),
                     'total_upi_transactions': total_upi_transactions,
                     'total_paytm_sales': round(total_paytm_sales, 2),
                     'total_paytm_transactions': total_paytm_transactions,
                     'total_phone_sales': round(total_phone_sales, 2),
                     'total_phone_transactions': total_phone_transactions,
                     'total_free_sales': round(total_free_sales, 2),
                     'total_free_transactions': total_free_transactions,
                     'total_sodexo_sales': round(total_sodexo_sales, 2),
                     'total_sodexo_transactions': total_sodexo_transactions,
                     'total_samsung_sales': round(total_samsung_sales, 2),
                     'total_samsung_transactions': total_samsung_transactions,
                     'total_apple_sales': round(total_apple_sales, 2),
                     'total_apple_transactions': total_apple_transactions,
                     })

        this_week_start_time = date_start
        this_week_end_time = date_stop
        dates = {}
        mondays = self.get_days(this_week_start_time, this_week_end_time, "Monday")
        tuesdays = self.get_days(this_week_start_time, this_week_end_time, "Tuesday")
        wednesdays = self.get_days(this_week_start_time, this_week_end_time, "Wednesday")
        thursdays = self.get_days(this_week_start_time, this_week_end_time, "Thursday")
        fridays = self.get_days(this_week_start_time, this_week_end_time, "Friday")
        saturdays = self.get_days(this_week_start_time, this_week_end_time, "Saturday")
        sundays = self.get_days(this_week_start_time, this_week_end_time, "Sunday")
        dates.update({
            'monday': mondays,
            'tuesday': tuesdays,
            'wednesday': wednesdays,
            'thursday': thursdays,
            'friday': fridays,
            'saturday': saturdays,
            'sunday': sundays
        })
        # current_date = []
        # for i in dates.values():
        #     if len(i) > 1:
        #         current_date.append(i)
        # current_key = self.find_key(dates, current_date[0])
        # dates.get(current_key).pop(0)

        i = 0
        row = 3
        column = 0

        worksheet.write(1, 1, dates.get('monday')[0].strftime('%d %b'), format4)
        worksheet.write(1, 2, dates.get('tuesday')[0].strftime('%d %b'), format4)
        worksheet.write(1, 3, dates.get('wednesday')[0].strftime('%d %b'), format4)
        worksheet.write(1, 4, dates.get('thursday')[0].strftime('%d %b'), format4)
        worksheet.write(1, 5, dates.get('friday')[0].strftime('%d %b'), format4)
        worksheet.write(1, 6, dates.get('saturday')[0].strftime('%d %b'), format4)
        worksheet.write(1, 7, dates.get('sunday')[0].strftime('%d %b'), format4)

        worksheet.write(13, 1, dates.get('monday')[0].strftime('%d %b'), format4)
        worksheet.write(13, 2, dates.get('tuesday')[0].strftime('%d %b'), format4)
        worksheet.write(13, 3, dates.get('wednesday')[0].strftime('%d %b'), format4)
        worksheet.write(13, 4, dates.get('thursday')[0].strftime('%d %b'), format4)
        worksheet.write(13, 5, dates.get('friday')[0].strftime('%d %b'), format4)
        worksheet.write(13, 6, dates.get('saturday')[0].strftime('%d %b'), format4)
        worksheet.write(13, 7, dates.get('sunday')[0].strftime('%d %b'), format4)

        worksheet.write(3, 1, data.get('monday_sales_gross'), format4)
        worksheet.write(3, 2, data.get('tuesday_sales_gross'), format4)
        worksheet.write(3, 3, data.get('wednesday_sales_gross'), format4)
        worksheet.write(3, 4, data.get('thursday_sales_gross'), format4)
        worksheet.write(3, 5, data.get('friday_sales_gross'), format4)
        worksheet.write(3, 6, data.get('saturday_sales_gross'), format4)
        worksheet.write(3, 7, data.get('sunday_sales_gross'), format4)
        worksheet.write(3, 8, data.get('sales_gross_total'), format4)

        worksheet.write(4, 1, data.get('monday_sales_net'), format4)
        worksheet.write(4, 2, data.get('tuesday_sales_net'), format4)
        worksheet.write(4, 3, data.get('wednesday_sales_net'), format4)
        worksheet.write(4, 4, data.get('thursday_sales_net'), format4)
        worksheet.write(4, 5, data.get('friday_sales_net'), format4)
        worksheet.write(4, 6, data.get('saturday_sales_net'), format4)
        worksheet.write(4, 7, data.get('sunday_sales_net'), format4)
        worksheet.write(4, 8, data.get('total_sales_net'), format4)

        worksheet.write(5, 1, data.get('monday_transactions'), format4)
        worksheet.write(5, 2, data.get('tuesday_transactions'), format4)
        worksheet.write(5, 3, data.get('wednesday_transactions'), format4)
        worksheet.write(5, 4, data.get('thursday_transactions'), format4)
        worksheet.write(5, 5, data.get('friday_transactions'), format4)
        worksheet.write(5, 6, data.get('saturday_transactions'), format4)
        worksheet.write(5, 7, data.get('sunday_transactions'), format4)
        worksheet.write(5, 8, data.get('sunday_transactions'), format4)

        worksheet.write(6, 1, data.get('monday_employees'), format4)
        worksheet.write(6, 2, data.get('tuesday_employees'), format4)
        worksheet.write(6, 3, data.get('wednesday_employees'), format4)
        worksheet.write(6, 4, data.get('thursday_employees'), format4)
        worksheet.write(6, 5, data.get('friday_employees'), format4)
        worksheet.write(6, 6, data.get('saturday_employees'), format4)
        worksheet.write(6, 7, data.get('sunday_employees'), format4)
        worksheet.write(6, 8, data.get('total_spmh'), format4)

        worksheet.write(7, 1, data.get('monday_refund_amount'), format4)
        worksheet.write(7, 2, data.get('tuesday_refund_amount'), format4)
        worksheet.write(7, 3, data.get('wednesday_refund_amount'), format4)
        worksheet.write(7, 4, data.get('thursday_refund_amount'), format4)
        worksheet.write(7, 5, data.get('friday_refund_amount'), format4)
        worksheet.write(7, 6, data.get('saturday_refund_amount'), format4)
        worksheet.write(7, 7, data.get('sunday_refund_amount'), format4)
        worksheet.write(7, 8, data.get('total_refund'), format4)

        worksheet.write(8, 1, data.get('promo_amount'), format4)
        worksheet.write(8, 2, data.get('promo_amount'), format4)
        worksheet.write(8, 3, data.get('promo_amount'), format4)
        worksheet.write(8, 4, data.get('promo_amount'), format4)
        worksheet.write(8, 5, data.get('promo_amount'), format4)
        worksheet.write(8, 6, data.get('promo_amount'), format4)
        worksheet.write(8, 7, data.get('promo_amount'), format4)
        worksheet.write(8, 8, data.get('promo_amount'), format4)

        worksheet.write(9, 1, data.get('monday_employee_meals'), format4)
        worksheet.write(9, 2, data.get('tuesday_employee_meals'), format4)
        worksheet.write(9, 3, data.get('wednesday_employee_meals'), format4)
        worksheet.write(9, 4, data.get('thursday_employee_meals'), format4)
        worksheet.write(9, 5, data.get('friday_employee_meals'), format4)
        worksheet.write(9, 6, data.get('saturday_employee_meals'), format4)
        worksheet.write(9, 7, data.get('sunday_employee_meals'), format4)
        worksheet.write(9, 8, data.get('total_employee_meals'), format4)

        worksheet.write(15, 1, data.get('cash_monday_sales'), format5)
        worksheet.write(15, 2, data.get('cash_tuesday_sales'), format5)
        worksheet.write(15, 3, data.get('cash_wednesday_sales'), format5)
        worksheet.write(15, 4, data.get('cash_thursday_sales'), format5)
        worksheet.write(15, 5, data.get('cash_friday_sales'), format5)
        worksheet.write(15, 6, data.get('cash_saturday_sales'), format5)
        worksheet.write(15, 7, data.get('cash_sunday_sales'), format5)
        worksheet.write(15, 8, data.get('total_cash_sales'), format5)

        worksheet.write(16, 1, data.get('cash_monday_transactions'), format5)
        worksheet.write(16, 2, data.get('cash_tuesday_transactions'), format5)
        worksheet.write(16, 3, data.get('cash_wednesday_transactions'), format5)
        worksheet.write(16, 4, data.get('cash_thursday_transactions'), format5)
        worksheet.write(16, 5, data.get('cash_friday_transactions'), format5)
        worksheet.write(16, 6, data.get('cash_saturday_transactions'), format5)
        worksheet.write(16, 7, data.get('cash_sunday_transactions'), format5)
        worksheet.write(16, 8, data.get('total_cash_transactions'), format5)

        worksheet.write(18, 1, data.get('credit_monday_sales'), format5)
        worksheet.write(18, 2, data.get('credit_tuesday_sales'), format5)
        worksheet.write(18, 3, data.get('credit_wednesday_sales'), format5)
        worksheet.write(18, 4, data.get('credit_thursday_sales'), format5)
        worksheet.write(18, 5, data.get('credit_friday_sales'), format5)
        worksheet.write(18, 6, data.get('credit_saturday_sales'), format5)
        worksheet.write(18, 7, data.get('credit_sunday_sales'), format5)
        worksheet.write(18, 8, data.get('total_credit_sales'), format5)

        worksheet.write(19, 1, data.get('credit_monday_transactions'), format5)
        worksheet.write(19, 2, data.get('credit_tuesday_transactions'), format5)
        worksheet.write(19, 3, data.get('credit_wednesday_transactions'), format5)
        worksheet.write(19, 4, data.get('credit_thursday_transactions'), format5)
        worksheet.write(19, 5, data.get('credit_friday_transactions'), format5)
        worksheet.write(19, 6, data.get('credit_saturday_transactions'), format5)
        worksheet.write(19, 7, data.get('credit_sunday_transactions'), format5)
        worksheet.write(19, 8, data.get('total_credit_transactions'), format5)

        worksheet.write(21, 1, data.get('debit_monday_sales'), format5)
        worksheet.write(21, 2, data.get('debit_tuesday_sales'), format5)
        worksheet.write(21, 3, data.get('debit_wednesday_sales'), format5)
        worksheet.write(21, 4, data.get('debit_thursday_sales'), format5)
        worksheet.write(21, 5, data.get('debit_friday_sales'), format5)
        worksheet.write(21, 6, data.get('debit_saturday_sales'), format5)
        worksheet.write(21, 7, data.get('debit_sunday_sales'), format5)
        worksheet.write(21, 8, data.get('total_debit_sales'), format5)

        worksheet.write(22, 1, data.get('debit_monday_transactions'), format5)
        worksheet.write(22, 2, data.get('debit_tuesday_transactions'), format5)
        worksheet.write(22, 3, data.get('debit_wednesday_transactions'), format5)
        worksheet.write(22, 4, data.get('debit_thursday_transactions'), format5)
        worksheet.write(22, 5, data.get('debit_friday_transactions'), format5)
        worksheet.write(22, 6, data.get('debit_saturday_transactions'), format5)
        worksheet.write(22, 7, data.get('debit_sunday_transactions'), format5)
        worksheet.write(22, 8, data.get('total_debit_transactions'), format5)

        worksheet.write(24, 1, data.get('upi_monday_sales'), format5)
        worksheet.write(24, 2, data.get('upi_tuesday_sales'), format5)
        worksheet.write(24, 3, data.get('upi_wednesday_sales'), format5)
        worksheet.write(24, 4, data.get('upi_thursday_sales'), format5)
        worksheet.write(24, 5, data.get('upi_friday_sales'), format5)
        worksheet.write(24, 6, data.get('upi_saturday_sales'), format5)
        worksheet.write(24, 7, data.get('upi_sunday_sales'), format5)
        worksheet.write(24, 8, data.get('total_upi_sales'), format5)

        worksheet.write(25, 1, data.get('upi_monday_transactions'), format5)
        worksheet.write(25, 2, data.get('upi_tuesday_transactions'), format5)
        worksheet.write(25, 3, data.get('upi_wednesday_transactions'), format5)
        worksheet.write(25, 4, data.get('upi_thursday_transactions'), format5)
        worksheet.write(25, 5, data.get('upi_friday_transactions'), format5)
        worksheet.write(25, 6, data.get('upi_saturday_transactions'), format5)
        worksheet.write(25, 7, data.get('upi_sunday_transactions'), format5)
        worksheet.write(25, 8, data.get('total_upi_transactions'), format5)

        worksheet.write(27, 1, data.get('paytm_monday_sales'), format5)
        worksheet.write(27, 2, data.get('paytm_tuesday_sales'), format5)
        worksheet.write(27, 3, data.get('paytm_wednesday_sales'), format5)
        worksheet.write(27, 4, data.get('paytm_thursday_sales'), format5)
        worksheet.write(27, 5, data.get('paytm_friday_sales'), format5)
        worksheet.write(27, 6, data.get('paytm_saturday_sales'), format5)
        worksheet.write(27, 7, data.get('paytm_sunday_sales'), format5)
        worksheet.write(27, 8, data.get('total_paytm_sales'), format5)

        worksheet.write(28, 1, data.get('paytm_monday_transactions'), format5)
        worksheet.write(28, 2, data.get('paytm_tuesday_transactions'), format5)
        worksheet.write(28, 3, data.get('paytm_wednesday_transactions'), format5)
        worksheet.write(28, 4, data.get('paytm_thursday_transactions'), format5)
        worksheet.write(28, 5, data.get('paytm_friday_transactions'), format5)
        worksheet.write(28, 6, data.get('paytm_saturday_transactions'), format5)
        worksheet.write(28, 7, data.get('paytm_sunday_transactions'), format5)
        worksheet.write(28, 8, data.get('total_paytm_transactions'), format5)

        worksheet.write(30, 1, data.get('phone_monday_sales'), format5)
        worksheet.write(30, 2, data.get('phone_tuesday_sales'), format5)
        worksheet.write(30, 3, data.get('phone_wednesday_sales'), format5)
        worksheet.write(30, 4, data.get('phone_thursday_sales'), format5)
        worksheet.write(30, 5, data.get('phone_friday_sales'), format5)
        worksheet.write(30, 6, data.get('phone_saturday_sales'), format5)
        worksheet.write(30, 7, data.get('phone_sunday_sales'), format5)
        worksheet.write(30, 8, data.get('total_phone_sales'), format5)

        worksheet.write(31, 1, data.get('phone_monday_transactions'), format5)
        worksheet.write(31, 2, data.get('phone_tuesday_transactions'), format5)
        worksheet.write(31, 3, data.get('phone_wednesday_transactions'), format5)
        worksheet.write(31, 4, data.get('phone_thursday_transactions'), format5)
        worksheet.write(31, 5, data.get('phone_friday_transactions'), format5)
        worksheet.write(31, 6, data.get('phone_saturday_transactions'), format5)
        worksheet.write(31, 7, data.get('phone_sunday_transactions'), format5)
        worksheet.write(31, 8, data.get('total_phone_transactions'), format5)

        worksheet.write(33, 1, data.get('free_monday_sales'), format5)
        worksheet.write(33, 2, data.get('free_tuesday_sales'), format5)
        worksheet.write(33, 3, data.get('free_wednesday_sales'), format5)
        worksheet.write(33, 4, data.get('free_thursday_sales'), format5)
        worksheet.write(33, 5, data.get('free_friday_sales'), format5)
        worksheet.write(33, 6, data.get('free_saturday_sales'), format5)
        worksheet.write(33, 7, data.get('free_sunday_sales'), format5)
        worksheet.write(33, 8, data.get('total_free_sales'), format5)

        worksheet.write(34, 1, data.get('free_monday_transactions'), format5)
        worksheet.write(34, 2, data.get('free_tuesday_transactions'), format5)
        worksheet.write(34, 3, data.get('free_wednesday_transactions'), format5)
        worksheet.write(34, 4, data.get('free_thursday_transactions'), format5)
        worksheet.write(34, 5, data.get('free_friday_transactions'), format5)
        worksheet.write(34, 6, data.get('free_saturday_transactions'), format5)
        worksheet.write(34, 7, data.get('free_sunday_transactions'), format5)
        worksheet.write(34, 8, data.get('total_free_transactions'), format5)

        worksheet.write(36, 1, data.get('sodexo_monday_sales'), format5)
        worksheet.write(36, 2, data.get('sodexo_tuesday_sales'), format5)
        worksheet.write(36, 3, data.get('sodexo_wednesday_sales'), format5)
        worksheet.write(36, 4, data.get('sodexo_thursday_sales'), format5)
        worksheet.write(36, 5, data.get('sodexo_friday_sales'), format5)
        worksheet.write(36, 6, data.get('sodexo_saturday_sales'), format5)
        worksheet.write(36, 7, data.get('sodexo_sunday_sales'), format5)
        worksheet.write(36, 8, data.get('total_sodexo_sales'), format5)

        worksheet.write(37, 1, data.get('sodexo_monday_transactions'), format5)
        worksheet.write(37, 2, data.get('sodexo_tuesday_transactions'), format5)
        worksheet.write(37, 3, data.get('sodexo_wednesday_transactions'), format5)
        worksheet.write(37, 4, data.get('sodexo_thursday_transactions'), format5)
        worksheet.write(37, 5, data.get('sodexo_friday_transactions'), format5)
        worksheet.write(37, 6, data.get('sodexo_saturday_transactions'), format5)
        worksheet.write(37, 7, data.get('sodexo_sunday_transactions'), format5)
        worksheet.write(37, 8, data.get('total_sodexo_transactions'), format5)

        worksheet.write(39, 1, data.get('samsung_monday_sales'), format5)
        worksheet.write(39, 2, data.get('samsung_tuesday_sales'), format5)
        worksheet.write(39, 3, data.get('samsung_wednesday_sales'), format5)
        worksheet.write(39, 4, data.get('samsung_thursday_sales'), format5)
        worksheet.write(39, 5, data.get('samsung_friday_sales'), format5)
        worksheet.write(39, 6, data.get('samsung_saturday_sales'), format5)
        worksheet.write(39, 7, data.get('samsung_sunday_sales'), format5)
        worksheet.write(39, 8, data.get('total_samsung_sales'), format5)

        worksheet.write(40, 1, data.get('samsung_monday_transactions'), format5)
        worksheet.write(40, 2, data.get('samsung_tuesday_transactions'), format5)
        worksheet.write(40, 3, data.get('samsung_wednesday_transactions'), format5)
        worksheet.write(40, 4, data.get('samsung_thursday_transactions'), format5)
        worksheet.write(40, 5, data.get('samsung_friday_transactions'), format5)
        worksheet.write(40, 6, data.get('samsung_saturday_transactions'), format5)
        worksheet.write(40, 7, data.get('samsung_sunday_transactions'), format5)
        worksheet.write(40, 8, data.get('total_samsung_transactions'), format5)

        worksheet.write(42, 1, data.get('apple_monday_sales'), format5)
        worksheet.write(42, 2, data.get('apple_tuesday_sales'), format5)
        worksheet.write(42, 3, data.get('apple_wednesday_sales'), format5)
        worksheet.write(42, 4, data.get('apple_thursday_sales'), format5)
        worksheet.write(42, 5, data.get('apple_friday_sales'), format5)
        worksheet.write(42, 6, data.get('apple_saturday_sales'), format5)
        worksheet.write(42, 7, data.get('apple_sunday_sales'), format5)
        worksheet.write(42, 8, data.get('total_apple_sales'), format5)

        worksheet.write(43, 1, data.get('apple_monday_transactions'), format5)
        worksheet.write(43, 2, data.get('apple_tuesday_transactions'), format5)
        worksheet.write(43, 3, data.get('apple_wednesday_transactions'), format5)
        worksheet.write(43, 4, data.get('apple_thursday_transactions'), format5)
        worksheet.write(43, 5, data.get('apple_friday_transactions'), format5)
        worksheet.write(43, 6, data.get('apple_saturday_transactions'), format5)
        worksheet.write(43, 7, data.get('apple_sunday_transactions'), format5)
        worksheet.write(43, 8, data.get('total_apple_transactions'), format5)


