# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID
from odoo.http import request, route
from odoo.addons.bus.controllers.main import BusController
from odoo.http import Controller, route, request
from odoo import http
import time
from odoo import models, fields, api, tools, _
import pytz
import datetime
from datetime import date
from datetime import datetime
from odoo.addons.kitchen_order.controllers import order_template
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class BusControllerInherit(BusController):
    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            channels = list(channels)
            channels.append((request.db, 'pos.stock.channel'))
        return super(BusControllerInherit, self)._poll(dbname, channels, last, options)


class BoardLongPooling(Controller):

    @route('/longpolling/pollings', type="json", auth="public", cors="*", csrf=False)
    def PollFetchDataNew(self, session_id):
        pos = []
        order_sequence_pos = []
        so = []
        order_sequence_so = []

        message = False
        messages = request.env['message.kitchen'].sudo().search(
            [('send', '=', False), ('pos_session', '=', session_id)], order='id asc', limit=1)
        if messages:
            for m in messages:
                m.sudo().write({
                    'send': True,
                })
                message = 'Message from ' + m.user_name + " " + m.message

        sessions = request.env['pos.session'].sudo().search(
            [('id', '=', session_id)], limit=1)

        all_category = request.env['pos.category'].sudo().search([])
        all_category = [{'name':i.name,'id':i.id} for i in all_category]
        curb_popup = sessions.config_id.kerbside_popup
        user_type = sessions.user_id
        if sessions.config_id.uhc_product:
            data = self.uhc_products(user_type)
            all_order_uhc = data[0] + data[1]
            all_order_uhc = sorted(all_order_uhc, key=lambda k: k['date_order'])
            data.extend((message, 'uhc_product', all_order_uhc))
            return data
        elif sessions.config_id.fried_product:
            # TODO Fried
            data = self.fried_products(user_type)
            all_order_uhc = data[0] + data[1]
            all_order_uhc = sorted(all_order_uhc, key=lambda k: k['date_order'])
            data.extend((message, 'fried_product', all_order_uhc))
            print("data>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print(data)
            return data
        else:
            pos_domain = False
            if sessions.config_id.show_only_delivery_order:
                pos_domain = ('delivery_type', 'in', ['woosh', 'uber', 'door', 'menulog', 'deliveroo'])
            if sessions.config_id.show_all_order_expect_delivery:
                pos_domain = ('delivery_type', 'not in', ['woosh', 'uber', 'door', 'menulog', 'deliveroo'])
            is_cook = request.env.user.kitchen_screen_user
            categories_id = request.env.user.pos_category_ids.ids
            if is_cook == 'manager' or is_cook == 'admin':
                pos_order_line_domain = ['cancel', 'return', 'done']
                domain = [('lines.order_line_state', 'not in', ['cancel', 'done', 'return', False])]
                if pos_domain != False:
                    domain.append(pos_domain)
                pos_line = request.env['pos.order'].sudo().search(domain, order='date_order ASC')

            else:
                pos_order_line_domain = ['cancel', 'return', 'done', 'ready', 'delivering']
                domain = [
                    ('lines.order_line_state', 'not in', ['cancel', 'done', 'return', 'ready', 'delivering', False])]
                if pos_domain != False:
                    domain.append(pos_domain)
                pos_line = request.env['pos.order'].sudo().search(domain, order='date_order ASC', )

            from datetime import timedelta
            from datetime import datetime
            res_config_settings = request.env['ir.config_parameter'].sudo()
            pos_order_kitchen_display = res_config_settings.get_param('website_sale_hour.pos_order_kitchen_display')
            pos_order_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(pos_order_kitchen_display) * 60, 60))
            pos_kitchen_pre_order_time = datetime.strptime(pos_order_time, '%H:%M').time()
            pos_tot_secs = (
                                       pos_kitchen_pre_order_time.hour * 60 + pos_kitchen_pre_order_time.minute) * 60 + pos_kitchen_pre_order_time.second
            pos_min_kitchen_display_time = pos_tot_secs / 60

            pos_count = 0
            tz = pytz.timezone(user_type.tz or 'UTC')
            for i in pos_line:
                create_flter_date = False
                payment_ids = i.payment_ids.sorted(key='create_date', reverse=True)
                if payment_ids:
                    create_flter_date = payment_ids[0].create_date
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
                if i.date_order and pos_min_kitchen_display_time:
                    order_status = ''
                    waiting = 0
                    preparing = 0
                    delivery = 0
                    ready = 0
                    done = 0
                    count = 0
                    for k in i.lines.filtered(
                            lambda r: int(r.pos_categ_id) in categories_id and r.pos_categ_id != False):
                        count += 1
                        if k.order_line_state == 'waiting':
                            waiting += 1
                        if k.order_line_state == 'preparing':
                            preparing += 1
                        if k.order_line_state == 'ready':
                            ready += 1
                        if k.order_line_state == 'delivering':
                            delivery += 1
                        if k.order_line_state == 'done':
                            done += 1

                        if waiting > 0:
                            order_status = 'waiting'
                        elif preparing > 0:
                            order_status = 'preparing'
                        elif ready > 0:
                            order_status = 'ready'
                        elif delivery > 0:
                            order_status = 'delivering'
                        elif done > 0:
                            order_status = 'done'

                    order_line_note_pos = ''
                    if min_time >= pos_min_kitchen_display_time:
                        for note in i.lines:
                            if note.note:
                                order_line_note_pos = note.note

                        for line in i.lines.filtered(lambda r: int(
                                r.pos_categ_id) in categories_id and r.pos_categ_id != False and r.order_line_state not in pos_order_line_domain):
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
                                    'preparation_estimation': line.preparation_date.astimezone(tz) + timedelta(hours=0,
                                                                                                               minutes=line.preparation_time),
                                    'is_optional': line.product_id.is_optional_product or False,
                                    'website_delivery_type': 'pos_order',
                                    'order_line_mark': line.order_line_mark or False,
                                    'note': line.note or False,
                                    'disable_print': line.product_id.disable_print
                                }
                                if line.product_id.is_optional_product:
                                    data['parent_line'] = previous_line
                                    data['icon'] = line.product_id.product_option_group.icon or False
                                    optional_line.append(data)
                                else:
                                    previous_line = line.id
                                    list.append(data)
                        printed = []
                        if i.is_printed:
                            for p in i.is_printed:
                                printed.append(p.session.id)
                        if len(list) > 0:
                            sorted_order_line = sorted(list, key=lambda k: k['pos_categ_sequence'])
                            order_line = []
                            # print_order_line_all = []
                            parent_lines = [i['parent_line'] for i in optional_line if i['parent_line']]
                            for act_line in sorted_order_line:
                                # order_line.append(act_line)
                                if act_line['id'] not in parent_lines:
                                    flag = False
                                    for rece in order_line:
                                        if rece.get('product_id') == act_line.get('product_id') and rece[
                                            'id'] not in parent_lines:
                                            qty = rece.get('product_uom_qty') + act_line['product_uom_qty']
                                            rece['product_uom_qty'] = qty
                                            flag = True
                                    if not flag:
                                        order_line.append(act_line)
                                else:
                                    order_line.append(act_line)
                                    for opt in optional_line:
                                        if act_line['id'] == opt['parent_line']:
                                            order_line.append(opt)
                            dict = {
                                'name': i.name,
                                'partner_contact': i.partner_id.phone if i.partner_id else False,
                                'printed': printed or False,
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
                                'table': i.table_name,
                                'delivery_type': i.delivery_type,
                                'pos_order_note': i.note,
                                'order_status': order_status,
                                'delivery_note': i.delivery_note,
                                'date_order': i.date_order,
                                'order_sequence': i.order_sequence,
                                'filter_date': create_flter_date if create_flter_date else i.date_order,
                                'all_category': all_category,
                                'street': i.partner_id.street if i.partner_id else False,
                                'street2': i.partner_id.street2 if i.partner_id else False,
                                'city': i.partner_id.city if i.partner_id else False,
                                'zip': i.partner_id.zip if i.partner_id else False,
                            }
                            if i.order_sequence > 0:
                                order_sequence_pos.append(dict)
                            else:
                                pos.append(dict)
                    else:
                        pass
                else:
                    order_status = ''
                    waiting = 0
                    preparing = 0
                    delivery = 0
                    ready = 0
                    done = 0
                    count = 0
                    for k in i.lines.filtered(
                            lambda r: int(r.pos_categ_id) in categories_id and r.pos_categ_id != False):
                        count += 1
                        if k.order_line_state == 'waiting':
                            waiting += 1
                        if k.order_line_state == 'preparing':
                            preparing += 1
                        if k.order_line_state == 'ready':
                            ready += 1
                        if k.order_line_state == 'delivering':
                            delivery += 1
                        if k.order_line_state == 'done':
                            done += 1

                        if waiting > 0:
                            order_status = 'waiting'
                        elif preparing > 0:
                            order_status = 'preparing'
                        elif ready > 0:
                            order_status = 'ready'
                        elif delivery > 0:
                            order_status = 'delivering'
                        elif done > 0:
                            order_status = 'done'

                    order_line_note_pos = ''
                    for note in i.lines:
                        if note.note:
                            order_line_note_pos = note.note

                    for line in i.lines.filtered(lambda r: int(
                            r.pos_categ_id) in categories_id and r.pos_categ_id != False and r.order_line_state not in pos_order_line_domain):
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
                                'pos_categ_sequence': line.product_id.pos_categ_id.sequence or 0,
                                'pos_categ_name': line.product_id.pos_categ_id.name,
                                'customer': [line.customer.id, line.customer.name] or False,
                                'price_lst': line.product_id.lst_price or False,
                                'price': line.price_subtotal or False,
                                'discount': line.discount or False,
                                'price_display': line.price_subtotal_incl or False,
                                'product_id': line.product_id.id or False,
                                'preparation_time': line.preparation_time or False,
                                'preparation_estimation': line.preparation_date.astimezone(tz) + timedelta(hours=0,
                                                                                                           minutes=line.preparation_time) if line.preparation_date else False,
                                'is_optional': line.product_id.is_optional_product or False,
                                'website_delivery_type': 'pos_order',
                                'order_line_mark': line.order_line_mark or False,
                                'note': line.note or False,
                                'disable_print': line.product_id.disable_print

                            }
                            if line.product_id.is_optional_product:
                                data['parent_line'] = previous_line
                                data['icon'] = line.product_id.product_option_group.icon or False
                                optional_line.append(data)
                            else:
                                previous_line = line.id
                                list.append(data)
                    printed = []
                    if i.is_printed:
                        for p in i.is_printed:
                            printed.append(p.session.id)
                    if len(list) > 0:
                        sorted_order_line = sorted(list, key=lambda k: k['pos_categ_sequence'])
                        order_line = []
                        # print_order_line_all = []
                        parent_lines = [i['parent_line'] for i in optional_line if i['parent_line']]
                        for act_line in sorted_order_line:
                            # order_line.append(act_line)
                            if act_line['id'] not in parent_lines:
                                flag = False
                                for rece in order_line:
                                    if rece.get('product_id') == act_line.get('product_id') and rece[
                                        'id'] not in parent_lines:
                                        qty = rece.get('product_uom_qty') + act_line['product_uom_qty']
                                        rece['product_uom_qty'] = qty
                                        flag = True
                                if not flag:
                                    order_line.append(act_line)
                            else:
                                order_line.append(act_line)
                                for opt in optional_line:
                                    if act_line['id'] == opt['parent_line']:
                                        order_line.append(opt)
                        dict = {
                            'partner_contact': i.partner_id.phone if i.partner_id else False,
                            'name': i.name,
                            'printed': printed or False,
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
                            'table': i.table_name,
                            'delivery_type': i.delivery_type,
                            'pos_order_note': i.note,
                            'order_status': order_status,
                            'delivery_note': i.delivery_note,
                            'date_order': i.date_order,
                            'order_sequence': i.order_sequence,
                            'filter_date': create_flter_date if create_flter_date else i.date_order,
                            'all_category': all_category,
                            'street': i.partner_id.street if i.partner_id else False,
                            'street2': i.partner_id.street2 if i.partner_id else False,
                            'city': i.partner_id.city if i.partner_id else False,
                            'zip': i.partner_id.zip if i.partner_id else False,

                        }
                        if i.order_sequence > 0:
                            order_sequence_pos.append(dict)
                        else:
                            pos.append(dict)

            res_config_settings = request.env['ir.config_parameter'].sudo()
            pre_order_kitchen_display = res_config_settings.get_param('website_sale_hour.pre_order_kitchen_display')
            pre_order_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(pre_order_kitchen_display) * 60, 60))
            kitchen_pre_order_time = datetime.strptime(pre_order_time, '%H:%M').time()
            tot_secs = (
                                   kitchen_pre_order_time.hour * 60 + kitchen_pre_order_time.minute) * 60 + kitchen_pre_order_time.second
            min_kitchen_display_time = tot_secs / 60

            sale_domain = False
            if sessions.config_id.show_only_delivery_order:
                sale_domain = ('website_delivery_type', 'in', ['delivery'])
            if sessions.config_id.show_all_order_expect_delivery:
                sale_domain = ('website_delivery_type', 'not in', ['delivery'])

            if is_cook == 'manager' or is_cook == 'admin':
                search_domain = [('order_line.order_line_state', 'not in', ['cancel', 'return', 'done']),
                                 ('state', '=', 'sale'), ('parent_id', '=', False)]
                if sale_domain != False:
                    search_domain.append(sale_domain)
                so_line = request.env['sale.order'].sudo().search(search_domain, order='preparation_time ASC')
            else:
                search_domain = [
                    ('order_line.order_line_state', 'not in', ['cancel', 'return', 'done', 'ready', 'delivering']),
                    ('state', '=', 'sale'), ('parent_id', '=', False)]
                if sale_domain != False:
                    search_domain.append(sale_domain)
                # so_line = request.env['sale.order'].sudo().search(search_domain, order='date_order ASC')
                so_line = request.env['sale.order'].sudo().search(search_domain, order='preparation_time ASC')
            current_date_time = datetime.now()
            time_now = current_date_time.replace(microsecond=0)

            from datetime import timedelta
            from datetime import datetime
            res_config_settings = request.env['ir.config_parameter'].sudo()
            kvs_display_time = res_config_settings.get_param(
                'website_qr_order_merge.kvs_display_time')
            kvs_display_time_m = '{0:02.0f}:{1:02.0f}'.format(
                *divmod(float(kvs_display_time) * 60, 60))
            kvs_order_display_time = datetime.strptime(kvs_display_time_m, '%H:%M').time()
            kvs_order_display_time = (
                                                 kvs_order_display_time.hour * 60 + kvs_order_display_time.minute) * 60 + kvs_order_display_time.second
            kvs_order_display_time = kvs_order_display_time / 60

            current_uid = request.env.user
            user_type = request.env['res.users'].sudo().search([('id', '=', current_uid.id)])
            is_cook = user_type.kitchen_screen_user
            if not sessions.config_id.show_only_pos_order:
                for i in so_line:
                    # Pre order time filter starts
                    if sessions.config_id.enable_pre_order:
                        # if i.website_delivery_type in ['delivery','pickup','curb']:
                        if i.website_delivery_type == 'delivery' and i.pickup_date_string:
                            try:
                                session_pre_order = datetime.strptime(i.pickup_date_string, '%Y-%m-%d %H:%M:%S')
                            except:
                                session_pre_order = datetime.strptime(i.pickup_date_string, '%d/%m/%Y %H:%M')
                            session_prep_time = i.preparation_time + sessions.config_id.pre_order_time
                            session_order_time = session_pre_order - relativedelta(minutes=session_prep_time)
                            from datetime import datetime
                            session_kvs_current_date_time = datetime.now(tz).astimezone(tz)
                            session_kvs_current_date_time = session_kvs_current_date_time.replace(microsecond=0)
                            session_kvs_current_date_time = session_kvs_current_date_time.replace(tzinfo=None)
                            if session_kvs_current_date_time >= session_order_time:
                                pass
                            else:
                                continue
                        if i.website_delivery_type in ['pickup', 'curb'] and i.pickup_date_string:
                            try:
                                session_pre_order = datetime.strptime(i.pickup_date_string, '%Y-%m-%d %H:%M:%S')
                            except:
                                session_pre_order = datetime.strptime(i.pickup_date_string, '%d/%m/%Y %H:%M')
                            session_prep_time = i.preparation_time + sessions.config_id.pre_order_time
                            session_order_time = session_pre_order - relativedelta(minutes=session_prep_time)
                            from datetime import datetime
                            session_kvs_current_date_time = datetime.now(tz).astimezone(tz)
                            session_kvs_current_date_time = session_kvs_current_date_time.replace(microsecond=0)
                            session_kvs_current_date_time = session_kvs_current_date_time.replace(tzinfo=None)
                            if session_kvs_current_date_time >= session_order_time:
                                pass
                            else:
                                continue
                        if i.website_delivery_type in ['dine_in']:
                            try:
                                session_pre_order = datetime.strptime(i.pickup_date_string, '%Y-%m-%d %H:%M:%S')
                            except:
                                session_pre_order = datetime.strptime(i.pickup_date_string, '%d/%m/%Y %H:%M')
                            session_prep_time = i.preparation_time + sessions.config_id.pre_order_time
                            session_order_time = session_pre_order - relativedelta(minutes=session_prep_time)
                            from datetime import datetime
                            session_kvs_current_date_time = datetime.now(tz).astimezone(tz)
                            session_kvs_current_date_time = session_kvs_current_date_time.replace(microsecond=0)
                            session_kvs_current_date_time = session_kvs_current_date_time.replace(tzinfo=None)
                            if session_kvs_current_date_time >= session_order_time:
                                pass
                            else:
                                continue
                    # Pre order time filter end

                    list = []
                    optional_line = []
                    previous_line = False
                    filter_date = False
                    transaction_ids = i.transaction_ids.sorted(key='create_date', reverse=True)
                    if transaction_ids:
                        filter_date = transaction_ids[0].create_date
                        filter_date = filter_date - relativedelta(minutes=i.preparation_time)

                    if i.state == 'sale' and transaction_ids and transaction_ids[0].state in ['authorized','done']:
                        if i.pickup_date_string and not filter_date:
                            try:
                                filter_date = datetime.strptime(i.pickup_date_string, '%Y-%m-%d %H:%M:%S')
                                filter_date = filter_date - relativedelta(minutes=i.preparation_time)
                            except:
                                filter_date = datetime.strptime(i.pickup_date_string, '%d/%m/%Y %H:%M')
                                filter_date = filter_date - relativedelta(minutes=i.preparation_time)

                        t1 = i.date_order.astimezone(tz)
                        if i.website_delivery_type == 'dine_in':
                            from datetime import timedelta
                            from datetime import datetime
                            kvs_current_date_time = datetime.now(tz).astimezone(tz)
                            kvs_time_now1 = kvs_current_date_time.replace(microsecond=0)
                            kvs_time_now = kvs_time_now1.replace(tzinfo=None)
                            now = datetime.utcnow()
                            utc = pytz.timezone('UTC')
                            utc.localize(datetime.now())
                            delta = utc.localize(now) - tz.localize(now)
                            sec = delta.seconds
                            total_minute = sec / 60
                            kvs_order_time = i.date_order + timedelta(minutes=total_minute)
                            kvs_time_difference = kvs_time_now - kvs_order_time
                            kvs_sec_time = kvs_time_difference.total_seconds()
                            kvs_min_time = kvs_sec_time / 60

                            if kvs_min_time >= kvs_order_display_time:
                                pass
                            else:
                                continue
                        if is_cook == "manager" or is_cook == 'admin':
                            selected_line = False
                            selected_line_merge = False
                            if i.merge_order:
                                domain = [('order_line.order_line_state', 'not in', ['cancel', 'return', 'done']),
                                          ('state', '=', 'sale'), ('parent_id', '=', i.id)]
                                order_lines = request.env['sale.order'].sudo().search(domain,
                                                                                      order='date_order ASC').mapped(
                                    'order_line')
                                for lines in order_lines.filtered(
                                        lambda r: int(r.pos_categ_id) in categories_id and r.pos_categ_id != False and
                                                  r.order_line_state not in ['cancel', 'return',
                                                                             'done'] and r.product_id.is_optional_product == False):
                                    if lines:
                                        if not selected_line_merge:
                                            selected_line_merge = lines
                                        data = {
                                            'id': lines.id,
                                            'name': lines.name,
                                            'product_id': [lines.product_id.id, lines.product_id.name] or False,
                                            'product_uom_qty': lines.product_uom_qty,
                                            'order_line_note': lines.order_line_note,
                                            'order_line_state': lines.order_line_state,
                                            'create_date': lines.create_date.astimezone(tz),
                                            'order_partner_id': [lines.order_partner_id.id,
                                                                 lines.order_partner_id.name] or False,
                                            'pos_categ_id': lines.pos_categ_id,
                                            'pos_categ_sequence': lines.product_id.pos_categ_id.sequence or 0,
                                            'order_product_name': lines.order_product_name,
                                            'price_unit': lines.price_unit,
                                            'price_subtotal': lines.price_subtotal,
                                            'preparation_time': lines.preparation_time,
                                            'preparation_estimation': lines.preparation_date.astimezone(tz) + timedelta(
                                                hours=0, minutes=lines.preparation_time),
                                            'is_optional': lines.product_id.is_optional_product or False,
                                            'order_line_mark': lines.order_line_mark or False,
                                            'checkout_note': lines.checkout_note or False,
                                            'disable_print': lines.product_id.disable_print
                                        }
                                        list.append(data)
                                        for option in lines.option_line_ids:
                                            data = {
                                                'id': option.id,
                                                'name': option.name,
                                                'product_id': [option.product_id.id, option.product_id.name] or False,
                                                'product_uom_qty': option.product_uom_qty,
                                                'order_line_note': option.order_line_note,
                                                'order_line_state': option.order_line_state,
                                                'create_date': option.create_date.astimezone(tz),
                                                'order_partner_id': [option.order_partner_id.id,
                                                                     option.order_partner_id.name] or False,
                                                'pos_categ_id': option.pos_categ_id,
                                                'pos_categ_sequence': option.product_id.pos_categ_id.sequence or 0,

                                                'order_product_name': option.order_product_name,
                                                'price_unit': option.price_unit,
                                                'price_subtotal': option.price_subtotal,
                                                'preparation_time': option.preparation_time,
                                                'preparation_estimation': option.preparation_date.astimezone(
                                                    tz) + timedelta(
                                                    hours=0, minutes=option.preparation_time),
                                                'is_optional': option.product_id.is_optional_product or False,
                                                'parent_line': lines.id or False,
                                                'icon': option.product_id.product_option_group.icon or False,
                                                'disable_print': lines.product_id.disable_print
                                            }
                                            optional_line.append(data)
                            actual_min_time, actual_kitchen_display_time = self.action_preorder(i, res_config_settings,
                                                                                                tz)
                            if actual_min_time >= actual_kitchen_display_time:
                                for lines in i.order_line.filtered(
                                        lambda r: int(r.pos_categ_id) in categories_id and r.pos_categ_id != False and
                                                  r.order_line_state not in ['cancel', 'return', 'done'] and r.product_id.is_optional_product == False and r.bundle_child == False):
                                    if lines:
                                        if not selected_line:
                                            selected_line = lines
                                        if lines.preparation_date_delivery > selected_line.preparation_date_delivery:
                                            if lines.preparation_time_delivery > selected_line.preparation_time_delivery:
                                                selected_line = lines
                                        delivery_time_lines = False
                                        if i.pickup_date_string:
                                            delivery_time_lines = (datetime.strptime(i.pickup_date_string,'%d/%m/%Y %H:%M') + timedelta(hours=0, minutes=lines.preparation_time)).strftime('%H:%M')
                                        data = {
                                            'id': lines.id,
                                            'name': lines.name,
                                            'product_id': [lines.product_id.id, lines.product_id.name] or False,
                                            'product_uom_qty': lines.product_uom_qty,
                                            'order_line_note': lines.order_line_note,
                                            'order_line_state': lines.order_line_state,
                                            'create_date': lines.create_date.astimezone(tz),
                                            'order_partner_id': [lines.order_partner_id.id,
                                                                 lines.order_partner_id.name] or False,
                                            'pos_categ_id': lines.pos_categ_id,
                                            'pos_categ_sequence': lines.product_id.pos_categ_id.sequence or 0,
                                            'order_product_name': lines.order_product_name,
                                            'price_unit': lines.price_unit,
                                            'price_subtotal': lines.price_subtotal,
                                            'preparation_time': lines.preparation_time,
                                            'preparation_estimation': lines.preparation_date.astimezone(tz) + timedelta(hours=0, minutes=lines.preparation_time),
                                            'is_optional': lines.product_id.is_optional_product or False,
                                            'order_line_mark': lines.order_line_mark or False,
                                            'checkout_note': lines.checkout_note or False,
                                            'disable_print': lines.product_id.disable_print,
                                            'delivery_time_2': delivery_time_lines,
                                        }
                                        list.append(data)
                                        for option in lines.option_line_ids:
                                            delivery_time_options = False
                                            if i.pickup_date_string:
                                                delivery_time_options = (datetime.strptime(i.pickup_date_string,'%d/%m/%Y %H:%M') + timedelta(hours=0, minutes=option.preparation_time)).strftime('%H:%M')
                                            data = {
                                                'id': option.id,
                                                'name': option.name,
                                                'product_id': [option.product_id.id, option.product_id.name] or False,
                                                'product_uom_qty': option.product_uom_qty,
                                                'order_line_note': option.order_line_note,
                                                'order_line_state': option.order_line_state,
                                                'create_date': option.create_date.astimezone(tz),
                                                'order_partner_id': [option.order_partner_id.id,
                                                                     option.order_partner_id.name] or False,
                                                'pos_categ_id': option.pos_categ_id,
                                                'pos_categ_sequence': option.product_id.pos_categ_id.sequence or 0,

                                                'order_product_name': option.order_product_name,
                                                'price_unit': option.price_unit,
                                                'price_subtotal': option.price_subtotal,
                                                'preparation_time': option.preparation_time,
                                                'preparation_estimation': option.preparation_date.astimezone(tz) + timedelta(
                                                    hours=0, minutes=option.preparation_time),
                                                'is_optional': option.product_id.is_optional_product or False,
                                                'parent_line': lines.id or False,
                                                'icon': option.product_id.product_option_group.icon or False,
                                                'disable_print': lines.product_id.disable_print,
                                                'delivery_time_2': delivery_time_options,

                                            }
                                            optional_line.append(data)
                                printed = []
                                if i.is_printed:
                                    for p in i.is_printed:
                                        printed.append(p.session.id)
                                if len(list) > 0:
                                    sorted_order_line = sorted(list, key=lambda k: k['pos_categ_sequence'])
                                    order_line = []
                                    # print_order_line_all = []
                                    parent_lines = [i['parent_line'] for i in optional_line if i['parent_line']]
                                    for act_line in sorted_order_line:
                                        # order_line.append(act_line)
                                        if act_line['id'] not in parent_lines:
                                            flag = False
                                            for rece in order_line:
                                                if rece.get('product_id') == act_line.get('product_id') and rece[
                                                    'id'] not in parent_lines:
                                                    qty = rece.get('product_uom_qty') + act_line['product_uom_qty']
                                                    rece['product_uom_qty'] = qty
                                                    flag = True
                                            if not flag:
                                                order_line.append(act_line)
                                        else:
                                            order_line.append(act_line)
                                            for opt in optional_line:
                                                if act_line['id'] == opt['parent_line']:
                                                    order_line.append(opt)
                                    if not selected_line:
                                        selected_line = selected_line_merge
                                    pick_up_time_delivery = datetime.strptime(str((i.date_order.astimezone(
                                        tz) + timedelta(hours=0, minutes=selected_line.preparation_time)).replace(
                                        tzinfo=None)), '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M:%S')
                                    dict = {
                                        'delivery_time':datetime.strptime(str((selected_line.preparation_date_delivery.astimezone(
                                            tz) + timedelta(hours=0, minutes=selected_line.preparation_time_delivery)).replace(tzinfo=None)),
                                                                          '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M:%S') if selected_line else False,
                                        'order_id': [i.id, i.name] or False,
                                        'delivery_boy': i.delivery_boy.name,
                                        'pick_up_time_delivery':pick_up_time_delivery,
                                        'lines': order_line,
                                        'printed': printed or False,
                                        'customer': i.partner_id.name or False,
                                        'website_delivery_type': i.website_delivery_type or False,
                                        'checkout_note': i.checkout_note or False,
                                        'pickup_date_string': i.pickup_date_string or False,
                                        'updated_location': i.updated_location or False,
                                        'state': i.state or False,
                                        'vehicle_type': i.vehicle_type.type_name or False,
                                        'vehicle_make': i.vehicle_make.make_name or False,
                                        'approximate_location': i.approximate_location.location_name or False,
                                        'location_notes': i.location_notes or False,
                                        'vehicle_color': i.vehicle_color or False,
                                        'license_plate_no': i.license_plate_no or False,
                                        'order_time': t1.strftime('%H:%M'),
                                        'preparation_time': i.preparation_time,
                                        'type': 'sale',
                                        'amount_untaxed': i.amount_untaxed,
                                        'amount_tax': i.amount_tax,
                                        'amount_total': i.amount_total,
                                        'preparation_date': i.preparation_date,
                                        'preparation_estimation': i.preparation_date.astimezone(tz) + timedelta(
                                            hours=0, minutes=i.preparation_time),
                                        'kitchen_screen': i.kitchen_screen,
                                        'dine_in_table': i.dine_in_table.name,
                                        'delivery_address_street': i.partner_shipping_id.street,
                                        'delivery_address_street2': i.partner_shipping_id.street2,
                                        'delivery_address_city': i.partner_shipping_id.city,
                                        'delivery_address_state': i.partner_shipping_id.state_id.name,
                                        'delivery_address_zip': i.partner_shipping_id.zip,
                                        'delivery_address_country': i.partner_shipping_id.country_id.name,
                                        'partner_contact': i.partner_id.phone,
                                        'partner_email': i.partner_id.email,
                                        'date_order': i.date_order,
                                        'order_sequence': i.order_sequence,
                                        'filter_date': filter_date if filter_date else i.date_order,
                                        'is_hubster': i.is_hubster or False,
                                        'friendly_id': i.friendly_id or False,
                                        'all_category': all_category,
                                        'street': i.partner_id.street if i.partner_id else False,
                                        'street2': i.partner_id.street2 if i.partner_id else False,
                                        'city': i.partner_id.city if i.partner_id else False,
                                        'zip': i.partner_id.zip if i.partner_id else False,

                                    }
                                    if i.order_sequence > 0:
                                        order_sequence_so.append(dict)
                                    else:
                                        so.append(dict)
                        if is_cook == "cook":

                            from datetime import timedelta
                            from datetime import datetime
                            dine_in_order = False
                            min_time = 0
                            if i.pickup_date:
                                pre_order_kitchen_display = res_config_settings.get_param(
                                    'website_sale_hour.pre_order_kitchen_display')
                                pre_order_time = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(float(pre_order_kitchen_display) * 60, 60))
                                kitchen_pre_order_time = datetime.strptime(pre_order_time, '%H:%M').time()
                                tot_secs = (kitchen_pre_order_time.hour * 60 + kitchen_pre_order_time.minute) \
                                           * 60 + kitchen_pre_order_time.second
                                min_kitchen_display_time = tot_secs / 60
                                current_date_time = datetime.now(tz).astimezone(tz)
                                time_now1 = current_date_time.replace(microsecond=0)
                                time_now = time_now1.replace(tzinfo=None)
                                now = datetime.utcnow()
                                utc = pytz.timezone('UTC')
                                utc.localize(datetime.now())
                                delta = utc.localize(now) - tz.localize(now)
                                sec = delta.seconds
                                total_minute = sec / 60
                                order_time = i.date_order + timedelta(minutes=total_minute)
                                time_difference = time_now - order_time
                                sec_time = time_difference.total_seconds()
                                min_time = sec_time / 60
                            elif i.website_delivery_type == 'dine_in':
                                from datetime import timedelta
                                from datetime import datetime
                                res_config_settings = request.env['ir.config_parameter'].sudo()
                                pos_order_kitchen_display = res_config_settings.get_param(
                                    'website_sale_hour.pos_order_kitchen_display')
                                pos_order_time = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(float(pos_order_kitchen_display) * 60, 60))
                                pos_kitchen_pre_order_time = datetime.strptime(pos_order_time, '%H:%M').time()
                                pos_tot_secs = (
                                                           pos_kitchen_pre_order_time.hour * 60 + pos_kitchen_pre_order_time.minute) \
                                               * 60 + pos_kitchen_pre_order_time.second
                                min_kitchen_display_time = pos_tot_secs / 60

                                current_date_time = datetime.now(tz).astimezone(tz)
                                time_now1 = current_date_time.replace(microsecond=0)
                                time_now = time_now1.replace(tzinfo=None)
                                now = datetime.utcnow()
                                utc = pytz.timezone('UTC')
                                utc.localize(datetime.now())
                                delta = utc.localize(now) - tz.localize(now)
                                sec = delta.seconds
                                total_minute = sec / 60
                                order_time = i.date_order + timedelta(minutes=total_minute)
                                time_difference = time_now - order_time
                                sec_time = time_difference.total_seconds()
                                min_time = sec_time / 60
                                dine_in_order = True
                            if i.pickup_date and min_kitchen_display_time:
                                selected_line = False
                                if min_time >= min_kitchen_display_time:
                                    for lines in i.order_line.filtered(
                                            lambda r: int(r.pos_categ_id) in categories_id and r.pos_categ_id != False
                                                      and r.order_line_state not in ['cancel', 'return', 'done',
                                                                                     'ready',
                                                                                     'delivering'] and r.product_id.is_optional_product == False and r.bundle_child == False):
                                        if lines:
                                            if not selected_line:
                                                selected_line = lines
                                            if lines.preparation_date_delivery > selected_line.preparation_date_delivery:
                                                if lines.preparation_time_delivery > selected_line.preparation_time_delivery:
                                                    selected_line = lines
                                            data = {
                                                'id': lines.id,
                                                'name': lines.name,
                                                'product_id': [lines.product_id.id, lines.product_id.name] or False,
                                                'product_uom_qty': lines.product_uom_qty,
                                                'order_line_note': lines.order_line_note,
                                                'order_line_state': lines.order_line_state,
                                                'create_date': lines.create_date.astimezone(tz),
                                                'order_partner_id': [lines.order_partner_id.id,
                                                                     lines.order_partner_id.name] or False,
                                                'pos_categ_id': lines.pos_categ_id,
                                                'pos_categ_sequence': lines.product_id.pos_categ_id.sequence or 0,
                                                'order_product_name': lines.order_product_name,
                                                'price_unit': lines.price_unit,
                                                'price_subtotal': lines.price_subtotal,
                                                'preparation_time': lines.preparation_time,
                                                'preparation_estimation': lines.preparation_date.astimezone(
                                                    tz) + timedelta(hours=0, minutes=lines.preparation_time),
                                                'is_optional': lines.product_id.is_optional_product or False,
                                                'order_line_mark': lines.order_line_mark or False,
                                                'checkout_note': lines.checkout_note or False,
                                                'disable_print': lines.product_id.disable_print
                                            }
                                            list.append(data)

                                            for option in lines.option_line_ids:
                                                data = {
                                                    'id': option.id,
                                                    'name': option.name,
                                                    'product_id': [option.product_id.id,
                                                                   option.product_id.name] or False,
                                                    'product_uom_qty': option.product_uom_qty,
                                                    'order_line_note': option.order_line_note,
                                                    'order_line_state': option.order_line_state,
                                                    'create_date': option.create_date.astimezone(tz),
                                                    'order_partner_id': [option.order_partner_id.id,
                                                                         option.order_partner_id.name] or False,
                                                    'pos_categ_id': option.pos_categ_id,
                                                    'pos_categ_sequence': option.product_id.pos_categ_id.sequence or 0,
                                                    'parent_line': lines.id or False,
                                                    'order_product_name': option.order_product_name,
                                                    'price_unit': option.price_unit,
                                                    'price_subtotal': option.price_subtotal,
                                                    'preparation_time': option.preparation_time,
                                                    'preparation_estimation': option.preparation_date.astimezone(
                                                        tz) + timedelta(
                                                        hours=0, minutes=option.preparation_time),
                                                    'is_optional': option.product_id.is_optional_product or False,
                                                    'icon': option.product_id.product_option_group.icon or False,
                                                    'disable_print': lines.product_id.disable_print

                                                }
                                                optional_line.append(data)
                                    printed = []
                                    if i.is_printed:
                                        for p in i.is_printed:
                                            printed.append(p.session.id)
                                    if len(list) > 0:
                                        sorted_order_line = sorted(list, key=lambda k: k['pos_categ_sequence'])
                                        order_line = []
                                        # print_order_line_all = []
                                        parent_lines = [i['parent_line'] for i in optional_line if i['parent_line']]
                                        for act_line in sorted_order_line:
                                            # order_line.append(act_line)
                                            if act_line['id'] not in parent_lines:
                                                flag = False
                                                for rece in order_line:
                                                    if rece.get('product_id') == act_line.get('product_id') and rece[
                                                        'id'] not in parent_lines:
                                                        qty = rece.get('product_uom_qty') + act_line['product_uom_qty']
                                                        rece['product_uom_qty'] = qty
                                                        flag = True
                                                if not flag:
                                                    order_line.append(act_line)
                                            else:
                                                order_line.append(act_line)
                                                for opt in optional_line:
                                                    if act_line['id'] == opt['parent_line']:
                                                        order_line.append(opt)

                                        pick_up_time_delivery = datetime.strptime(str((i.date_order.astimezone(
                                            tz) + timedelta(hours=0, minutes=selected_line.preparation_time)).replace(
                                            tzinfo=None)), '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M:%S')

                                        dict = {
                                            'delivery_time': datetime.strptime(
                                                str((selected_line.preparation_date_delivery.astimezone(
                                                    tz) + timedelta(hours=0,
                                                                    minutes=selected_line.preparation_time_delivery)).replace(
                                                    tzinfo=None)),
                                                '%Y-%m-%d %H:%M:%S').strftime(
                                                '%m/%d/%Y %H:%M:%S') if selected_line else False,
                                            'order_id': [i.id, i.name] or False,
                                            'delivery_boy': i.delivery_boy.name,
                                            'printed': printed or False,
                                            'lines': order_line,
                                            'customer': i.partner_id.name or False,
                                            'website_delivery_type': i.website_delivery_type or False,
                                            'checkout_note': i.checkout_note or False,
                                            'order_time': t1.strftime('%H:%M'),
                                            'pick_up_time_delivery': pick_up_time_delivery,
                                            'preparation_time': i.preparation_time,
                                            'type': 'sale',
                                            'pickup_date_string': i.pickup_date_string or False,
                                            'updated_location': i.updated_location or False,
                                            'state': i.state or False,
                                            'amount_untaxed': i.amount_untaxed,
                                            'amount_tax': i.amount_tax,
                                            'amount_total': i.amount_total,
                                            'preparation_date': i.preparation_date,
                                            'preparation_estimation': i.preparation_date.astimezone(tz) + timedelta(
                                                hours=0, minutes=i.preparation_time),
                                            'kitchen_screen': i.kitchen_screen,
                                            'dine_in_table': i.dine_in_table.name,
                                            'delivery_address_street': i.partner_shipping_id.street,
                                            'delivery_address_street2': i.partner_shipping_id.street2,
                                            'delivery_address_city': i.partner_shipping_id.city,
                                            'delivery_address_state': i.partner_shipping_id.state_id.name,
                                            'delivery_address_zip': i.partner_shipping_id.zip,
                                            'delivery_address_country': i.partner_shipping_id.country_id.name,
                                            'partner_contact': i.partner_id.phone,
                                            'partner_email': i.partner_id.email,
                                            'date_order': i.date_order,
                                            'order_sequence': i.order_sequence,
                                            'filter_date': filter_date if filter_date else i.date_order,
                                            'is_hubster': i.is_hubster or False,
                                            'friendly_id': i.friendly_id or False,
                                            'all_category': all_category,
                                            'street': i.partner_id.street if i.partner_id else False,
                                            'street2': i.partner_id.street2 if i.partner_id else False,
                                            'city': i.partner_id.city if i.partner_id else False,
                                            'zip': i.partner_id.zip if i.partner_id else False,

                                        }
                                        if i.order_sequence > 0:
                                            order_sequence_so.append(dict)
                                        else:
                                            so.append(dict)
                            else:
                                selected_line = False
                                selected_line_merge = False
                                if dine_in_order:
                                    if min_time >= min_kitchen_display_time:
                                        if i.merge_order:
                                            domain = [
                                                ('order_line.order_line_state', 'not in', ['cancel', 'return', 'done']),
                                                ('state', '=', 'sale'), ('parent_id', '=', i.id)]
                                            order_lines = request.env['sale.order'].sudo().search(domain,
                                                                                                  order='date_order ASC').mapped(
                                                'order_line')
                                            for lines in order_lines.filtered(
                                                    lambda r: int(
                                                        r.pos_categ_id) in categories_id and r.pos_categ_id != False and
                                                              r.order_line_state not in ['cancel', 'return',
                                                                                         'done'] and r.product_id.is_optional_product == False):
                                                if lines:
                                                    if not selected_line_merge:
                                                        selected_line_merge = lines
                                                    data = {
                                                        'id': lines.id,
                                                        'name': lines.name,
                                                        'product_id': [lines.product_id.id,
                                                                       lines.product_id.name] or False,
                                                        'product_uom_qty': lines.product_uom_qty,
                                                        'order_line_note': lines.order_line_note,
                                                        'order_line_state': lines.order_line_state,
                                                        'create_date': lines.create_date.astimezone(tz),
                                                        'order_partner_id': [lines.order_partner_id.id,
                                                                             lines.order_partner_id.name] or False,
                                                        'pos_categ_id': lines.pos_categ_id,
                                                        'pos_categ_sequence': lines.product_id.pos_categ_id.sequence or 0,
                                                        'order_product_name': lines.order_product_name,
                                                        'price_unit': lines.price_unit,
                                                        'price_subtotal': lines.price_subtotal,
                                                        'preparation_time': lines.preparation_time,
                                                        'preparation_estimation': lines.preparation_date.astimezone(
                                                            tz) + timedelta(hours=0, minutes=lines.preparation_time),
                                                        'is_optional': lines.product_id.is_optional_product or False,
                                                        'order_line_mark': lines.order_line_mark or False,
                                                        'checkout_note': lines.checkout_note or False,
                                                        'disable_print': lines.product_id.disable_print
                                                    }
                                                    list.append(data)
                                                    for option in lines.option_line_ids:
                                                        data = {
                                                            'id': option.id,
                                                            'name': option.name,
                                                            'product_id': [option.product_id.id,
                                                                           option.product_id.name] or False,
                                                            'product_uom_qty': option.product_uom_qty,
                                                            'order_line_note': option.order_line_note,
                                                            'order_line_state': option.order_line_state,
                                                            'create_date': option.create_date.astimezone(tz),
                                                            'order_partner_id': [option.order_partner_id.id,
                                                                                 option.order_partner_id.name] or False,
                                                            'pos_categ_id': option.pos_categ_id,
                                                            'pos_categ_sequence': option.product_id.pos_categ_id.sequence or 0,

                                                            'order_product_name': option.order_product_name,
                                                            'price_unit': option.price_unit,
                                                            'price_subtotal': option.price_subtotal,
                                                            'preparation_time': option.preparation_time,
                                                            'preparation_estimation': option.preparation_date.astimezone(
                                                                tz) + timedelta(
                                                                hours=0, minutes=option.preparation_time),
                                                            'is_optional': option.product_id.is_optional_product or False,
                                                            'parent_line': lines.id or False,
                                                            'icon': option.product_id.product_option_group.icon or False,
                                                            'disable_print': lines.product_id.disable_print
                                                        }
                                                        optional_line.append(data)
                                        for lines in i.order_line.filtered(
                                                lambda r: int(
                                                    r.pos_categ_id) in categories_id and r.pos_categ_id != False
                                                          and r.order_line_state not in ['cancel', 'return', 'done',
                                                                                         'ready',
                                                                                         'delivering'] and r.product_id.is_optional_product == False and r.bundle_child == False):
                                            if lines:
                                                if not selected_line:
                                                    selected_line = lines
                                                if lines.preparation_date_delivery > selected_line.preparation_date_delivery:
                                                    if lines.preparation_time_delivery > selected_line.preparation_time_delivery:
                                                        selected_line = lines
                                                data = {
                                                    'id': lines.id,
                                                    'name': lines.name,
                                                    'product_id': [lines.product_id.id, lines.product_id.name] or False,
                                                    'product_uom_qty': lines.product_uom_qty,
                                                    'order_line_note': lines.order_line_note,
                                                    'order_line_state': lines.order_line_state,
                                                    'create_date': lines.create_date.astimezone(tz),
                                                    'order_partner_id': [lines.order_partner_id.id,
                                                                         lines.order_partner_id.name] or False,
                                                    'pos_categ_id': lines.pos_categ_id,
                                                    'pos_categ_sequence': lines.product_id.pos_categ_id.sequence or 0,
                                                    'order_product_name': lines.order_product_name,
                                                    'price_unit': lines.price_unit,
                                                    'price_subtotal': lines.price_subtotal,
                                                    'preparation_time': lines.preparation_time,
                                                    'preparation_estimation': lines.preparation_date.astimezone(
                                                        tz) + timedelta(
                                                        hours=0, minutes=lines.preparation_time),
                                                    'is_optional': lines.product_id.is_optional_product or False,
                                                    'order_line_mark': lines.order_line_mark or False,
                                                    'checkout_note': lines.checkout_note or False,
                                                    'disable_print': lines.product_id.disable_print
                                                }
                                                list.append(data)

                                                for option in lines.option_line_ids:
                                                    data = {
                                                        'id': option.id,
                                                        'name': option.name,
                                                        'product_id': [option.product_id.id,
                                                                       option.product_id.name] or False,
                                                        'product_uom_qty': option.product_uom_qty,
                                                        'order_line_note': option.order_line_note,
                                                        'order_line_state': option.order_line_state,
                                                        'create_date': option.create_date.astimezone(tz),
                                                        'order_partner_id': [option.order_partner_id.id,
                                                                             option.order_partner_id.name] or False,
                                                        'pos_categ_id': option.pos_categ_id,
                                                        'pos_categ_sequence': option.product_id.pos_categ_id.sequence or 0,
                                                        'order_product_name': option.order_product_name,
                                                        'price_unit': option.price_unit,
                                                        'price_subtotal': option.price_subtotal,
                                                        'preparation_time': option.preparation_time,
                                                        'parent_line': lines.id or False,
                                                        'preparation_estimation': option.preparation_date.astimezone(
                                                            tz) + timedelta(
                                                            hours=0, minutes=option.preparation_time),
                                                        'is_optional': option.product_id.is_optional_product or False,
                                                        'icon': option.product_id.product_option_group.icon or False,
                                                        'disable_print': lines.product_id.disable_print

                                                    }
                                                    optional_line.append(data)
                                        printed = []
                                        if i.is_printed:
                                            for p in i.is_printed:
                                                printed.append(p.session.id)
                                        if len(list) > 0:
                                            sorted_order_line = sorted(list, key=lambda k: k['pos_categ_sequence'])
                                            order_line = []
                                            # print_order_line_all = []
                                            parent_lines = [i['parent_line'] for i in optional_line if i['parent_line']]
                                            for act_line in sorted_order_line:
                                                # order_line.append(act_line)
                                                if act_line['id'] not in parent_lines:
                                                    flag = False
                                                    for rece in order_line:
                                                        if rece.get('product_id') == act_line.get('product_id') and \
                                                                rece[
                                                                    'id'] not in parent_lines:
                                                            qty = rece.get('product_uom_qty') + act_line[
                                                                'product_uom_qty']
                                                            rece['product_uom_qty'] = qty
                                                            flag = True
                                                    if not flag:
                                                        order_line.append(act_line)
                                                else:
                                                    order_line.append(act_line)
                                                    for opt in optional_line:
                                                        if act_line['id'] == opt['parent_line']:
                                                            order_line.append(opt)
                                            if not selected_line:
                                                selected_line = selected_line_merge
                                            pick_up_time_delivery = datetime.strptime(str((i.date_order.astimezone(
                                                tz) + timedelta(hours=0,
                                                                minutes=selected_line.preparation_time)).replace(
                                                tzinfo=None)), '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M:%S')

                                            dict = {
                                                'delivery_time': datetime.strptime(
                                                    str((selected_line.preparation_date_delivery.astimezone(
                                                        tz) + timedelta(hours=0,
                                                                        minutes=selected_line.preparation_time_delivery)).replace(
                                                        tzinfo=None)),
                                                    '%Y-%m-%d %H:%M:%S').strftime(
                                                    '%m/%d/%Y %H:%M:%S') if selected_line else False,
                                                'order_id': [i.id, i.name] or False,
                                                'delivery_boy': i.delivery_boy.name,
                                                'printed': printed or False,
                                                'lines': order_line,
                                                'customer': i.partner_id.name or False,
                                                'website_delivery_type': i.website_delivery_type or False,
                                                'checkout_note': i.checkout_note or False,
                                                'order_time': t1.strftime('%H:%M'),
                                                'pick_up_time_delivery': pick_up_time_delivery,
                                                'preparation_time': i.preparation_time,
                                                'pickup_date_string': i.pickup_date_string or False,
                                                'type': 'sale',
                                                'order_sequence': i.order_sequence,
                                                'amount_untaxed': i.amount_untaxed,
                                                'amount_tax': i.amount_tax,
                                                'amount_total': i.amount_total,
                                                'preparation_date': i.preparation_date,
                                                'preparation_estimation': i.preparation_date.astimezone(tz) + timedelta(
                                                    hours=0, minutes=i.preparation_time),
                                                'kitchen_screen': i.kitchen_screen,
                                                'dine_in_table': i.dine_in_table.name,
                                                'delivery_address_street': i.partner_shipping_id.street,
                                                'delivery_address_street2': i.partner_shipping_id.street2,
                                                'delivery_address_city': i.partner_shipping_id.city,
                                                'delivery_address_state': i.partner_shipping_id.state_id.name,
                                                'delivery_address_zip': i.partner_shipping_id.zip,
                                                'delivery_address_country': i.partner_shipping_id.country_id.name,
                                                'partner_contact': i.partner_id.phone,
                                                'updated_location': i.updated_location or False,
                                                'state': i.state or False,
                                                'partner_email': i.partner_id.email,
                                                'date_order': i.date_order,
                                                'filter_date': filter_date if filter_date else i.date_order,
                                                'is_hubster': i.is_hubster or False,
                                                'friendly_id': i.friendly_id or False,
                                                'all_category': all_category,
                                                'street': i.partner_id.street if i.partner_id else False,
                                                'street2': i.partner_id.street2 if i.partner_id else False,
                                                'city': i.partner_id.city if i.partner_id else False,
                                                'zip': i.partner_id.zip if i.partner_id else False,
                                            }
                                            if i.order_sequence > 0:
                                                order_sequence_so.append(dict)
                                            else:
                                                so.append(dict)

                                else:
                                    selected_line = False
                                    for lines in i.order_line.filtered(
                                            lambda r: int(r.pos_categ_id) in categories_id and r.pos_categ_id != False
                                                      and r.order_line_state not in ['cancel', 'return', 'done',
                                                                                     'ready',
                                                                                     'delivering'] and r.product_id.is_optional_product == False and r.bundle_child == False):
                                        if lines:

                                            if not selected_line:
                                                selected_line = lines
                                            if lines.preparation_date_delivery > selected_line.preparation_date_delivery:
                                                if lines.preparation_time_delivery > selected_line.preparation_time_delivery:
                                                    selected_line = lines
                                            data = {
                                                'delivery_time': datetime.strptime(
                                                    str((selected_line.preparation_date_delivery.astimezone(
                                                        tz) + timedelta(hours=0,
                                                                        minutes=selected_line.preparation_time_delivery)).replace(
                                                        tzinfo=None)),
                                                    '%Y-%m-%d %H:%M:%S').strftime(
                                                    '%m/%d/%Y %H:%M:%S') if selected_line else False,
                                                'id': lines.id,
                                                'name': lines.name,
                                                'product_id': [lines.product_id.id, lines.product_id.name] or False,
                                                'product_uom_qty': lines.product_uom_qty,
                                                'order_line_note': lines.order_line_note,
                                                'order_line_state': lines.order_line_state,
                                                'create_date': lines.create_date.astimezone(tz),
                                                'order_partner_id': [lines.order_partner_id.id,
                                                                     lines.order_partner_id.name] or False,
                                                'pos_categ_id': lines.pos_categ_id,
                                                'pos_categ_sequence': lines.product_id.pos_categ_id.sequence or 0,

                                                'order_product_name': lines.order_product_name,
                                                'price_unit': lines.price_unit,
                                                'price_subtotal': lines.price_subtotal,
                                                'preparation_time': lines.preparation_time,
                                                'preparation_estimation': lines.preparation_date.astimezone(
                                                    tz) + timedelta(
                                                    hours=0, minutes=lines.preparation_time),
                                                'is_optional': lines.product_id.is_optional_product or False,
                                                'order_line_mark': lines.order_line_mark or False,
                                                'checkout_note': lines.checkout_note or False,
                                                'disable_print': lines.product_id.disable_print
                                            }
                                            list.append(data)

                                            for option in lines.option_line_ids:
                                                data = {
                                                    'id': option.id,
                                                    'name': option.name,
                                                    'product_id': [option.product_id.id,
                                                                   option.product_id.name] or False,
                                                    'product_uom_qty': option.product_uom_qty,
                                                    'order_line_note': option.order_line_note,
                                                    'order_line_state': option.order_line_state,
                                                    'create_date': option.create_date.astimezone(tz),
                                                    'order_partner_id': [option.order_partner_id.id,
                                                                         option.order_partner_id.name] or False,
                                                    'pos_categ_id': option.pos_categ_id,
                                                    'pos_categ_sequence': option.product_id.pos_categ_id.sequence or 0,
                                                    'order_product_name': option.order_product_name,
                                                    'price_unit': option.price_unit,
                                                    'price_subtotal': option.price_subtotal,
                                                    'preparation_time': option.preparation_time,
                                                    'preparation_estimation': option.preparation_date.astimezone(
                                                        tz) + timedelta(
                                                        hours=0, minutes=option.preparation_time),
                                                    'is_optional': option.product_id.is_optional_product or False,
                                                    'parent_line': lines.id or False,
                                                    'icon': option.product_id.product_option_group.icon or False,
                                                    'disable_print': lines.product_id.disable_print

                                                }
                                                optional_line.append(data)
                                    printed = []
                                    if i.is_printed:
                                        for p in i.is_printed:
                                            printed.append(p.session.id)
                                    if len(list) > 0:
                                        sorted_order_line = sorted(list, key=lambda k: k['pos_categ_sequence'])
                                        order_line = []
                                        # print_order_line_all = []
                                        parent_lines = [i['parent_line'] for i in optional_line if i['parent_line']]
                                        for act_line in sorted_order_line:
                                            # order_line.append(act_line)
                                            if act_line['id'] not in parent_lines:
                                                flag = False
                                                for rece in order_line:
                                                    if rece.get('product_id') == act_line.get('product_id') and rece[
                                                        'id'] not in parent_lines:
                                                        qty = rece.get('product_uom_qty') + act_line['product_uom_qty']
                                                        rece['product_uom_qty'] = qty
                                                        flag = True
                                                if not flag:
                                                    order_line.append(act_line)
                                            else:
                                                order_line.append(act_line)
                                                for opt in optional_line:
                                                    if act_line['id'] == opt['parent_line']:
                                                        order_line.append(opt)
                                        pick_up_time_delivery = datetime.strptime(str((i.date_order.astimezone(
                                            tz) + timedelta(hours=0, minutes=selected_line.preparation_time)).replace(
                                            tzinfo=None)), '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M:%S')

                                        dict = {
                                            'delivery_time': datetime.strptime(
                                                str((selected_line.preparation_date_delivery.astimezone(
                                                    tz) + timedelta(hours=0,
                                                                    minutes=selected_line.preparation_time_delivery)).replace(
                                                    tzinfo=None)), '%Y-%m-%d %H:%M:%S').strftime(
                                                '%m/%d/%Y %H:%M:%S') if selected_line else False,
                                            'order_id': [i.id, i.name] or False,
                                            'delivery_boy': i.delivery_boy.name,
                                            'printed': printed or False,
                                            'lines': order_line,
                                            'order_sequence': i.order_sequence,
                                            'customer': i.partner_id.name or False,
                                            'website_delivery_type': i.website_delivery_type or False,
                                            'checkout_note': i.checkout_note or False,
                                            'order_time': t1.strftime('%H:%M'),
                                            'pick_up_time_delivery': pick_up_time_delivery,
                                            'preparation_time': i.preparation_time,
                                            'pickup_date_string': i.pickup_date_string or False,
                                            'type': 'sale',
                                            'amount_untaxed': i.amount_untaxed,
                                            'amount_tax': i.amount_tax,
                                            'amount_total': i.amount_total,
                                            'preparation_date': i.preparation_date,
                                            'preparation_estimation': i.preparation_date.astimezone(tz) + timedelta(
                                                hours=0, minutes=i.preparation_time),
                                            'kitchen_screen': i.kitchen_screen,
                                            'updated_location': i.updated_location or False,
                                            'state': i.state or False,
                                            'dine_in_table': i.dine_in_table.name,
                                            'delivery_address_street': i.partner_shipping_id.street,
                                            'delivery_address_street2': i.partner_shipping_id.street2,
                                            'delivery_address_city': i.partner_shipping_id.city,
                                            'delivery_address_state': i.partner_shipping_id.state_id.name,
                                            'delivery_address_zip': i.partner_shipping_id.zip,
                                            'delivery_address_country': i.partner_shipping_id.country_id.name,
                                            'partner_contact': i.partner_id.phone,
                                            'partner_email': i.partner_id.email,
                                            'date_order': i.date_order,
                                            'filter_date': filter_date if filter_date else i.date_order,
                                            'is_hubster': i.is_hubster or False,
                                            'friendly_id': i.friendly_id or False,
                                            'all_category': all_category,
                                            'street': i.partner_id.street if i.partner_id else False,
                                            'street2': i.partner_id.street2 if i.partner_id else False,
                                            'city': i.partner_id.city if i.partner_id else False,
                                            'zip': i.partner_id.zip if i.partner_id else False,
                                        }
                                        if i.order_sequence > 0:
                                            order_sequence_so.append(dict)
                                        else:
                                            so.append(dict)

            all_order = pos + so
            all_order_index = len(all_order)
            if all_order_index > 0:
                all_order_without_sq = sorted(all_order, key=lambda k: k['filter_date'])
                # for order in :
                #     if order.get('order_sequence',0)>0:
                #         if order.get('order_sequence')-1<= all_order_index:
                #             all_order.insert(order.get('order_sequence')-1,order)
                #         else:
                #             all_order.append(order)
                all_order = sorted(order_sequence_so + order_sequence_pos, key=lambda k: k['order_sequence'])
                all_order = all_order + all_order_without_sq
            else:
                all_order = order_sequence_so + order_sequence_pos
                # all_order = sorted(all_order, key=lambda k: k['order_sequence'])

            all_pos = sorted(order_sequence_pos + pos, key=lambda k: k['filter_date'])
            all_sale = sorted(order_sequence_so + so, key=lambda k: k['filter_date'])
            return [all_pos, all_sale, len(all_pos), len(all_sale), message, 'not_uhc_product', all_order, curb_popup]

    def uhc_products(self, user_type):
        pos = []
        so = []
        is_cook = user_type.kitchen_screen_user
        categories_id = user_type.pos_category_ids.ids

        pos_line = request.env['pos.order'].sudo().search(
                [('lines.order_line_state', 'not in', ['cancel', 'done', 'return', 'ready', 'delivering', False])],
                order='date_order ASC')

        from datetime import timedelta
        from datetime import datetime
        pos_count = 0
        tz = pytz.timezone(user_type.tz or 'UTC')
        for i in pos_line:
            t2 = i.date_order.astimezone(tz)
            order_line = []
            order_line_note_pos = ''
            for note in i.lines:
                if note.note:
                    order_line_note_pos = note.note

            for line in i.lines.filtered(lambda r: int(r.pos_categ_id) in categories_id and r.pos_categ_id != False and
                                         r.uhc_state not in ['finish']):
                 if line.product_id.uhc_products:
                     for opt_product in line.product_id.uhc_products:
                            data = {
                                'create_date': line.create_date.astimezone(tz),
                                'floor': line.floor,
                                'full_product_name': opt_product.name,
                                'id': line.id,
                                'name': line.name,
                                'note': line.note,
                                'order_line_note': line.order_line_note,
                                'order_line_state': line.order_line_state,
                                'uhc_state':line.uhc_state,
                                'product_uom_qty': line.qty,
                                'table': line.table,
                                'pos_categ_id': line.pos_categ_id,
                                'customer': [line.customer.id, line.customer.name] or False,
                                'price_lst': line.product_id.lst_price or False,
                                'price': line.price_subtotal or False,
                                'discount': line.discount or False,
                                'price_display': line.price_subtotal_incl or False,
                                'product_id': line.product_id.id or False,
                                'preparation_time': line.preparation_time or False,
                                'preparation_estimation': line.preparation_date.astimezone(tz) + timedelta(hours=0,minutes=line.preparation_time),
                                'website_delivery_type': 'pos_order',
                                'disable_print': line.product_id.disable_print
                            }
                            order_line.append(data)
            if len(order_line)>=1:
                main_order = {
                    'name': i.name,
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
                    'preparation_estimation': i.preparation_date.astimezone(tz) + timedelta(hours=0,minutes=i.preparation_time),
                    'kitchen_screen': i.kitchen_screen,
                    'website_delivery_type': 'pos_order',
                    'table': i.table_name,
                    'delivery_type': i.delivery_type,
                    'pos_order_note': i.note,
                    'date_order': i.date_order
                }
                pos.append(main_order)

        # sale order
        res_config_settings = request.env['ir.config_parameter'].sudo()
        pre_order_kitchen_display = res_config_settings.get_param('website_sale_hour.pre_order_kitchen_display')
        pre_order_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(pre_order_kitchen_display) * 60, 60))
        kitchen_pre_order_time = datetime.strptime(pre_order_time, '%H:%M').time()
        tot_secs = (kitchen_pre_order_time.hour * 60 + kitchen_pre_order_time.minute) * 60 + kitchen_pre_order_time.second
        min_kitchen_display_time = tot_secs / 60

        so_line = request.env['sale.order'].sudo().search(
                [('order_line.order_line_state', 'not in', ['cancel', 'return', 'done', 'ready', 'delivering'])],
                order='date_order ASC')
        current_date_time = datetime.now()
        time_now = current_date_time.replace(microsecond=0)
        current_uid = request.env.user
        user_type = request.env['res.users'].sudo().search([('id', '=', current_uid.id)])
        is_cook = user_type.kitchen_screen_user
        for i in so_line:
            order_line = []
            if i.state == 'sale':
                t1 = i.date_order.astimezone(tz)
                from datetime import timedelta
                from datetime import datetime
                min_time = 0
                if i.pickup_date:
                    current_date_time = datetime.now(tz).astimezone(tz)
                    time_now1 = current_date_time.replace(microsecond=0)
                    time_now = time_now1.replace(tzinfo=None)
                    time_difference = i.pickup_date - time_now
                    sec_time = time_difference.total_seconds()
                    min_time = sec_time / 60
                if i.pickup_date and min_kitchen_display_time:
                    if min_time <= min_kitchen_display_time:
                        for lines in i.order_line.filtered(
                                lambda r: int(r.pos_categ_id) in categories_id and r.pos_categ_id != False
                                          and r.order_line_state not in ['cancel', 'return', 'done', 'ready','delivering'] and r.uhc_state not in ['finish']):
                            if lines:
                                if lines.product_id.uhc_products:
                                    for opt_product in lines.product_id.uhc_products:
                                        data = {
                                            'uhc_state':lines.uhc_state,
                                            'id': lines.id,
                                            'name': lines.name,
                                            'product_id': [lines.product_id.id, opt_product.name] or False,
                                            'product_uom_qty': lines.product_uom_qty,
                                            'order_line_note': lines.order_line_note,
                                            'order_line_state': lines.order_line_state,
                                            'create_date': lines.create_date.astimezone(tz),
                                            'order_partner_id': [lines.order_partner_id.id,
                                                                 lines.order_partner_id.name] or False,
                                            'pos_categ_id': lines.pos_categ_id,
                                            'order_product_name': opt_product.name,
                                            'price_unit': lines.price_unit,
                                            'price_subtotal': lines.price_subtotal,
                                            'preparation_time': lines.preparation_time,
                                            'preparation_estimation': lines.preparation_date.astimezone(tz) + timedelta(hours=0,
                                                                                                                        minutes=lines.preparation_time),
                                            'is_optional': lines.product_id.is_optional_product or False,
                                            'disable_print': lines.product_id.disable_print
                                        }
                                        order_line.append(data)
                        if len(order_line)>=1:
                            order_main = {
                                'order_id': [i.id, i.name] or False,
                                'delivery_boy': i.delivery_boy.name,
                                'lines': order_line,
                                'customer': i.partner_id.name or False,
                                'partner_contact': i.partner_id.phone or False,
                                'website_delivery_type': i.website_delivery_type or False,
                                'checkout_note': i.checkout_note or False,
                                'order_time': t1.strftime('%H:%M'),
                                'preparation_time': i.preparation_time,
                                'type': 'sale',
                                'updated_location': i.updated_location or False,
                                'state': i.state or False,
                                'amount_untaxed': i.amount_untaxed,
                                'amount_tax': i.amount_tax,
                                'amount_total': i.amount_total,
                                'preparation_date': i.preparation_date,
                                'preparation_estimation': i.preparation_date.astimezone(tz) + timedelta(
                                    hours=0, minutes=i.preparation_time),
                                'kitchen_screen': i.kitchen_screen,
                                'date_order': i.date_order
                            }
                            so.append(order_main)
                else:
                    for lines in i.order_line.filtered(
                            lambda r: int(r.pos_categ_id) in categories_id and r.pos_categ_id != False
                                      and r.order_line_state not in ['cancel', 'return', 'done', 'ready',
                                                                     'delivering'] and r.uhc_state not in ['finish']):
                        if lines:
                            if lines.product_id.uhc_products:
                                for opt_product in lines.product_id.uhc_products:
                                    data = {
                                        'uhc_state': lines.uhc_state,
                                        'id': lines.id,
                                        'name': lines.name,
                                        'product_id': [lines.product_id.id, opt_product.name] or False,
                                        'product_uom_qty': lines.product_uom_qty,
                                        'order_line_note': lines.order_line_note,
                                        'order_line_state': lines.order_line_state,
                                        'create_date': lines.create_date.astimezone(tz),
                                        'order_partner_id': [lines.order_partner_id.id,
                                                             lines.order_partner_id.name] or False,
                                        'pos_categ_id': lines.pos_categ_id,
                                        'order_product_name': opt_product.name,
                                        'price_unit': lines.price_unit,
                                        'price_subtotal': lines.price_subtotal,
                                        'preparation_time': lines.preparation_time,
                                        'preparation_estimation': lines.preparation_date.astimezone(tz) + timedelta(
                                            hours=0,
                                            minutes=lines.preparation_time),
                                        'is_optional': lines.product_id.is_optional_product or False,
                                        'disable_print': lines.product_id.disable_print
                                    }
                                    order_line.append(data)
                    if len(order_line) >= 1:
                        order_main = {
                            'order_id': [i.id, i.name] or False,
                            'delivery_boy': i.delivery_boy.name,
                            'lines': order_line,
                            'customer': i.partner_id.name or False,
                            'partner_contact': i.partner_id.phone or False,
                            'website_delivery_type': i.website_delivery_type or False,
                            'checkout_note': i.checkout_note or False,
                            'order_time': t1.strftime('%H:%M'),
                            'preparation_time': i.preparation_time,
                            'type': 'sale',
                            'updated_location': i.updated_location or False,
                            'state': i.state or False,
                            'amount_untaxed': i.amount_untaxed,
                            'amount_tax': i.amount_tax,
                            'amount_total': i.amount_total,
                            'preparation_date': i.preparation_date,
                            'preparation_estimation': i.preparation_date.astimezone(tz) + timedelta(
                                hours=0, minutes=i.preparation_time),
                            'kitchen_screen': i.kitchen_screen,
                            'date_order': i.date_order
                        }
                        so.append(order_main)
        return [pos, so, len(pos), len(so)]

    def fried_products(self, user_type):
        from datetime import timedelta
        pos = []
        so = []

        # pos order

        domain = [
            ('lines.order_line_state', 'not in', ['cancel', 'done', 'return', 'ready', 'delivering', False]),
            ('fried_state', 'not in', ['finish', False])
        ]
        pos_line = request.env['pos.order'].sudo().search(domain, order='date_order ASC')
        from datetime import datetime
        tz = pytz.timezone(user_type.tz or 'UTC')
        for i in pos_line:
            t2 = i.date_order.astimezone(tz)
            order_line = []
            for line in i.lines.filtered(
                    lambda r: r.order_line_state not in ['cancel', 'done', 'return', 'ready', 'delivering', False]):
                if line.product_id.fried_products:
                    if line.fried_ids:
                        pass
                    else:
                        for fp in line.product_id.fried_products:
                            request.env['pos.kitchen.fried.line'].sudo().create({
                                'product_id': fp.id,
                                'pos_line_id': line.id
                            })
                    request.env.cr.commit()
                    for fried_id in line.fried_ids:
                        data = {
                            'full_product_name': fried_id.product_id.name,
                            'id': fried_id.id,
                            'product_uom_qty': line.qty,
                            'product_name': line.product_id.name,
                            'preparation_estimation': line.preparation_date.astimezone(
                                tz) + timedelta(
                                hours=0, minutes=line.preparation_time),
                            'product_id': line.product_id.id or False
                        }
                        order_line.append(data)
            printed = []
            if i.is_printed:
                for p in i.is_printed:
                    printed.append(p.session.id)
            if len(order_line)>=1:
                main_order = {
                    'name': i.name,
                    'type': 'pos',
                    'customer': [i.partner_id.id, i.partner_id.name] or False,
                    'partner_contact': i.partner_id.phone if i.partner_id.phone else False,
                    'order_id': i.id,
                    'pos_reference': i.pos_reference,
                    'lines': order_line,
                    'order_status': i.fried_state,
                    'order_time': t2.strftime('%H:%M'),
                    'printed': printed,
                    'kitchen_screen': i.kitchen_screen,
                    'preparation_time': i.preparation_time,
                    'preparation_date': i.preparation_date.astimezone(tz),
                    'preparation_estimation': i.preparation_date.astimezone(tz) + timedelta(hours=0,
                                                                                            minutes=i.preparation_time),
                    'date_order': i.date_order
                }
                pos.append(main_order)

        # sale order

        so_line = request.env['sale.order'].sudo().search([
            ('order_line.order_line_state', 'not in', ['cancel', 'return', 'done', 'ready', 'delivering']),
            ('fried_state', 'not in', ['finish', False])], order='date_order ASC')
        for i in so_line:
            order_line = []
            if i.state == 'sale':
                from datetime import timedelta
                from datetime import datetime
                for line in i.order_line.filtered(
                        lambda r: r.order_line_state not in ['cancel', 'return', 'done', 'ready', 'delivering']):
                    if line.product_id.is_fried_product:
                        data = {
                            'full_product_name': line.product_id.name,
                            'id': line.id,
                            'product_uom_qty': line.product_uom_qty,
                            'product_id': line.product_id.id or False
                        }
                        order_line.append(data)
                    if line.product_id.fried_products:
                        if line.fried_ids:
                            pass
                        else:
                            for fp in line.product_id.fried_products:
                                request.env['sale.kitchen.fried.line'].sudo().create({
                                    'product_id': fp.id,
                                    'sale_line_id': line.id
                                })
                        request.env.cr.commit()
                        for fried_id in line.fried_ids:
                            data = {
                                'full_product_name': fried_id.product_id.name,
                                'id': fried_id.id,
                                'product_uom_qty': line.product_uom_qty,
                                'product_name': line.product_id.name,
                                'product_id': line.product_id.id or False
                            }
                            order_line.append(data)
                if len(order_line) >= 1:
                    main_order = {
                        'name': i.name,
                        'type': 'sale',
                        'customer': [i.partner_id.id, i.partner_id.name] or False,
                        'partner_contact': i.partner_id.phone if i.partner_id.phone else False,
                        'order_id': i.id,
                        'pos_reference': i.name,
                        'lines': order_line,
                        'order_status': i.fried_state,
                        'order_time': t2.strftime('%H:%M'),
                        'date_order': i.date_order
                    }
                    so.append(main_order)
        return [pos, so, len(pos), len(so)]

    @route('/upadate/time', type="json", auth="public", cors="*")
    def PollFetchUpdateTime(self, order, inputPin, type, product_info,send_sms,kitchen_screen):
        if type == 'pos':
            pos_order = request.env['pos.order'].sudo().search([('id', '=', order['order_id'])], limit=1)
            product_name = []
            if pos_order:
                if kitchen_screen:
                    pos_order.sudo().write({'kitchen_screen': kitchen_screen})
            for line in pos_order.lines:
                if product_info:
                    for pro in product_info:
                        if int(line.product_id.id) == int(pro):
                            line.sudo().write({
                                'preparation_time': inputPin
                            })
                            val = {
                                'pos_id': pos_order.id,
                                'product_id': line.product_id.id,
                                'order_line_state': line.order_line_state,
                                'preparation_time': line.preparation_time,
                            }
                            exist = pos_order.rel_ids.sudo().search(
                                [('pos_id', '=', pos_order.id), ('product_id', '=', line.product_id.id)], limit=1)

                            if exist:
                                exist.write(val)
                            else:
                                request.env['pos.rel'].sudo().create(val)
                            product_name.append(line.product_id.name)
            if len(product_name)>0:
                product_name_whole = ','.join(product_name)
                if pos_order.partner_id and pos_order.partner_id.phone  and send_sms:
                    self.send_sms_time_updation(pos_order.partner_id.name,inputPin,pos_order.partner_id.phone,product_name_whole)
                if pos_order.partner_id:
                    self.send_email_time_updation(pos_order.partner_id.name,inputPin,pos_order.partner_id.id,product_name_whole,pos_order)

            # pos_order.sudo().write({
            #     'preparation_time': inputPin
            # })
        if type == 'sale':
            product_name = []

            pos_order = request.env['sale.order'].sudo().search([('id', '=', order['order_id'][0])], limit=1)
            if pos_order:
                if kitchen_screen:
                    pos_order.sudo().write({'kitchen_screen': kitchen_screen})
            for line in pos_order.order_line:
                if product_info:
                    for pro in product_info:
                        if int(line.product_id.id) == int(pro):
                            line.sudo().write({
                                'preparation_time': inputPin
                            })
                            product_name.append(line.product_id.name)

            if len(product_name)>0:
                product_name_whole = ','.join(product_name)
                if pos_order.partner_id and pos_order.partner_id.phone  and send_sms:
                    self.send_sms_time_updation(pos_order.partner_id.name,inputPin,pos_order.partner_id.phone,product_name_whole)
                if pos_order.partner_id:
                    self.send_email_time_updation(pos_order.partner_id.name,inputPin,pos_order.partner_id.id,product_name_whole,pos_order)
        return True

    def send_email_time_updation(self,partner_name,inputPin,partner_id,product_name_whole,pos_order):
        # try:
            from datetime import datetime
            pickup_date = pos_order.preparation_time
            company = request.env.user.company_id
            message_body = "Hi " + str(partner_name) + ", your order Cooking time is changed to " + str(pickup_date) + " minutes " + "."
            mail = request.env['mail.mail'].sudo().create({
                'subject': _('Delivery Time Changed'),
                'email_from': company.catchall_formatted or company.email_formatted,
                'recipient_ids': [(4, partner_id)],
                'body_html': message_body,
            })
            mail.send()
        # except:
        #     pass

    def send_sms_time_updation(self,partner_name,inputPin, phone, product_name_whole):
        try:
            message = request.env['pos.order'].sudo().send_message_time_updation(partner_name,inputPin,phone, product_name_whole)
        except:
            pass

    @route('/upadate/start', type="json", auth="public", cors="*")
    def PollFetchUpdatestart(self, order, type, product_info):

        from datetime import datetime
        if type == 'pos':
            pos_order = request.env['pos.order'].sudo().search([('id', '=', order['order_id'])], limit=1)
            if not pos_order.start_order_time:
                pos_order.sudo().write({'start_order_time': datetime.now()})
            for line in pos_order.lines:
                if product_info:
                    for pro in product_info:
                        if int(line.product_id.id) == int(pro):
                            line.sudo().write({
                                'order_line_state': "preparing",
                                'preparation_date': fields.Datetime.now()
                            })
                            val = {
                                'pos_id': pos_order.id,
                                'product_id': line.product_id.id,
                                'order_line_state': line.order_line_state,
                                'preparation_date': line.preparation_date,
                            }
                            exist = pos_order.rel_ids.sudo().search(
                                [('pos_id', '=', pos_order.id), ('product_id', '=', line.product_id.id)], limit=1)
                            if exist:
                                exist.write(val)
                            else:
                                request.env['pos.rel'].sudo().create(val)
            pos_order.sudo().write({
                'preparation_date': fields.Datetime.now()
            })
        if type == 'sale':
            sale_order = request.env['sale.order'].sudo().search([('id', '=', order['order_id'][0])], limit=1)
            if not sale_order.start_order_time:
                sale_order.sudo().write({'start_order_time': datetime.now()})

            for sline in sale_order.order_line:
                if product_info:
                    for pro in product_info:
                        if int(sline.product_id.id) == int(pro):
                            sline.sudo().write({
                                'order_line_state': "preparing",
                                'preparation_date': fields.Datetime.now()
                            })
                # for sline in sale_order.order_line:
                if sline.is_delivery:
                    sline.sudo().write({
                        'order_line_state': "preparing",
                        'preparation_date': fields.Datetime.now()
                    })

            sale_order.sudo().write({
                'preparation_date': fields.Datetime.now()
            })
        return True

    @route('/upadate/start/uhc', type="json", auth="public", cors="*")
    def UpdatestartUhc(self, order, type, product_info):
        product_info = list(set(product_info))
        if type == 'pos':
            pos_order = request.env['pos.order'].sudo().search([('id', '=', order['order_id'])], limit=1)
            for line in pos_order.lines:
                if product_info:
                    for pro in product_info:
                        if int(line.product_id.id) == int(pro):
                            line.sudo().write({
                                'uhc_state': "start",
                            })
        if type == 'sale':
            sale_order = request.env['sale.order'].sudo().search([('id', '=', order['order_id'][0])], limit=1)
            for sline in sale_order.order_line:
                if product_info:
                    for pro in product_info:
                        if int(sline.product_id.id) == int(pro):
                            sline.sudo().write({
                                'uhc_state': "start",
                                # 'preparation_date': fields.Datetime.now()
                            })
                # for sline in sale_order.order_line:
                if sline.is_delivery:
                    sline.sudo().write({
                        'uhc_state': "start"
                    })


        return True

    @route('/update/done/fried', type="json", auth="public", cors="*")
    def update_done_fried(self, order, type, product_info):
        product_info = map(int, product_info)
        product_info = list(set(product_info))
        print("shek mone>>>>>>>>>>>>>>>>>>>>>>")
        if type == 'pos':
            print("shek mone pos>>>>>>>>>>>>>>>>>>>>>>")
            pos_order = request.env['pos.order'].sudo().search([('id', '=', order['order_id'])], limit=1)
            if pos_order:
                pos_order.write({'fried_state': 'done'})

        if type == 'sale':
            print("shek mone sale>>>>>>>>>>>>>>>>>>>>>>")
            sale_order = request.env['sale.order'].sudo().search([('id', '=', order['order_id'])], limit=1)
            if sale_order:
                sale_order.write({'fried_state': 'done'})
        return True

    @route('/update/finish/fried', type="json", auth="public", cors="*")
    def update_finish_fried(self, order, type, product_info):
        product_info = map(int, product_info)
        product_info = list(set(product_info))
        if type == 'pos':
            pos_order = request.env['pos.order'].sudo().search([('id', '=', order['order_id'])], limit=1)
            if pos_order:
                pos_order.write({'fried_state': 'finish'})

        if type == 'sale':
            sale_order = request.env['sale.order'].sudo().search([('id', '=', order['order_id'])], limit=1)
            if sale_order:
                sale_order.write({'fried_state': 'finish'})
        return True


    @route('/upadate/finish/uhc', type="json", auth="public", cors="*")
    def UpdatefinishUhc(self, order, type, product_info, send_sms):
        product_info = map(int, product_info)
        product_info = list(set(product_info))
        if type == 'pos':
            pos_order = request.env['pos.order'].sudo().search([('id', '=', order['order_id'])], limit=1)
            order_line_filter = pos_order.lines.filtered(lambda r: r.product_id.id in product_info)
            counter_list = {}
            if order_line_filter:
                for line in order_line_filter:
                    if line.product_id:
                        line.sudo().write({
                            'uhc_state': "finish"
                        })

        if type == 'sale':
            sale_order = request.env['sale.order'].sudo().search([('id', '=', order['order_id'][0])], limit=1)
            order_line_filter = sale_order.order_line.filtered(lambda r: r.product_id.id in product_info)
            counter_list = {}
            for sline in order_line_filter:
                sline.sudo().write({
                    'uhc_state': "finish",

                })
                if sline.is_delivery:
                    sline.sudo().write({
                        'uhc_state': "finish"
                    })
        return True

    @route('/upadate/finish', type="json", auth="public", cors="*")
    def PollFetchUpdatefinish(self, order, type, product_info, send_sms):
        product_info = map(int, product_info)
        product_info = list(product_info)
        categories_id = request.env.user.pos_category_ids.ids

        from datetime import datetime
        if type == 'pos':
            pos_order = request.env['pos.order'].sudo().search([('id', '=', order['order_id'])], limit=1)
            pos_order.sudo().write({'finish_order_time': datetime.now()})
            order_line_filter = pos_order.lines.filtered(lambda r: r.product_id.id in product_info and int(r.pos_categ_id) in categories_id and r.pos_categ_id != False)
            product_name = []
            if order_line_filter:
                for line in order_line_filter:
                    if line.product_id:
                        line.sudo().write({
                            'order_line_state': "ready"
                        })
                        val = {
                            'pos_id': pos_order.id,
                            'product_id': line.product_id.id,
                            'order_line_state': line.order_line_state,
                        }
                        exist = pos_order.rel_ids.sudo().search(
                            [('pos_id', '=', pos_order.id), ('product_id', '=', line.product_id.id)], limit=1)
                        if exist:
                            exist.write(val)
                        else:
                            request.env['pos.rel'].sudo().create(val)
                        if not line.product_id.is_optional_product:
                            product_name.append(line.product_id.name)

                if pos_order.partner_id and len(product_name)>0:
                    self.send_prepared_notification(product_name, pos_order.partner_id.name, pos_order.partner_id.id,pos_order.partner_id.phone, pos_order.partner_id.email, send_sms)

        if type == 'sale':
            sale_order = request.env['sale.order'].sudo().search([('id', '=', order['order_id'][0])], limit=1)
            sale_order.sudo().write({'finish_order_time': datetime.now()})
            order_line_filter = sale_order.order_line.filtered(lambda r: r.product_id.id in product_info and int(r.pos_categ_id) in categories_id and r.pos_categ_id != False)
            product_name = []
            for sline in order_line_filter:
                sline.sudo().write({
                    'order_line_state': "ready",

                })
                if sline.is_delivery:
                    sline.sudo().write({
                        'order_line_state': "ready",
                        'preparation_date': fields.Datetime.now()
                    })
                if not sline.product_id.is_optional_product:
                    product_name.append(sline.product_id.name)
            if sale_order.partner_id and len(product_name)>0:
                self.send_prepared_notification(product_name, sale_order.partner_id.name, sale_order.partner_id.id,sale_order.partner_id.phone, sale_order.partner_id.email, send_sms)
            if sale_order.merge_order:
                child_orders = request.env['sale.order'].sudo().search([('parent_id','=',sale_order.id)])
                if child_orders:
                    for c_orders in child_orders:
                        c_orders.sudo().write({'finish_order_time': datetime.now()})
                        order_line_filter = c_orders.order_line.filtered(lambda r: r.product_id.id in product_info and int(r.pos_categ_id) in categories_id and r.pos_categ_id != False)
                        product_name = []
                        for sline in order_line_filter:
                            sline.sudo().write({
                                'order_line_state': "ready",
                            })
                            if sline.is_delivery:
                                sline.sudo().write({
                                    'order_line_state': "ready",
                                    'preparation_date': fields.Datetime.now()
                                })
                            if not sline.product_id.is_optional_product:
                                product_name.append(sline.product_id.name)
                        if c_orders.partner_id and len(product_name) > 0:
                            self.send_prepared_notification(product_name, c_orders.partner_id.name,
                                                            c_orders.partner_id.id, c_orders.partner_id.phone,
                                                            c_orders.partner_id.email, send_sms)

        return True

    def send_prepared_notification(self, product_name, partner_id_name, partner_id, phone, email, send_sms):
        product = ','.join(product_name)
        if send_sms:
            try:
                message = request.env['pos.order'].sudo().send_prepared_messages(partner_id_name,phone,product)
            except:
                pass

        # company = request.env.user.company_id
        # # message_body = "Hi " + str(
        # #     partner_id_name) + ",your order  [" + product + "] is prepared"
        # detail = {'partner_id_name':partner_id_name,'product':product}
        # mail = request.env['mail.mail'].sudo().create({
        #     'subject': _('Order Is Prepared'),
        #     'email_from': company.catchall_formatted or company.email_formatted,
        #     'recipient_ids': [(4, partner_id)],
        #     'body_html': order_template.prepared().format(**detail),
        # })
        # mail.send()

    def send_messages_and_mail(self, counter_list, partner_id_name, partner_id, phone, email, send_sms):
        for counter in counter_list.keys():
            product = ','.join(counter_list[counter])
            if send_sms:
                self.send_message_via_phone(product, phone, partner_id_name, counter)
            # self.send_email(counter_list, partner_id_name, partner_id, email, counter, product)

    def send_email(self, counter_list, partner_id_name, partner_id, email, counter, product):
        company = request.env.user.company_id
        message_body = "Hi " + str(
            partner_id_name) + ",your order [" + product + "] is ready to deliver ,Please collect from " + str(counter)
        mail = request.env['mail.mail'].sudo().create({
            'subject': _('Out for Delivery'),
            'email_from': company.catchall_formatted or company.email_formatted,
            'recipient_ids': [(4, partner_id)],
            'body_html': order_template.out_for_deliver().format(partner_id_name=partner_id_name,order_name=product,counter=counter),
        })
        mail.send()

    def send_message_via_phone(self, product, phone, partner_id_name, counter):
        try:
            message = request.env['pos.order'].sudo().send_messages(phone, counter, partner_id_name)
        except:
            pass

    @route('/upadate/delivery', type="json", auth="public", cors="*")
    def PollFetchUpdatedelivery(self, order, type, product_info,send_sms):
        from datetime import datetime
        if type == 'pos':
            pos_order = request.env['pos.order'].sudo().search([('id', '=', order['order_id'])], limit=1)
            pos_order.sudo().write({'delivery_order_time': datetime.now()})
            counter_list = {}

            for line in pos_order.lines:
                if product_info:
                    for pro in product_info:
                        if int(line.product_id.id) == int(pro):
                            line.sudo().write({
                                'order_line_state': "delivering"
                            })
                            val = {
                                'pos_id': pos_order.id,
                                'product_id': line.product_id.id,
                                'order_line_state': line.order_line_state,
                            }
                            exist = pos_order.rel_ids.sudo().search(
                                [('pos_id', '=', pos_order.id), ('product_id', '=', line.product_id.id)], limit=1)
                            if exist:
                                exist.write(val)
                            else:
                                request.env['pos.rel'].sudo().create(val)

                            for ecateg in line.product_id.public_categ_ids:
                                if ecateg.counters:
                                    if ecateg.counters.name in counter_list.keys():
                                        counter_list_value = counter_list.get(ecateg.counters.name)
                                        counter_list_value.append(line.product_id.name)
                                        counter_list[ecateg.counters.name] = counter_list_value
                                        break
                                    else:
                                        counter_list_value = []
                                        counter_list_value.append(line.product_id.name)
                                        counter_list[ecateg.counters.name] = counter_list_value
                                        break
            if pos_order.partner_id:
                self.send_messages_and_mail(counter_list, pos_order.partner_id.name, pos_order.partner_id.id,
                                            pos_order.partner_id.phone, pos_order.partner_id.email, send_sms)


        if type == 'sale':
            sale_order = request.env['sale.order'].sudo().search([('id', '=', order['order_id'][0])], limit=1)
            sale_order.sudo().write({'delivery_order_time': datetime.now()})
            counter_list = {}
            for sline in sale_order.order_line:
                if product_info:
                    for pro in product_info:
                        if int(sline.product_id.id) == int(pro):
                            sline.sudo().write({
                                'order_line_state': "delivering",

                            })
                            for ecateg in sline.product_id.public_categ_ids:
                                if ecateg.counters:
                                    if ecateg.counters.name in counter_list.keys():
                                        counter_list_value = counter_list.get(ecateg.counters.name)
                                        counter_list_value.append(sline.product_id.name)
                                        counter_list[ecateg.counters.name] = counter_list_value
                                        break
                                    else:
                                        counter_list_value = []
                                        counter_list_value.append(sline.product_id.name)
                                        counter_list[ecateg.counters.name] = counter_list_value
                                        break
            if sale_order.partner_id:
                if sale_order.website_delivery_type not  in ['delivery','curb']:
                    self.send_messages_and_mail(counter_list, sale_order.partner_id.name, sale_order.partner_id.id,
                                                sale_order.partner_id.phone, sale_order.partner_id.email, send_sms)
                else:
                    self.send_mail_message_for_in_hotel(sale_order.name,sale_order.partner_id.name,sale_order.partner_id.id,sale_order.partner_id.phone, sale_order.partner_id.email, send_sms)


            if sale_order.merge_order:
                child_orders = request.env['sale.order'].sudo().search([('parent_id','=',sale_order.id)])
                if child_orders:
                    for c_orders in child_orders:
                        c_orders.sudo().write({'delivery_order_time': datetime.now()})
                        counter_list = {}
                        for sline in c_orders.order_line:
                            if product_info:
                                for pro in product_info:
                                    if int(sline.product_id.id) == int(pro):
                                        sline.sudo().write({
                                            'order_line_state': "delivering",

                                        })
                                        for ecateg in sline.product_id.public_categ_ids:
                                            if ecateg.counters:
                                                if ecateg.counters.name in counter_list.keys():
                                                    counter_list_value = counter_list.get(ecateg.counters.name)
                                                    counter_list_value.append(sline.product_id.name)
                                                    counter_list[ecateg.counters.name] = counter_list_value
                                                    break
                                                else:
                                                    counter_list_value = []
                                                    counter_list_value.append(sline.product_id.name)
                                                    counter_list[ecateg.counters.name] = counter_list_value
                                                    break
                        if c_orders.partner_id:
                            if c_orders.website_delivery_type not in ['delivery', 'curb']:
                                self.send_messages_and_mail(counter_list, c_orders.partner_id.name,
                                                            c_orders.partner_id.id,
                                                            c_orders.partner_id.phone, c_orders.partner_id.email,
                                                            send_sms)
                            else:
                                self.send_mail_message_for_in_hotel(c_orders.name, c_orders.partner_id.name,
                                                                    c_orders.partner_id.id,
                                                                    c_orders.partner_id.phone,
                                                                    c_orders.partner_id.email, send_sms)

        return True

    def send_mail_message_for_in_hotel(self,order_name,name,partner_id,phone,email,send_sms):
        company = request.env.user.company_id
        # message_body = "Hi " + str(
        #     name) + ",your order [" + order_name + "] is ready to deliver."
        # mail = request.env['mail.mail'].sudo().create({
        #     'subject': _('Out for Delivery'),
        #     'email_from': company.catchall_formatted or company.email_formatted,
        #     'recipient_ids': [(4, partner_id)],
        #     'body_html': order_template.prepared().format(partner_id_name=name,order_name=order_name)
        # })
        # mail.send()
        if send_sms:

            try:
                message = request.env['pos.order'].sudo().send_message_for_in_hotel(order_name,name,phone)
            except:
                pass

    @route('/upadate/done', type="json", auth="public", cors="*")
    def PollFetchUpdatedeliverydone(self, order, type, product_info):
        from datetime import datetime
        if type == 'pos':
            recall = request.env['recall.order'].sudo().search(
                [('type', '=', 'pos'), ('order_id', '=', order['order_id'])], limit=1)
            if recall:
                recall.sudo().unlink()

            recall_order = request.env['recall.order'].sudo().search_count([]) or 0
            if recall_order<11:
                request.env['recall.order'].sudo().create({'order_id': order['order_id'],'type':'pos'})
            else:
                recall_order_all = request.env['recall.order'].sudo().search([],order='create_date ASC', limit=1)
                if recall_order_all:
                    recall_order_all.sudo().unlink()
                request.env['recall.order'].sudo().create({'order_id': order['order_id'], 'type': 'pos'})

            pos_order = request.env['pos.order'].sudo().search([('id', '=', order['order_id'])], limit=1)
            if pos_order.recall_order:
                pos_order.sudo().write({'done_order_time': datetime.now(),'recall_order':False})
            else:
                pos_order.sudo().write({'done_order_time': datetime.now()})

            for line in pos_order.lines:
                if product_info:
                    for pro in product_info:
                        if int(line.product_id.id) == int(pro):
                            line.sudo().write({
                                'order_line_state': "done"
                            })
                            val = {
                                'pos_id': pos_order.id,
                                'product_id': line.product_id.id,
                                'order_line_state': line.order_line_state,
                            }
                            exist = pos_order.rel_ids.sudo().search(
                                [('pos_id', '=', pos_order.id), ('product_id', '=', line.product_id.id)], limit=1)
                            if exist:
                                exist.write(val)
                            else:
                                request.env['pos.rel'].sudo().create(val)

        if type == 'sale':
            try:
                recall = request.env['recall.order'].sudo().search(
                    [('type', '=', 'sale'), ('order_id', '=', order['order_id'][0])], limit=1)
                if recall:
                    recall.sudo().unlink()
                recall_order = request.env['recall.order'].sudo().search_count([]) or 0
                if recall_order<11:
                    request.env['recall.order'].sudo().create({'order_id': order['order_id'][0],'type':'sale'})
                else:
                    recall_order_all = request.env['recall.order'].sudo().search([],order='create_date ASC', limit=1)
                    if recall_order_all:
                        recall_order_all.sudo().unlink()
                    request.env['recall.order'].sudo().create({'order_id': order['order_id'][0], 'type': 'sale'})
            except:
                pass
            sale_order = request.env['sale.order'].sudo().search([('id', '=', order['order_id'][0])], limit=1)


            if sale_order.recall_order:
                sale_order.sudo().write({'done_order_time': datetime.now(), 'recall_order': False})
            else:
                sale_order.sudo().write({'done_order_time': datetime.now()})

            for sline in sale_order.order_line:
                if product_info:
                    for pro in product_info:
                        if int(sline.product_id.id) == int(pro):
                            sline.sudo().write({
                                'order_line_state': "done",

                            })

            if sale_order.merge_order:
                child_orders = request.env['sale.order'].sudo().search([('parent_id','=',sale_order.id)])
                if child_orders:
                    for c_orders in child_orders:
                        c_orders.sudo().write({'done_order_time': datetime.now()})
                        for sline in c_orders.order_line:
                            if product_info:
                                for pro in product_info:
                                    if int(sline.product_id.id) == int(pro):
                                        sline.sudo().write({
                                            'order_line_state': "done",

                                        })
        return True

    @route('/recall/order/kitchen', type="json", auth="public", cors="*")
    def RecallOrder(self):

        pos = request.env['pos.order'].sudo().search_count([('recall_order','=',True)]) or 0
        sale = request.env['sale.order'].sudo().search_count([('recall_order','=',True)]) or 0
        if pos+sale==10:
            return {'status': 'fail'}
        else:
            recall_order = request.env['recall.order'].sudo().search([('recall_order', '=', False)], order='create_date DESC',limit=1)
            if recall_order:
                recall_order.recall_order = True

                if recall_order.type == 'pos':
                    pos_order = request.env['pos.order'].sudo().search([('id', '=', recall_order.order_id)], limit=1)
                    pos_order.recall_order = True
                    for line in pos_order.lines:
                        line.order_line_state = 'preparing'

                else:
                    sale_order = request.env['sale.order'].sudo().search([('id', '=', recall_order.order_id)], limit=1)
                    sale_order.recall_order = True
                    for line in sale_order.order_line:
                        line.order_line_state = 'preparing'
                return {'status': 'success'}
            else:
                return {'status': 'no_order'}

    @route('/upadate/timeout', type="json", auth="public", cors="*")
    def PollFetchUpdatetimeouts(self, order ,type):
        if type == 'pos':
            pos_order = request.env['pos.order'].sudo().search([('id', '=', order)], limit=1)
            pos_order.sudo().write({
                'kitchen_screen': False
            })

        if type == 'sale':
            sale_order = request.env['sale.order'].sudo().search([('id', '=', order)], limit=1)
            sale_order.sudo().write({
                'kitchen_screen': False
            })

        return True

    @route('/order/print', type="json", auth="public", cors="*")
    def PrintOrder(self, order, print_session, order_type):
        try:
            pos_printed = True
            sale_printed = True
            if order_type == 'pos':
                pos_order = request.env['pos.order'].sudo().search([('id', '=', order)], limit=1)
                for i in pos_order.is_printed:
                    if i.session.id == print_session:
                        print(i)
                        pos_printed = False
                        break
                if pos_printed:
                    pos_order.sudo().write({'is_printed': [(0, 0, {
                        'pos_receipt_id': pos_order.id,
                        'session': int(print_session)
                    })]})
                    pos_printed = True
            elif order_type == 'sale':
                sale_order = request.env['sale.order'].sudo().search([('id', '=', order)], limit=1)
                for i in sale_order.is_printed:
                    if i.session.id == print_session:
                        sale_printed = False
                        break
                if sale_printed:
                    sale_order.sudo().write({'is_printed': [(0, 0, {
                        'sale_receipt_id': sale_order.id,
                        'session': int(print_session)
                    })]})
                    sale_printed = True
            else:
                printed = False
            # print(sale_printed)
            # print(pos_printed)
            if sale_printed or pos_printed:
                return True
            else:
                return False
        except:
            return False

    @route('/upadate/message', type="json", auth="public", cors="*")
    def SendMeaageToKitchen(self, inputPin, session_id):
        uid = request.session.uid,
        if inputPin['session'] and inputPin['inputValue']:
            message = request.env['message.kitchen']
            user = request.env['res.users'].sudo().search([('id', '=', uid)], limit=1).name
            if inputPin['session'] == 'all':
                sessions = request.env['pos.session'].sudo().search(
                    [('state', 'in', ['opening_control', 'opened']), ('rescue', '=', False),
                     ('id', '!=', int(session_id))])
                for session in sessions:
                    message.sudo().create({
                        'message': inputPin['inputValue'],
                        'user_name': user or False,
                        'pos_session': session.id or False
                    })
            else:
                message.sudo().create({
                    'message': inputPin['inputValue'],
                    'user_name': user or False,
                    'pos_session': inputPin['session'] or False
                })
        return True


    @route('/google/search', type="json", auth="public", cors="*")
    def SearchGooglevia(self, tag):
        if tag:
            try:
                import googlesearch
                d = googlesearch.search(tag, num_results=10, lang="en")
                import re
                from bs4 import BeautifulSoup
                import requests
                find_link = False
                filter1 = re.compile("https://en.wikipedia.org")
                for line in d:
                    if filter1.match(line):
                        find_link = line
                r = requests.get(find_link)
                soup = BeautifulSoup(r.content, 'html5lib')
                table = soup.find('div', attrs={'class': 'mw-parser-output'})
                count = 0
                list = []
                for row in table.findAll('p'):
                    list.append(row)

                data = str(list[1])
                p = re.compile(r'<.*?>')
                a = p.sub('', data)
                if a:
                    return a
                else:
                    return False
            except:
                return False
        else:
            return False

    @route('/upadate/pos/mark', type="json", auth="public", cors="*")
    def UpdatePosMark(self, pro_line):
        uid = request.session.uid,
        pline = request.env['pos.order.line'].sudo().search([('id','=',pro_line)])
        if pline:
                pline.write({
                    'order_line_mark': True,
                })
        return True

    @route('/upadate/pos/unmark', type="json", auth="public", cors="*")
    def UpdatePosUnMark(self, pro_line):
        uid = request.session.uid,
        pline = request.env['pos.order.line'].sudo().search([('id','=',pro_line)])
        if pline:
                pline.write({
                    'order_line_mark': False,
                })
        return True

    @route('/upadate/sale/mark', type="json", auth="public", cors="*")
    def UpdateSaleMark(self, pro_line):
        uid = request.session.uid,
        pline = request.env['sale.order.line'].sudo().search([('id', '=', pro_line)])
        if pline:
            pline.write({
                'order_line_mark': True,
            })
        return True

    @route('/upadate/sale/unmark', type="json", auth="public", cors="*")
    def UpdateSaleUnMark(self, pro_line):
        uid = request.session.uid,
        pline = request.env['sale.order.line'].sudo().search([('id', '=', pro_line)])
        if pline:
            pline.write({
                'order_line_mark': False,
            })
        return True

    @route('/upadate/order/position', type="json", auth="public", cors="*")
    def UpdatePosPosition(self, order_id,position,type,move_to,all_order_new):
        uid = request.session.uid,
        sale = [i for i in all_order_new if i['type']=='sale'] or False
        pos =[i for i in all_order_new if i['type']=='pos'] or False
        if sale:
            ids = [i.get('id')[0] for i in sale]
            order_all= request.env['sale.order'].sudo().search([('id','in',ids)])

            for seq in sale:
                order = order_all.filtered(lambda r: r.id == seq['id'][0])
                if order:
                    order.write({'order_sequence': seq['sequence']})
        if pos:
            ids = [i.get('id') for i in pos]
            order_all = request.env['pos.order'].sudo().search([('id', 'in', ids)])
            if order_all:
                for seq in pos:
                    order = order_all.filtered(lambda r:r.id==seq['id'])
                    if order:
                        order.write({'order_sequence':seq['sequence']})


        return True

    def action_preorder(self, i, res_config_settings, tz):
        from datetime import timedelta
        from datetime import datetime
        dine_in_order = False
        min_time = 0
        min_kitchen_display_time = 0
        if i.pickup_date:
            pre_order_kitchen_display = res_config_settings.get_param(
                'website_sale_hour.pre_order_kitchen_display')
            pre_order_time = '{0:02.0f}:{1:02.0f}'.format(
                *divmod(float(pre_order_kitchen_display) * 60, 60))
            kitchen_pre_order_time = datetime.strptime(pre_order_time, '%H:%M').time()
            tot_secs = (kitchen_pre_order_time.hour * 60 + kitchen_pre_order_time.minute) \
                       * 60 + kitchen_pre_order_time.second
            min_kitchen_display_time = tot_secs / 60
            current_date_time = datetime.now(tz).astimezone(tz)
            time_now1 = current_date_time.replace(microsecond=0)
            time_now = time_now1.replace(tzinfo=None)
            now = datetime.utcnow()
            utc = pytz.timezone('UTC')
            utc.localize(datetime.now())
            delta = utc.localize(now) - tz.localize(now)
            sec = delta.seconds
            total_minute = sec / 60
            order_time = i.date_order + timedelta(minutes=total_minute)
            time_difference = time_now - order_time
            sec_time = time_difference.total_seconds()
            min_time = sec_time / 60
        elif i.website_delivery_type == 'dine_in':
            from datetime import timedelta
            from datetime import datetime
            res_config_settings = request.env['ir.config_parameter'].sudo()
            pos_order_kitchen_display = res_config_settings.get_param(
                'website_sale_hour.pos_order_kitchen_display')
            pos_order_time = '{0:02.0f}:{1:02.0f}'.format(
                *divmod(float(pos_order_kitchen_display) * 60, 60))
            pos_kitchen_pre_order_time = datetime.strptime(pos_order_time, '%H:%M').time()
            pos_tot_secs = (pos_kitchen_pre_order_time.hour * 60 + pos_kitchen_pre_order_time.minute)\
                           * 60 + pos_kitchen_pre_order_time.second
            min_kitchen_display_time = pos_tot_secs / 60

            current_date_time = datetime.now(tz).astimezone(tz)
            time_now1 = current_date_time.replace(microsecond=0)
            time_now = time_now1.replace(tzinfo=None)
            now = datetime.utcnow()
            utc = pytz.timezone('UTC')
            utc.localize(datetime.now())
            delta = utc.localize(now) - tz.localize(now)
            sec = delta.seconds
            total_minute = sec / 60
            order_time = i.date_order + timedelta(minutes=total_minute)
            time_difference = time_now - order_time
            sec_time = time_difference.total_seconds()
            min_time = sec_time / 60
            dine_in_order = True
        return min_time, min_kitchen_display_time
