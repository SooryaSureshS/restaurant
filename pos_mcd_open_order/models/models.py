# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
import psycopg2
import time
from odoo.tools import float_is_zero
from odoo import models, fields, api, tools, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from datetime import datetime
from operator import itemgetter
from timeit import itertools
from itertools import groupby
import datetime
import time
from odoo.http import request

# Enable this checkbox for using kitchen screen


_logger = logging.getLogger(__name__)

class PosConfigKitchenPOsOrdersChange(models.Model):
    _name = 'change.order'

    product_id = fields.Many2one('product.product', string="Products")
    qty = fields.Integer(string='Qty', default=0)
    change_id = fields.Many2one('pos.order',string='Change Id', default=0)


class RestaurantPrinter(models.Model):
    _inherit = 'restaurant.printer'

    is_pass_printer = fields.Boolean('Is pass')

class PosConfigKitchenPOsOrders(models.Model):
    _inherit = 'pos.order'

    updated_order = fields.Boolean(string='Updated Order', readonly=True, copy=False)
    change_ids = fields.One2many('change.order', 'change_id', string='Tables', help='The list of Change orders')


    @api.model
    def get_tables_remove_change(self, product_id, qty, name):
        print("get tabledd removed",product_id,qty,name)
        changes = self.env['pos.order'].search([('pos_reference', '=', str(name))],limit=1)
        if changes:
            for i in changes:
                changes_obj = self.env['change.order'].create({
                    'product_id': int(product_id),
                    'qty': int(qty),
                    'change_id': i.id
                })
                if changes_obj:
                    return True
        return False

    @api.model
    def get_pos_orders_send(self, data,change_order,change_order_list):
        print(change_order_list)
        orders = self.env['pos.order'].search([('pos_reference', '=', str(data))],limit=1)
        pos_orders = []
        pos = []
        if orders:

            all_category = request.env['pos.category'].sudo().search([])

            all_category = [{'name': i.name, 'id': i.id} for i in all_category]

            user_type = orders.session_id.user_id

            from datetime import timedelta
            from datetime import datetime
            res_config_settings = request.env['ir.config_parameter'].sudo()
            pos_order_kitchen_display = res_config_settings.get_param('website_sale_hour.pos_order_kitchen_display')
            pos_order_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(pos_order_kitchen_display) * 60, 60))
            pos_kitchen_pre_order_time = datetime.strptime(pos_order_time, '%H:%M').time()
            pos_tot_secs = (
                                       pos_kitchen_pre_order_time.hour * 60 + pos_kitchen_pre_order_time.minute) * 60 + pos_kitchen_pre_order_time.second
            pos_min_kitchen_display_time = pos_tot_secs / 60
            categories_id = request.env.user.pos_category_ids.ids

            pos_count = 0
            tz = pytz.timezone(user_type.tz or 'UTC')
            for i in orders:
                t2 = i.date_order.astimezone(tz)
                list = []
                optional_line = []
                previous_line = False
                from datetime import timedelta
                from datetime import datetime
                min_time = 0
                if i.date_order:
                    current_date_time = datetime.now(tz).astimezone(tz)
                    time_now1 = current_date_time.replace(microsecond=0)
                    time_now = time_now1.replace(tzinfo=None)
                    order_time = i.date_order + timedelta(hours=10)
                    time_difference = time_now - order_time
                    sec_time = time_difference.total_seconds()
                    min_time = sec_time / 60
                # if i.date_order and pos_min_kitchen_display_time:
                order_status = ''
                count = 0
                for k in i.lines.filtered(
                        lambda r: int(r.pos_categ_id) in categories_id and r.pos_categ_id != False):
                    count += 1

                order_line_note_pos = ''
                for note in i.lines:
                    if note.note:
                        order_line_note_pos = note.note
                for line in i.lines.filtered(lambda r: int(
                        r.pos_categ_id) in categories_id and r.pos_categ_id != False and r.order_line_state):
                    if line.qty > 0 and line.qty - line.returned_qty > 0:
                        data = {
                            'create_date': line.create_date.astimezone(tz),
                            'floor': line.floor,
                            'full_product_name': line.full_product_name,
                            'id': line.id,
                            'name': line.name,
                            'order_line_note': line.order_line_note,
                            'order_line_state': line.order_line_state,
                            'product_uom_qty': line.qty - line.returned_qty,
                            'table': line.table,
                            'pos_categ_id': line.pos_categ_id,
                            'pos_categ_name': line.product_id.pos_categ_id.name,
                            'pos_categ_sequence': line.product_id.pos_categ_id.sequence or 0,
                            'customer': [line.customer.id, line.customer.name] or False,
                            'price_lst': line.product_id.lst_price or False,
                            'price': line.price_subtotal or False,
                            'discount': line.discount or False,
                            'price_display': line.price_subtotal_incl or False,
                            'product_id': line.product_id.id or False,
                            'preparation_time': line.preparation_time or False,
                            'preparation_estimation': line.preparation_date.astimezone(tz) + timedelta(
                                hours=0, minutes=line.preparation_time),
                            'is_optional': line.product_id.is_optional_product or False,
                            'website_delivery_type': 'pos_order',
                            'order_line_mark': line.order_line_mark or False,
                            'note': line.note or False,

                        }
                        if line.product_id.is_optional_product:
                            data['parent_line'] = previous_line
                            data['icon'] = line.product_id.product_option_group.icon or False
                            optional_line.append(data)
                        else:
                            previous_line = line.id
                            list.append(data)
                if len(list) > 0:
                    sorted_order_line = sorted(list, key=lambda k: k['pos_categ_sequence'])
                    order_line = []
                    for act_line in sorted_order_line:
                        order_line.append(act_line)
                        for opt in optional_line:
                            if act_line['id'] == opt['parent_line']:
                                order_line.append(opt)

                    dict = {
                        'name': i.name,
                        'partner_contact': i.partner_id.phone if i.partner_id else False,
                        'customer': [i.partner_id.id, i.partner_id.name] or False,
                        'order_id': i.id,
                        'pos_reference': i.pos_reference,
                        'lines': order_line,
                        'order_time': t2.strftime('%H:%M'),
                        'preparation_time': i.preparation_time,
                        'type': 'pos',
                        'amount_total': i.amount_total,
                        'amount_tax': i.amount_tax,
                        'preparation_date': i.preparation_date.astimezone(tz),
                        'preparation_estimation': i.preparation_date.astimezone(tz) + timedelta(hours=0,
                                                                                                minutes=i.preparation_time),
                        'kitchen_screen': i.kitchen_screen,
                        'website_delivery_type': 'pos_order',
                        'table': i.table_id.name,
                        'delivery_type': i.delivery_type,
                        'pos_order_note': i.note,
                        'order_status': order_status,
                        'delivery_note': i.delivery_note,
                        'date_order': i.date_order,
                        'order_sequence': i.order_sequence,
                        'filter_date': i.date_order,
                        'all_category': all_category,
                        'street': i.partner_id.street if i.partner_id else False,
                        'street2': i.partner_id.street2 if i.partner_id else False,
                        'city': i.partner_id.city if i.partner_id else False,
                        'zip': i.partner_id.zip if i.partner_id else False,
                    }

                    pos.append(dict)


        if bool(pos):
            vals= pos[0]
            vals['change_order']=change_order
            vals['change_list']=change_order_list
            return vals
        else:
            return {}