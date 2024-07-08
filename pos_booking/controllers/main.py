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
from odoo.addons.website_sale.controllers.main import WebsiteSale

# class WebsiteBookingInformation(WebsiteSale):

    # @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    # def checkout(self, **post):
    #     order = request.website.sale_get_order()
    #     if order:
    #
    #     return super(WebsiteBookingInformation, self).checkout(**post)


class PosInheritsBooking(http.Controller):

    @http.route('/get/pos/table/booking', csrf=False, type='json', auth="public")
    def TablePosBookingTime(self, **kw):
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
        start_time = datetime.combine(booking_date, time_val) - Datetime.timedelta(hours=5,minutes=30)
        end_time = start_time + relativedelta(minutes=float(reservation_time))
        all_tables = request.env['website.reservation.line'].sudo().search([('date_reserved_end','>=',start_time),('date_reserved','<=',start_time)])
        table = all_tables.mapped('reservation_id.id')
        # table = all_tables.filtered(lambda r: r.date_reserved_end >= end_time and r.date_reserved <= start_time).mapped('reservation_id.id')

        table_not_selected = request.env['restaurant.table'].sudo().search([('id', 'not in', table)])
        list_of_avialable_table = []
        for rec in table_not_selected:
            list_of_avialable_table.append({'floor': rec.floor_id.name, 'id': rec.floor_id.id,
                                            'table_id': rec.id, 'selected_time': select_time, 'table_name': rec.name})
        if len(list_of_avialable_table) <= 0:
            return False
        else:
            return list_of_avialable_table

    @http.route('/get/pos/table/booking/id', csrf=False, type='json', auth="public")
    def TablePosBookingTimeReservationBck(self, **kw):
    # def get_tables_reservation_availableh(self,booking_selected_table,minimize_booking_gape ):
        """         """
        # self.ensure_one()
        print("\n _____TablePosBookingTimeReservationBck_______\n")
        booking_selected_table = kw.get('booking_selected_table')
        minimize_booking_gape = kw.get('minimize_booking_gape')

        booking_date = kw.get('booking_date').replace('-', '/')
        select_time = kw.get('select_time')

        booking_date = datetime.strptime(booking_date, '%Y/%m/%d').date()

        time_val = datetime.strptime(select_time, '%H:%M').time()
        now = datetime.combine(booking_date, time_val) - Datetime.timedelta(hours=5, minutes=30)

        unavailable_tables_list = []
        soon_unavailable_tables_list = []
        soon_available_tables_list = []
        res_config_settings = request.env['ir.config_parameter'].sudo()
        reservation_time = res_config_settings.get_param('website_reservation.reservation_time')
        current = request.env.company
        tz = pytz.timezone(current.tz)
        time_soon_gap = float(minimize_booking_gape) + float(reservation_time)
        time_ends = now - relativedelta(minutes=float(time_soon_gap))
        if reservation_time and minimize_booking_gape:
            unavailable_tables = request.env['website.reservation.line'].sudo().search([('date_reserved_end','>=',now),('date_reserved','<=',now),('state','!=','cancel')])
            for i in unavailable_tables:
                time_elapse = i.date_reserved - time_ends
                sec = time_elapse.seconds
                total_minute = sec / 60
                if total_minute <= time_soon_gap:
                    dict_rev = {
                        'table_id': i.reservation_id.id,
                        'table_name': i.reservation_id.name,
                        'date_reserved': i.date_reserved.astimezone(tz),
                        'date_reserved_end': i.date_reserved_end.astimezone(tz),
                        'occasion': i.occasion,
                        'special_request': i.special_request,
                        'partner_id': i.partner_id.name,
                        'id': i.id,
                        'state': i.state,
                        'name': i.name,
                    }
                    unavailable_tables_list.append(dict_rev)
            time_soon_gap1 = float(minimize_booking_gape)

            soon_unavailable= request.env['website.reservation.line'].sudo().search([('date_reserved', '>', now),('state','!=','cancel')])
            for i in soon_unavailable:
                time_date_reserved = i.date_reserved-now
                sec1 = time_date_reserved.seconds
                total_minute1 = sec1 / 60
                if total_minute1 < time_soon_gap1 and total_minute1 > 0:
                    dict_rev = {
                        'table_id': i.reservation_id.id,
                        'table_name': i.reservation_id.name,
                        'date_reserved': i.date_reserved.astimezone(tz),
                        'date_reserved_end': i.date_reserved_end.astimezone(tz),
                        'occasion': i.occasion,
                        'special_request': i.special_request,
                        'partner_id': i.partner_id.name,
                        'id': i.id,
                        'state': i.state,
                        'name': i.name,
                    }
                    unavailable_tables_list.append(dict_rev)
        exist = False
        for i in unavailable_tables_list:
            if i['table_id'] == int(booking_selected_table):
                exist = True
        return exist

    @http.route('/get/time/booking1', csrf=False, type='json', auth="public")
    def BookingTime1(self, **kw):

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
        min_delivery_time = 00
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

    @http.route('/get/pos/time/booking', csrf=False, type='json', auth="public")
    def BookingPosTime(self, **kw):

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



    @http.route('/create/pos/user/Booking', csrf=False, type='json', auth="public")
    def CreatePosUser(self, **kw):
        table_booking = request.env['ir.config_parameter'].sudo().get_param('table_booking.table_booking')
        table_booking_product = request.env['ir.config_parameter'].sudo().get_param('table_booking.table_booking_product')
        # order = kw.get('order')
        if table_booking and table_booking_product:
            first_name = kw.get('first_name')
            last_name = kw.get('last_name')
            phone = kw.get('phone')
            email = kw.get('email')
            floor_id = kw.get('floor_id')
            table_id = kw.get('table_id')
            select_person = kw.get('select_person')
            selected_time = kw.get('selected_time')
            booking_date = kw.get('booking_date').replace('-', '/')
            occasion = kw.get('occasion')
            note = kw.get('note')
            merge = kw.get('merge')
            border_color = kw.get('border_color')
            occasion_val = False
            if occasion in ['birthday', 'date', 'business', 'special']:
                occasion_val = occasion
            current = request.env.company
            tz = pytz.timezone(current.tz)

            booking_date = datetime.strptime(booking_date, '%Y/%m/%d').date()
            # booking_date = datetime.strptime(booking_date, '%Y/%m/%d')

            res_config_settings = request.env['ir.config_parameter'].sudo()
            reservation_time = res_config_settings.get_param('website_reservation.reservation_time')
            if selected_time:
                time_val = datetime.strptime(selected_time, '%H:%M').time()
            else:
                selected_time = str(datetime.now().strftime("%H:%M"))
                time_val = datetime.strptime(selected_time, '%H:%M').time()
            start_time = datetime.combine(booking_date, time_val)
            start_time = datetime.combine(booking_date, time_val) - Datetime.timedelta(hours=5,minutes=30)
            end_time = start_time + Datetime.timedelta(hours=00, minutes=float(reservation_time))
            end_time = end_time.replace(tzinfo=None)


            old_user = request.env['res.users'].sudo().search([('login', '=', str(email))])
            if old_user:
                new_partner1 = request.env['res.partner'].sudo().search([('id', '=', old_user.partner_id.id)])
                new_partner1.sudo().write({'phone': phone, 'email': str(email)})
                company = request.env['res.company'].sudo().browse(1)
                val = {
                    'company_type': 'person',
                    'parent_id': new_partner1.id,
                    'type': 'delivery',
                    'name': str(first_name + ' ' + last_name),
                    'phone': str(phone),
                    'email': str(email)
                }
                child = request.env['res.partner'].sudo().create(val)
                request.env.cr.commit()
                child.sudo().write({
                    'country_id': company.country_id,
                    'state_id': company.state_id,
                    'zip': company.zip,
                    'street': company.street,
                    'street2': company.street2,
                    'city': company.city
                })
                floor_id = request.env['restaurant.floor'].sudo().search([('id', '=', int(floor_id))], limit=1)
                if floor_id:
                    table = floor_id.table_ids
                    if table:
                        booking = request.env['website.reservation.line'].sudo().create(
                            {'reservation_id': int(table_id), 'partner_id': child.id,
                             'no_of_people': select_person, 'date_reserved': start_time,
                             'date_reserved_end': end_time, 'occasion': occasion_val,
                             'special_request': note})
                        if merge:
                            booking = request.env['website.reservation.line'].sudo().create(
                                {'reservation_id': int(merge), 'partner_id': child.id,
                                 'no_of_people': select_person, 'date_reserved': start_time,
                                 'date_reserved_end': end_time, 'occasion': occasion_val,
                                 'special_request': note, 'merged_table': int(table_id), 'border_color': border_color})
            else:
                val = {
                    'name': str(first_name + ' ' + last_name),
                    'login': str(email),
                    'groups_id': [(4, request.env.ref('base.group_portal').id)]
                }
                company = request.env['res.company'].sudo().browse(1)
                user = request.env['res.users']
                new_user = user.sudo().create(val)
                request.env.cr.commit()

                new_user.partner_id.sudo().write({'phone': phone, 'email': str(email)})
                new_user.partner_id.sudo().write({
                    'country_id': company.country_id,
                    'state_id': company.state_id,
                    'zip': company.zip,
                    'street': company.street,
                    'street2': company.street2,
                    'city': company.city
                })
                floor_id = request.env['restaurant.floor'].sudo().search([('id', '=', floor_id)], limit=1)
                if floor_id:
                    table = floor_id.table_ids
                    if table:
                        booking = request.env['website.reservation.line'].sudo().create(
                            {'reservation_id': int(table_id), 'partner_id': new_user.partner_id.id,
                             'no_of_people': select_person, 'date_reserved': start_time,
                             'date_reserved_end': end_time, 'occasion': occasion_val,
                             'special_request': note})
                        if merge:
                            booking = request.env['website.reservation.line'].sudo().create(
                                {'reservation_id': int(merge), 'partner_id': new_user.partner_id.id,
                                 'no_of_people': select_person, 'date_reserved': start_time,
                                 'date_reserved_end': end_time, 'occasion': occasion_val,
                                 'special_request': note,'merged_table': int(table_id),'border_color': border_color})
                        # if booking:
                        #     sale_order = request.env['sale.order.line'].sudo().create({
                        #         'order_id': int(order),
                        #         'customer_lead': 1,
                        #         'product_id': int(table_booking_product),
                        #         'product_uom_qty': 1.0,
                        #         'price_unit': 5
                        #     })
                        #     sale_order.order_id.sudo().write({
                        #         'is_table_booked': True,
                        #         'table_booked': booking.id
                        #     });
                        #     sale_order.order_id.onchange_partner_shipping_id()
                        #     sale_order._compute_tax_id()
                        #     sale_order.order_id.sudo().write({'partner_id': new_user.partner_id.id})
                        #     sale_order.order_id.sudo().write({'carrier_id': 1})
                        #     sale_order.order_id.sudo().write({
                        #         'partner_shipping_id': new_user.partner_id.id,
                        #         'partner_invoice_id': new_user.partner_id.id,
                        #         'public_partner': new_user.partner_id.id,
                        #         'carrier_id': 1,
                        #     })
                        #     if sale_order.order_id.sudo().partner_id:
                        #         print("aaaa", sale_order)
            return True

    @http.route('/get/future/booking', csrf=False, type='json', auth="public")
    def FutureBooking(self, **kw):
        rev_list = []
        table = kw.get('table')
        res_config_settings = request.env['ir.config_parameter'].sudo()
        reservation_time = res_config_settings.get_param('website_reservation.reservation_time')
        current = request.env.company
        tz = pytz.timezone(current.tz)
        now = datetime.utcnow()
        utc = timezone('UTC')
        utc.localize(datetime.now())
        delta = utc.localize(now) - tz.localize(now)
        all_tables = request.env['website.reservation.line'].sudo().search([('reservation_id','=',table),('date_reserved','>',now)])
        for i in all_tables:
            rev_list.append({
                'name': i.name,
                'reservation_id': i.reservation_id.id,
                'date_reserved': i.date_reserved.astimezone(tz),
                'date_reserved_end': i.date_reserved_end.astimezone(tz),
                'no_of_people': i.no_of_people,
                'special_request': i.special_request,
                'partner_id': i.partner_id.id,
                'partner_name': i.partner_id.name,
                'occasion': i.occasion,
                'id': i.id,
            })
        return rev_list



        # select_person = kw.get('select_person')
        # booking_date = kw.get('booking_date').replace('-', '/')
        # select_time = kw.get('select_time')
        # current = request.env.company
        # tz = pytz.timezone(current.tz)
        # now = datetime.utcnow()
        # utc = timezone('UTC')
        # utc.localize(datetime.now())
        # delta = utc.localize(now) - tz.localize(now)
        # sec = delta.seconds
        # total_minute = sec / 60
        # res_config_settings = request.env['ir.config_parameter'].sudo()
        # reservation_time = res_config_settings.get_param('website_reservation.reservation_time')
        # booking_date = datetime.strptime(booking_date, '%Y/%m/%d').date()
        # time_val = datetime.strptime(select_time, '%H:%M').time()
        # start_time = datetime.combine(booking_date, time_val) - Datetime.timedelta(hours=5, minutes=30)
        # end_time = start_time + relativedelta(minutes=float(reservation_time))
        # all_tables = request.env['website.reservation.line'].sudo().search([('date_reserved_end', '>=', start_time), ('date_reserved', '<=', start_time)])
        # table = all_tables.mapped('reservation_id.id')
        # # table = all_tables.filtered(lambda r: r.date_reserved_end >= end_time and r.date_reserved <= start_time).mapped('reservation_id.id')
        #
        #
        #
        # table_not_selected = request.env['restaurant.table'].sudo().search([('id', 'not in', table)])
        # list_of_avialable_table = []
        # for rec in table_not_selected:
        #     list_of_avialable_table.append({'floor': rec.floor_id.name, 'id': rec.floor_id.id,
        #                                     'table_id': rec.id, 'selected_time': select_time, 'table_name': rec.name})
        # if len(list_of_avialable_table) <= 0:
        #     return False
        # else:
        #     return list_of_avialable_table

        # return True
    #
    # @http.route('/get/future/booking', csrf=False, type='json', auth="public")
    # def FutureBooking(self, **kw):


    @http.route('/get/update/booking', csrf=False, type='json', auth="public")
    def UpdateBookings(self, **kw):
        # TODO check the party size
        #  if party size greater than table capacity, move the reservation to another table
        #  if no table available with required party size, combine two tables
        #  if no tables available, notify it
        msg = 'Table Edited'
        if kw.get('reservation_id'):
            all_tables = request.env['website.reservation.line'].sudo().search([('id', '=', kw.get('reservation_id'))],limit=1)
            tz = pytz.timezone(all_tables.company_id.tz)
            now = datetime.utcnow()
            utc = timezone('UTC')
            utc.localize(datetime.now())
            delta = utc.localize(now) - tz.localize(now)
            sec = delta.seconds
            total_minute = sec / 60
            from datetime import timedelta

            if kw.get('reservation_start') and kw.get('reservation_ends') and kw.get('occasion') and all_tables:
                if len(kw.get('reservation_start'))<=16:
                    time_start = datetime.strptime(kw.get('reservation_start').replace('T', ' '),'%Y-%m-%d %H:%M') - timedelta(hours=0, minutes=total_minute)
                    all_tables.sudo().write({
                        'date_reserved':time_start,
                        'occasion':kw.get('occasion')
                    })
                else:
                    time_start = datetime.strptime(kw.get('reservation_start').replace('T', ' '),
                                                   '%Y-%m-%d %H:%M:%S') - timedelta(hours=0, minutes=total_minute)
                    all_tables.sudo().write({
                        'date_reserved': time_start,
                        'occasion': kw.get('occasion')
                    })
                if len(kw.get('reservation_ends')) <= 16:
                    time_ends = datetime.strptime(kw.get('reservation_ends').replace('T', ' '),
                                                  '%Y-%m-%d %H:%M') - timedelta(hours=0, minutes=total_minute)
                    all_tables.sudo().write({
                        'date_reserved_end': time_ends,
                        'occasion': kw.get('occasion')
                    })
                else:
                    time_ends = datetime.strptime(kw.get('reservation_ends').replace('T', ' '),
                                                  '%Y-%m-%d %H:%M:%S') - timedelta(hours=0, minutes=total_minute)
                    all_tables.sudo().write({
                        'date_reserved_end': time_ends,
                        'occasion': kw.get('occasion')
                    })

            table_size = 0
            if all_tables.reservation_id:
                table_size += all_tables.reservation_id.seats
            if int(kw.get('party_size')) > table_size:
                # single table reservation try
                required_size = int(kw.get('party_size'))
                available_tables = request.env['restaurant.table'].sudo().search([('current_status', '=', 'available')])
                available_table = available_tables.filtered(
                    lambda table: (table.floor_id.id == all_tables.reservation_id.floor_id.id) and
                                  (table.seats >= required_size)
                )

                if available_table:
                    smallest_table = available_table[0]
                    smallest_table_size = available_table[0].seats
                    for table in available_table:
                        if table.seats < smallest_table_size:
                            smallest_table = table
                            smallest_table_size = table.seats
                    all_tables.sudo().write({
                        'reservation_id': smallest_table.id,
                        'no_of_people': int(kw.get('party_size'))
                    })
                    msg = 'Booking edited. Reservation Name: '+all_tables.name+' Table name: '+smallest_table.name
                else:
                    # find one available largest table, and merge another table with pending size
                    available_table = available_tables.filtered(
                        lambda table: (table.floor_id.id == all_tables.reservation_id.floor_id.id)
                    )
                    if available_table:
                        largest_table = ''
                        largest_table_size = 0
                        for table in available_table:
                            if table.seats > largest_table_size:
                                largest_table = table
                                largest_table_size = table.seats
                        required_size = int(kw.get('party_size')) - largest_table_size
                        available_table = available_tables.filtered(
                            lambda table: (table.floor_id.id == all_tables.reservation_id.floor_id.id) and
                                          (table.seats >= required_size) and (table.id != largest_table.id)
                        )
                        if available_table:
                            smallest_table = available_table[0]
                            smallest_table_size = available_table[0].seats
                            for table in available_table:
                                if table.seats < smallest_table_size:
                                    smallest_table = table
                                    smallest_table_size = table.seats
                            all_tables.sudo().write({
                                'reservation_id': largest_table.id,
                                'no_of_people': largest_table.seats
                            })
                            booking = request.env['website.reservation.line'].sudo().create(
                                {'reservation_id': smallest_table.id, 'partner_id': all_tables.partner_id.id,
                                 'no_of_people': required_size, 'date_reserved': all_tables.date_reserved,
                                 'date_reserved_end': all_tables.date_reserved_end, 'occasion': all_tables.occasion,
                                 'special_request': all_tables.special_request, 'merged_table': all_tables.reservation_id.id,
                                 'border_color': all_tables.border_color})
                            msg = 'Booking edited. 1) Reservation Name: ' + all_tables.name + ' Table name: ' +\
                                  largest_table.name + ' and 2) Reservation Name: ' + booking.name + ' Table name: ' +\
                                  smallest_table.name
                        else:
                            msg = "No tables available for expanding the party size"
            else:
                # if party size can be accommodated in the current table
                all_tables.sudo().write({
                    'no_of_people': int(kw.get('party_size'))
                })
                msg = 'Increased party size to ' + str(kw.get('party_size'))
        return msg

    @http.route('/get/booking/cancel', csrf=False, type='json', auth="public")
    def UpdateBookingsCancels(self, **kw):
        if kw.get('reservation_id'):
            all_tables = request.env['website.reservation.line'].sudo().search([('id', '=', kw.get('reservation_id'))],limit=1)
            all_tables.sudo().write({
                'state': 'cancel',
                'reservation_id': False

            })

    @http.route('/get/table/available/booking', csrf=False, type='json', auth="public")
    def UpdateTableAvailable(self, **kw):
        print("kwwwwwwwwwwwwwww",kw)
        print("kw",kw.get('selected_merge_table'))
        print("kw d",kw.get('selected_table'))
        selected_merge_table = kw.get('selected_merge_table')
        selected_table = kw.get('selected_table')
        time_gap = kw.get('time_gap')
        merge_request = kw.get('merge_request')
        selected_time = kw.get('select_time')
        booking_date = kw.get('booking_date').replace('-', '/')
        current = request.env.company
        tz = pytz.timezone(current.tz)

        if booking_date:
            booking_date = datetime.strptime(booking_date, '%Y/%m/%d').date()
        else:
            booking_date = fields.Date().today()
        # booking_date = datetime.strptime(booking_date, '%Y/%m/%d')

        res_config_settings = request.env['ir.config_parameter'].sudo()
        reservation_time = res_config_settings.get_param('website_reservation.reservation_time')
        if selected_time:
            time_val = datetime.strptime(selected_time, '%H:%M').time()
        else:
            # now = datetime.now()
            selected_time = str(datetime.now().strftime("%H:%M"))
            time_val = datetime.strptime(selected_time, '%H:%M').time()
        start_time = datetime.combine(booking_date, time_val)
        start_time = datetime.combine(booking_date, time_val) - Datetime.timedelta(hours=5, minutes=30)
        start_time = start_time - Datetime.timedelta(hours=00, minutes=float(time_gap))
        end_time = start_time + Datetime.timedelta(hours=00, minutes=float(reservation_time))
        end_time = end_time.replace(tzinfo=None)
        exist = False
        merge = 0
        # date_reserved, reservation_id
        if merge_request:
            existing = request.env['website.reservation.line'].sudo().search([('reservation_id','=',selected_table),('date_reserved', '>=', start_time), ('date_reserved_end', '<=', end_time)],limit=1)
            if existing:
                merge = 1
            existing1 = request.env['website.reservation.line'].sudo().search([('reservation_id','=',selected_merge_table),('date_reserved', '>=', start_time), ('date_reserved_end', '<=', end_time)],limit=1)
            if existing1:
                merge = 2
            return merge
        else:
            existing = request.env['website.reservation.line'].sudo().search([('reservation_id','=',selected_table),('date_reserved', '>=', start_time), ('date_reserved_end', '<=', end_time)],limit=1)
            if existing:
                return 3
            else:
                return 4
        return False




