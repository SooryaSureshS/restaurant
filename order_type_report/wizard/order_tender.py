from odoo import api, fields, models,_
from datetime import datetime
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError

class TenderReportWizard(models.TransientModel):
    _name = "tender.report"

    # order_no = fields.Char(string="Order No")
    from_date = fields.Date(string="From Date", default=datetime.today(),required=True)
    to_date = fields.Date(string="To Date", default=datetime.today(),required=True)



    def print_report(self):
        return self.env.ref('order_type_report.report_tender_action').report_action(self, data=self.read([])[0])


class OrderReport(models.AbstractModel):
    _name = 'report.order_type_report.order_tender_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date=data.get('from_date')
        end_date=data.get('to_date')
        domain =  [('date_order', '>=', start_date), ('date_order', '<=',end_date),('state','in',['paid','done','invoiced'])]
        sale_domain =  [('date_order', '>=', start_date), ('date_order', '<=',end_date),('state','=','sale')]
        sale_order = self.env['sale.order'].search(sale_domain)
        sale_order_obj = self.env['sale.order']
        pos_order = self.env['pos.order'].search(domain)
        pos_order_obj = self.env['pos.order']

        if sale_order or  pos_order:
            pass
        else:
            raise ValidationError(_('No orders provided during the selected dates.'))

        uber_sale=sale_order.filtered(lambda r:r.website_delivery_type=='uber') or sale_order_obj
        door_dash_sale=sale_order.filtered(lambda r:r.website_delivery_type=='door')  or sale_order_obj
        menulog_sale=sale_order.filtered(lambda r:r.website_delivery_type=='menulog')  or sale_order_obj
        deliveroo_sale=sale_order.filtered(lambda r:r.website_delivery_type=='deliveroo')  or sale_order_obj

        uber_pos = pos_order.filtered(lambda r: r.delivery_type == 'uber')  or pos_order_obj
        door_dash_pos = pos_order.filtered(lambda r: r.delivery_type == 'door')  or pos_order_obj
        menulog_pos = pos_order.filtered(lambda r: r.delivery_type == 'menulog')  or pos_order_obj
        deliveroo_pos = pos_order.filtered(lambda r: r.delivery_type == 'deliveroo')  or pos_order_obj

        if uber_sale or menulog_sale or deliveroo_sale or door_dash_sale or uber_pos or menulog_pos or deliveroo_pos or door_dash_pos:
            uber_vals_dict={'count':len(uber_sale)+len(uber_pos),'amount':sum([i.amount_total for i in uber_sale])+sum([pos.amount_total for pos in uber_pos])}
            menulog_vals_dict={'count':len(menulog_sale)+len(menulog_pos),'amount':sum([i.amount_total for i in menulog_sale])+sum([pos.amount_total for pos in menulog_pos])}
            deliveroo_vals_dict={'count':len(deliveroo_sale)+len(deliveroo_pos),'amount':sum([i.amount_total for i in deliveroo_sale])+sum([pos.amount_total for pos in deliveroo_pos])}
            door_dash_vals_dict={'count':len(door_dash_sale)+len(door_dash_pos),'amount':sum([i.amount_total for i in door_dash_sale])+sum([pos.amount_total for pos in door_dash_pos])}

            total_amount = uber_vals_dict.get('amount',0)+menulog_vals_dict.get('amount',0)+deliveroo_vals_dict.get('amount',0)+door_dash_vals_dict.get('amount',0)
            uber_vals_dict['percentage']=(uber_vals_dict.get('amount',0)/total_amount)*100
            menulog_vals_dict['percentage']=(menulog_vals_dict.get('amount',0)/total_amount)*100
            deliveroo_vals_dict['percentage']=(deliveroo_vals_dict.get('amount',0)/total_amount)*100
            door_dash_vals_dict['percentage']=(door_dash_vals_dict.get('amount',0)/total_amount)*100
            data = {'uber': uber_vals_dict, 'menulog': menulog_vals_dict, 'deliveroo': deliveroo_vals_dict, 'door_dash': door_dash_vals_dict}

        else:
            raise ValidationError(_('No orders provided during the selected dates.'))

        return {
            'data': data,
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docids,
            'start_date': datetime.strptime(start_date,'%Y-%m-%d').strftime("%m/%d/%Y"),
            'end_date': datetime.strptime(end_date,'%Y-%m-%d').strftime("%m/%d/%Y"),
        }