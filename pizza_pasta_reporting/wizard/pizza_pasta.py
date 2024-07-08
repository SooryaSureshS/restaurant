from odoo import api, fields, models, _
from datetime import datetime
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError


class PizzaPasta(models.Model):
    _inherit = "pos.category"

    pizza_or_pasta = fields.Selection(
        [('pizza', "Pizza Product"), ('pasta', 'Pasta Product')], srting="Pizza or Pasta Product?")


class PizzaPastaReport(models.TransientModel):
    _name = "pizza.pasta.report.wizard"

    from_date = fields.Date(string="From Date", default=datetime.today(), required=True)
    to_date = fields.Date(string="To Date", default=datetime.today(), required=True)

    def print_report(self):
        return self.env.ref('pizza_pasta_reporting.pizza_pasta_report_action').report_action(self,
                                                                                             data=self.read([])[0])


class PosReportCategory(models.AbstractModel):
    _name = 'report.pizza_pasta_reporting.pizza_pasta_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date = data.get('from_date')
        end_date = data.get('to_date')
        from datetime import datetime
        from dateutil import relativedelta
        date1 = datetime.strptime(start_date, '%Y-%m-%d')
        date2 = datetime.strptime(end_date, '%Y-%m-%d')
        r = relativedelta.relativedelta(date2, date1)
        date_difference = 1
        sale_data = self.env['sale.order.line'].sudo().search(
            [('order_id.date_order', '>=', start_date), ('order_id.date_order', '<=', end_date),
             ('order_id.state', '=', 'sale'),
             ('product_id.pos_categ_id.pizza_or_pasta', 'in', ['pizza', 'pasta'])])
        pos_data = self.env['pos.order.line'].sudo().search(
            [('order_id.date_order', '>=', start_date), ('order_id.date_order', '<=', end_date),
             ('order_id.state', 'in', ['paid', 'posted']),
             ('product_id.pos_categ_id.pizza_or_pasta', 'in', ['pizza', 'pasta'])])
        # print(sale_data)
        # print(pos_data)
        start_time = "01:00"
        end_time = "23:00"
        start_time_val = datetime.strptime(start_time, '%H:%M')
        end_time_val = datetime.strptime(end_time, '%H:%M')
        time_diff = timedelta(minutes=30)
        # for i in pos_data:
        #     print(i.order_id.id)
        orders = []
        total_pizza_pasta = 0
        total_pizza = 0
        total_pasta = 0
        total_pizza_percentage = 0
        total_pasta_percentage = 0
        while start_time_val <= end_time_val:
            start_time_val += time_diff
            pizza_count = 0
            pasta_count = 0
            start_time_end = start_time_val + timedelta(minutes=30)
            for i in pos_data:
                start_time_end = start_time_val + timedelta(minutes=30)
                if i.order_id.date_order.time() >= start_time_val.time() and i.order_id.date_order.time() <= start_time_end.time():
                    # print(i.order_id.date_order.time())
                    # print(i.order_id.id)
                    # pizza_count = 0
                    # pasta_count = 0
                    print(i.qty)
                    if i.product_id.pos_categ_id.pizza_or_pasta == "pizza":
                        pizza_count += i.qty
                    elif i.product_id.pos_categ_id.pizza_or_pasta == "pasta":
                        pasta_count += i.qty
                    print(str(start_time_val.time()), pizza_count, pasta_count)
            if pizza_count > 0 or pasta_count > 0:
                total_pizza += pizza_count
                total_pasta += pasta_count
                pizza_percentage = 0
                pasta_percentage = 0
                total_count = pasta_count + pizza_count
                if pizza_count > 0:
                    pizza_percentage = round((pizza_count / total_count) * 100, 2)
                if pasta_count > 0:
                    pasta_percentage = round((pasta_count / total_count) * 100, 2)
                orders.append(
                    {'interval': str(start_time_val.time()), 'pizza_count': pizza_count, 'pasta_count': pasta_count,
                     'total_count': pasta_count + pizza_count, 'pizza_percentage': pizza_percentage,
                     'pasta_percentage': pasta_percentage
                     })

        total_sale = []
        for i in range(len(orders)):
            if orders[i]['pizza_count'] == 0 and orders[i]['pasta_count'] == 0:
                del orders[i]
        print("orders", orders)
        total_pizza_pasta = total_pasta + total_pizza
        if total_pizza > 0:
            total_pizza_percentage = round((total_pizza / total_pizza_pasta) * 100, 2)
        if total_pasta > 0:
            total_pasta_percentage = round((total_pasta / total_pizza_pasta) * 100, 2)
        orders.append(
            {'interval': "", 'pizza_count': "", 'pasta_count': "",
             'total_count': "", 'pizza_percentage': "",
             'pasta_percentage': ""
             })
        orders.append(
            {'interval': "Totals", 'pizza_count': total_pizza, 'pasta_count': total_pasta,
             'total_count': total_pizza_pasta, 'pizza_percentage': total_pizza_percentage,
             'pasta_percentage': total_pasta_percentage
             })

        return {
            'data': orders,
            'doc_ids': docids,
            'doc_model': 'pos.category',
            'docs': docids,
            'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime("%m/%d/%Y"),
            'end_date': datetime.strptime(end_date, '%Y-%m-%d').strftime("%m/%d/%Y"),
        }
