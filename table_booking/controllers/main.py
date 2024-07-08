# -*- coding: utf-8 -*-
import json
import logging
import datetime as Datetime
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request


class WebsiteBooking(http.Controller):

    @http.route('/booking', website=True, auth='public')
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']

        values = {
            'category': Category,
        }
        return request.render("table_booking.booking_template", values)

    @http.route('/get/table/booking', csrf=False, type='json', auth="public")
    def TableBookingTime(self, **kw):
        select_person = kw.get('select_person')
        booking_date = kw.get('booking_date').replace('-', '/')
        select_time = kw.get('select_time')
        current = request.env.company
        tz = pytz.timezone(current.tz)
        now = datetime.utcnow()
        utc = timezone('UTC')
        utc.localize(datetime.now())
        delta = utc.localize(now) - tz.localize(now)
        sec = delta.seconds
        total_minute = sec / 60
        res_config_settings = request.env['ir.config_parameter'].sudo()
        reservation_time = res_config_settings.get_param('website_reservation.reservation_time')

        booking_date = datetime.strptime(booking_date, '%Y/%m/%d').date()

        time_val = datetime.strptime(select_time, '%H:%M').time()
        start_time = datetime.combine(booking_date, time_val)
        end_time = start_time + relativedelta(minutes=float(reservation_time))
        all_tables = request.env['website.reservation.line'].sudo().search([])

        table = all_tables.filtered(lambda r: r.date_reserved_end - relativedelta(
            minutes=total_minute) <= end_time and r.date_reserved - relativedelta(
            minutes=total_minute) >= start_time).mapped('reservation_id.id')

        table_not_selected = request.env['restaurant.table'].sudo().search([('id', 'not in', table)])
        list_of_avialable_table = []
        for rec in table_not_selected:
            list_of_avialable_table.append({'floor': rec.floor_id.name, 'id': rec.floor_id.id,
                                            'table_id': rec.id, 'selected_time': select_time})
        if len(list_of_avialable_table) <= 0:
            return False
        else:
            return list_of_avialable_table

    @http.route('/get/time/booking', csrf=False, type='json', auth="public")
    def BookingTime(self, **kw):

        picking_date = kw.get('picking_date', 'Today')
        current_uid = request.env.user

        tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
        if picking_date == 'Today':
            today = datetime.datetime.now(tz).strftime("%A")
        else:
            date = datetime.strptime(picking_date, '%Y-%m-%d').strftime('%m/%d/%y')
            date = datetime.strptime(date, '%m/%d/%y')
            today = date.astimezone(tz).strftime("%A")
        res_config_settings = request.env['ir.config_parameter'].sudo()
        min_delivery_time = res_config_settings.get_param('website_sale_hour.pickup_time')
        minutes = float(min_delivery_time) * 60
        time = datetime.now(tz)

        from_time_1 = ''
        from_time_2 = ''
        if today == 'Sunday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_sunday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_sunday')
        elif today == 'Monday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_monday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_monday')
        elif today == 'Tuesday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_tuesday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_tuesday')
        elif today == 'Wednesday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_wednesday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_wednesday')
        elif today == 'Thursday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_thursday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_thursday')
        elif today == 'Friday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_friday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_friday')
        elif today == 'Saturday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_saturday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_saturday')

        time_from1 = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_1) * 60, 60))
        time_from2 = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_2) * 60, 60))

        pickup_date_val = time + Datetime.timedelta(minutes=minutes)

        time_now = pickup_date_val.time().strftime('%H:%M')
        if picking_date == 'Today':
            picking_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')
        else:
            picking_date = datetime.strptime(picking_date, '%Y-%m-%d')

        return {'time_now': time_now, 'picking_date': picking_date.date(),
                'after_date': pickup_date_val.date().strftime('%Y-%m-%d'),
                'today_date': datetime.now(tz).date().strftime('%Y-%m-%d'), "from_time_1": time_from1,
                'from_time_2': time_from2}

    @http.route('/create/user', csrf=False, type='json', auth="public")
    def CreateUser(self, **kw):
        first_name = kw.get('first_name')
        last_name = kw.get('last_name')
        phone = kw.get('phone')
        email = kw.get('email')
        floor_id = kw.get('floor_id')
        table_id = kw.get('table_id')
        select_person = kw.get('select_person')
        selected_time = kw.get('selected_time')
        booking_date = kw.get('booking_date').replace('-', '/')
        special_request = kw.get('request')
        occasion = kw.get('occasion')
        occasion_val = False
        if occasion in ['birthday', 'date', 'business', 'special']:
            occasion_val = occasion
        current = request.env.company
        tz = pytz.timezone(current.tz)

        booking_date = datetime.strptime(booking_date, '%Y/%m/%d').date()

        res_config_settings = request.env['ir.config_parameter'].sudo()
        reservation_time = res_config_settings.get_param('website_reservation.reservation_time')
        time_val = datetime.strptime(selected_time, '%H:%M').time()
        start_time = datetime.combine(booking_date, time_val).astimezone(tz).replace(tzinfo=None)
        end_time = start_time + Datetime.timedelta(hours=00, minutes=float(reservation_time))
        end_time = end_time.replace(tzinfo=None)

        old_user = request.env['res.users'].sudo().search([('login', '=', str(email))])
        if old_user:
            new_partner1 = request.env['res.partner'].sudo().search([('id', '=', old_user.partner_id.id)])
            new_partner1.sudo().write({'phone': phone, 'email': str(email)})
            country = request.env['res.country'].sudo().search([('code', '=', 'AU')], limit=1).id
            state_id = request.env['res.country.state'].sudo().search([('code', '=', 'QLD')], limit=1).id

            val = {
                'company_type': 'person',
                'parent_id': new_partner1.id,
                'type': 'delivery',
                'name': str(first_name + ' ' + last_name),
                'phone': int(phone),
                'email': str(email)
            }
            child = request.env['res.partner'].sudo().create(val)
            floor_id = request.env['restaurant.floor'].sudo().search([('id', '=', floor_id)], limit=1)
            if floor_id:
                table = floor_id.table_ids
                if table:
                    request.env['website.reservation.line'].sudo().create(
                        {'reservation_id': int(table_id), 'partner_id': child.id,
                         'no_of_people': select_person, 'date_reserved': start_time,
                         'date_reserved_end': end_time, 'occasion': occasion_val,
                         'special_request': special_request})
            request.env.cr.commit()
        else:
            val = {
                'name': str(first_name + ' ' + last_name),
                'login': str(email),
                'groups_id': [(4, request.env.ref('base.group_portal').id)]
            }
            user = request.env['res.users']
            new_user = user.sudo().create(val)
            new_user.partner_id.sudo().write({'phone': phone, 'email': str(email)})
            floor_id = request.env['restaurant.floor'].sudo().search([('id', '=', floor_id)], limit=1)
            if floor_id:
                table = floor_id.table_ids
                if table:
                    request.env['website.reservation.line'].sudo().create(
                        {'reservation_id': int(table_id), 'partner_id': new_user.partner_id.id,
                         'no_of_people': select_person, 'date_reserved': start_time,
                         'date_reserved_end': end_time, 'occasion': occasion_val,
                         'special_request': special_request})
        return True
