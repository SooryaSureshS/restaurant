from odoo import models,fields
import datetime
from datetime import datetime, timedelta

import pytz
from odoo.http import request

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_week_dates(self, base_date, start_day, end_day=None):
        monday = base_date - timedelta(days=base_date.isoweekday() - 1)
        week_dates = [monday + timedelta(days=i) for i in range(7)]
        return week_dates[start_day - 1:end_day or start_day]

    def get_this_and_last_week_sales(self, end_date):
        end_date = datetime.strptime(end_date+" 00:00:00", '%Y-%m-%d %H:%M:%S').astimezone(pytz.timezone(self.env.user.tz or 'Asia/Calcutta'))

        dates = self.get_week_dates(end_date.astimezone(pytz.utc), 1, 7)
        # dates = self.get_week_dates(((end_date.astimezone(tz)).replace(microsecond=0)).replace(tzinfo=None), 1, 7)

        l_dates = self.get_week_dates(end_date.astimezone(pytz.utc) - timedelta(weeks=1), 1, 7)
        # l_dates = self.get_week_dates(((end_date.astimezone(tz)).replace(microsecond=0)).replace(tzinfo=None) - timedelta(weeks=1), 1, 7)

        tws = dates[0].strftime('%Y') + "-" + dates[0].strftime('%m') + "-" + dates[0].strftime('%d')
        twe = dates[-1].strftime('%Y') + "-" + dates[-1].strftime('%m') + "-" + dates[-1].strftime('%d')

        pos_domain = [('date_order', '>=', tws), ('date_order', '<=', twe),
                      ('state', 'in', ['paid', 'done', 'invoiced'])]

        sale_domain = [('date_order', '>=', tws), ('date_order', '<=', twe), ('state', '=', 'sale')]

        t_pos_orders = self.env['pos.order'].search(pos_domain)
        t_sale_orders = self.env['sale.order'].search(sale_domain)
        t_sale = sum(t_pos_orders.mapped('amount_total')) + sum(t_sale_orders.mapped('amount_total'))
        t_trans = len(t_pos_orders.mapped('id')) + len(t_sale_orders.mapped('id'))
        t_avg_per_person = t_sale/sum(t_pos_orders.mapped('people_number')) if sum(t_pos_orders.mapped('people_number')) > 0 else 0
        currency_symbol = self.env.company.currency_id.symbol
        try:
            t_avg = t_sale / t_trans
        except:
            t_avg = 0
        lws = l_dates[0].strftime('%Y') + "-" + l_dates[0].strftime('%m') + "-" + l_dates[0].strftime('%d')
        lwe = l_dates[-1].strftime('%Y') + "-" + l_dates[-1].strftime('%m') + "-" + l_dates[-1].strftime('%d')
        pos_domain = [('date_order', '>=', lws), ('date_order', '<=', lwe),
                      ('state', 'in', ['paid', 'done', 'invoiced'])]
        sale_domain = [('date_order', '>=', lws), ('date_order', '<=', lwe), ('state', '=', 'sale')]
        l_pos_orders = self.env['pos.order'].search(pos_domain)

        l_sale_orders = self.env['sale.order'].search(sale_domain)
        l_sale = sum(l_pos_orders.mapped('amount_total')) + sum(l_sale_orders.mapped('amount_total'))
        l_trans = len(l_pos_orders.mapped('id')) + len(l_sale_orders.mapped('id'))
        l_avg_per_person = l_sale/sum(l_pos_orders.mapped('people_number')) if sum(l_pos_orders.mapped('people_number')) > 0 else 0
        try:
            l_avg = l_sale / l_trans
        except:
            l_avg = 0
        return {
            'currency_symbol': currency_symbol,
            't_sale': round(t_sale,2),
            't_trans': round(t_trans,2),
            't_avg': round(t_avg,2),
            'l_sale': round(l_sale,2),
            'l_trans': round(l_trans,2),
            'l_avg': round(l_avg,2),
            'variance': 2 if t_sale > l_sale else 1,
            't_avg_per_person': round(t_avg_per_person, 2),
            'l_avg_per_person': round(l_avg_per_person, 2)
        }

    def get_sales_hour_interval(self, interval, orders):
        return orders.filtered(lambda r: interval[0] <= r.date_order.astimezone(pytz.timezone(self.env.user.tz or 'Asia/Calcutta')) <= interval[1])

    def date_range(self, start, end):
        delta = end - start
        days = [start + timedelta(days=i) for i in range(delta.days + 1)]
        return days

    def get_hourly_sales_data(self, start_date, end_date):
        if start_date and end_date:
            start_date_a = start_date
            end_date_a = end_date
            end_date_b = end_date

            start_date = datetime.strptime(start_date + " 00:00:00", '%Y-%m-%d %H:%M:%S').astimezone(pytz.timezone(self.env.user.tz or 'Asia/Calcutta'))
            end_date = datetime.strptime(end_date + " 23:59:59", '%Y-%m-%d %H:%M:%S').astimezone(pytz.timezone(self.env.user.tz or 'Asia/Calcutta'))
        else:
            start_date = datetime.now(pytz.timezone(self.env.user.tz or 'Asia/Calcutta'))
            start_date_a = start_date.strftime('%Y-%m-%d')
            end_date_a = (start_date + timedelta(days=1)).strftime('%Y-%m-%d')

            end_date_b = (start_date + timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = start_date + timedelta(days=1)

        start_date = start_date.astimezone(pytz.utc)
        end_date = end_date.astimezone(pytz.utc)

        dates = self.date_range(start_date,end_date)

        pos_domain = [('date_order', '>=', start_date), ('date_order', '<=', end_date),
                      ('state', 'in', ['paid', 'done', 'invoiced'])]

        sale_domain = [('date_order', '>=', start_date), ('date_order', '<=', end_date), ('state', '=', 'sale')]
        pos_orders = self.env['pos.order'].search(pos_domain)
        sale_orders = self.env['sale.order'].search(sale_domain)

        hours = [9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,00]

        total = {
            'Monday': {'sale': 0, 'trans': 0},
            'Tuesday': {'sale': 0, 'trans': 0},
            'Wednesday': {'sale': 0, 'trans': 0},
            'Thursday': {'sale': 0, 'trans': 0},
            'Friday': {'sale': 0, 'trans': 0},
            'Saturday': {'sale': 0, 'trans': 0},
            'Sunday': {'sale': 0, 'trans': 0}
        }
        objs = {}
        data = {'objs': objs, 'start_date_val': start_date_a, 'end_date_val': end_date_a, 'total': total}
        for i in range(0, len(hours)-1):
            # key_time = str(hours[i][0])+" "+hours[i][1] + " - " + str(hours[i+1][0])+" "+hours[i+1][1]
            key_time = str(hours[i]) + " - " + str(hours[i+1])
            objs[key_time] = {
                'Monday': {'sale': 0, 'trans': 0},
                'Tuesday': {'sale': 0, 'trans': 0},
                'Wednesday': {'sale': 0, 'trans': 0},
                'Thursday': {'sale': 0, 'trans': 0},
                'Friday': {'sale': 0, 'trans': 0},
                'Saturday': {'sale': 0, 'trans': 0},
                'Sunday': {'sale': 0, 'trans': 0},
            }
        for i in range(0, len(hours) - 1):
            for j in dates:

                j = j.astimezone(pytz.timezone(self.env.user.tz or 'Asia/Calcutta'))

                t1 = j + timedelta(hours=hours[i])
                t2 = j + timedelta(hours=hours[i+1])

                so = self.get_sales_hour_interval((t1, t2), sale_orders)
                po = self.get_sales_hour_interval((t1, t2), pos_orders)

                a = str(t1.hour) + " - " + str(t2.hour)
                if so:
                    if a in objs:
                        objs[a][j.strftime('%A')]['sale'] += sum(so.mapped('amount_total'))
                        objs[a][j.strftime('%A')]['trans'] += len(so.mapped('id'))
                    total[j.strftime('%A')]['sale'] += sum(so.mapped('amount_total'))
                    total[j.strftime('%A')]['trans'] += len(po.mapped('id'))
                if po:
                    if a in objs:
                        objs[a][j.strftime('%A')]['sale'] += sum(po.mapped('amount_total'))
                        objs[a][j.strftime('%A')]['trans'] += len(po.mapped('id'))
                    total[j.strftime('%A')]['sale'] += sum(po.mapped('amount_total'))
                    total[j.strftime('%A')]['trans'] += len(po.mapped('id'))

        data['totals'] = self.get_this_and_last_week_sales(end_date_b)
        return data
