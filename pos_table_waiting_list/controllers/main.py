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

_logger = logging.getLogger(__name__)

# class WebsiteBookingInformation(WebsiteSale):




class WebsiteBooking(http.Controller):

    @http.route('/booking', website=True, auth='public')
    def shops(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        sale_order = request.website.sale_get_order(force_create=True)
        table_booking = request.env['ir.config_parameter'].sudo().get_param('table_booking.table_booking')
        table_booking_product = request.env['ir.config_parameter'].sudo().get_param('table_booking.table_booking_product')
        Category = request.env['product.public.category']
        values = {
            'category': Category,
            'sale_order_id':sale_order.id,
        }

        if sale_order and table_booking and table_booking_product:
            for line in sale_order.order_line:
                line.sudo().unlink()
            return request.render("table_booking.booking_template", values)

    @http.route('/modify/success',type='http', website=True, auth='public')
    def success_shops(self, page=0, category=None, search='', ppg=False, **post):
        return request.render("website_reservation.modified_reservation_success")

    @http.route('/booking/modify/<int:order_id>/', website=True, auth='public')
    def shops_modify(self, order_id=None, **post):
        sale_order = request.env['sale.order'].search([('id', '=', int(order_id))])
        table_booking = request.env['ir.config_parameter'].sudo().get_param('table_booking.table_booking')
        table_booking_product = request.env['ir.config_parameter'].sudo().get_param(
            'table_booking.table_booking_product')
        Category = request.env['product.public.category']
        values = {
            'category': Category,
            'sale_order_id': sale_order.id,
            'sale_order': sale_order
        }
        return request.render("table_booking.modify_booking_table", values)

    @http.route('/get/count', website=True, type='json', auth='public', sitemap=False)
    def count(self, page=0, category=None, search='', ppg=False, **post):
        res = []
        res_config_settings = request.env['ir.config_parameter'].sudo()
        signup_timeout = res_config_settings.get_param('website_reservation.signup_timeout')
        signup_timeout = float(signup_timeout)
        res.append(signup_timeout)
        return res

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
        signup_timeout = res_config_settings.get_param('website_reservation.signup_timeout')

        booking_date = datetime.strptime(booking_date, '%Y/%m/%d').date()

        time_val = datetime.strptime(select_time, '%H:%M').time()
        start_time = datetime.combine(booking_date, time_val) - Datetime.timedelta(hours=5,minutes=30)
        end_time = start_time + relativedelta(minutes=float(reservation_time))
        all_tables_iiddd = request.env['website.reservation.line'].sudo().search([('id','=',44)])
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
        table_booking = request.env['ir.config_parameter'].sudo().get_param('table_booking.table_booking')
        table_booking_product = request.env['ir.config_parameter'].sudo().get_param('table_booking.table_booking_product')
        order = kw.get('order')
        sale_order_id = request.env['sale.order'].sudo().search([('id', '=', int(order))])
        sale_order_id.sudo().write({'carrier_id': 1})
        if order and table_booking and table_booking_product:
            first_name = kw.get('first_name')
            last_name = kw.get('last_name')
            phone = kw.get('phone')
            email = kw.get('email')
            floor_id = kw.get('floor_id')
            table_id = kw.get('table_id')
            if kw.get('notification_enable') == "on":
                notification_enable = True
            else:
                notification_enable = False
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
            start_time = datetime.combine(booking_date, time_val)
            start_time = datetime.combine(booking_date, time_val) - Datetime.timedelta(hours=5,minutes=30)
            end_time = start_time + Datetime.timedelta(hours=00, minutes=float(reservation_time))
            end_time = end_time.replace(tzinfo=None)
            old_user = request.env['res.users'].sudo().search([('login', '=', str(email))])
            if old_user:
                new_partner1 = request.env['res.partner'].sudo().search([('id', '=', old_user.partner_id.id)])
                new_partner1.sudo().write({'phone': phone, 'email': str(email)})
                country = request.env['res.country'].sudo().search([('code', '=', 'AU')], limit=1).id
                company = request.env['res.company'].sudo().browse(1)
                state_id = request.env['res.country.state'].sudo().search([('code', '=', 'QLD')], limit=1).id

                val = {
                    'company_type': 'person',
                    'parent_id': new_partner1.id,
                    'type': 'delivery',
                    'name': str(first_name + ' ' + last_name),
                    'phone': int(phone),
                    'email': str(email),
                    'notification_enable': notification_enable
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
                floor_id = request.env['restaurant.floor'].sudo().search([('id', '=', floor_id)], limit=1)
                if floor_id:
                    table = floor_id.table_ids
                    if table:
                        booking = request.env['website.reservation.line'].sudo().create(
                            {'reservation_id': int(table_id), 'partner_id': child.id,
                             'no_of_people': select_person, 'date_reserved': start_time,
                             'date_reserved_end': end_time, 'occasion': occasion_val,
                             'special_request': special_request})
                        if booking:
                            sale_order = request.env['sale.order.line'].sudo().create({
                                'order_id': int(order),
                                'customer_lead': 1,
                                'product_id': int(table_booking_product),
                                'product_uom_qty': 1.0,
                                'price_unit': 5
                            })
                            sale_order.order_id.sudo().write({
                                'is_table_booked': True,
                                'table_booked': booking.id
                            });
                            sale_order.order_id.onchange_partner_shipping_id()
                            sale_order._compute_tax_id()
                            sale_order.order_id.sudo().write({'partner_id': child.id})
                            sale_order.order_id.sudo().write({'carrier_id': 1})
                            sale_order.order_id.sudo().write({
                                'partner_shipping_id': child.id,
                                'partner_invoice_id': child.id,
                                'public_partner': child.id,
                                'carrier_id': 1,
                                'website_delivery_type': 'dine_in'
                            })
                            if sale_order.order_id.sudo().partner_id:
                                print("aaaa", sale_order)
                #
                # request.env.cr.commit()
            else:
                val = {
                    'name': str(first_name + ' ' + last_name),
                    'login': str(email),
                    'groups_id': [(4, request.env.ref('base.group_portal').id)],
                    'notification_enable': notification_enable
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
                request.env.cr.commit()
                floor_id = request.env['restaurant.floor'].sudo().search([('id', '=', floor_id)], limit=1)
                if floor_id:
                    table = floor_id.table_ids
                    if table:
                        booking = request.env['website.reservation.line'].sudo().create(
                            {'reservation_id': int(table_id), 'partner_id': new_user.partner_id.id,
                             'no_of_people': select_person, 'date_reserved': start_time,
                             'date_reserved_end': end_time, 'occasion': occasion_val,
                             'special_request': special_request})
                        if booking:
                            sale_order = request.env['sale.order.line'].sudo().create({
                                'order_id': int(order),
                                'customer_lead': 1,
                                'product_id': int(table_booking_product),
                                'product_uom_qty': 1.0,
                                'price_unit': 5,
                                'name': "booking"
                            })
                            sale_order.order_id.sudo().write({
                                'is_table_booked': True,
                                'table_booked': booking.id
                            });
                            sale_order.order_id.onchange_partner_shipping_id()
                            sale_order._compute_tax_id()
                            sale_order.order_id.sudo().write({'partner_id': new_user.partner_id.id})
                            sale_order.order_id.sudo().write({'carrier_id': 1})
                            sale_order.order_id.sudo().write({
                                'partner_shipping_id': new_user.partner_id.id,
                                'partner_invoice_id': new_user.partner_id.id,
                                'public_partner': new_user.partner_id.id,
                                'carrier_id': 1,
                                'website_delivery_type': 'dine_in'
                            })
                            if sale_order.order_id.sudo().partner_id:
                                print("aaaa", sale_order)
            request.session['sale_last_order_id_session'] = sale_order.order_id.id
            return True

    @http.route('/modify/user', csrf=False, type='json', auth="public")
    def ModifyUser(self, **kw):
        table_booking = request.env['ir.config_parameter'].sudo().get_param('table_booking.table_booking')
        table_booking_product = request.env['ir.config_parameter'].sudo().get_param('table_booking.table_booking_product')
        order = kw.get('order')
        sale_order_id = request.env['sale.order'].sudo().search([('id', '=', int(order))])
        sale_order_id.sudo().write({'carrier_id': 1 })
        sale_order_id.table_booked.unlink()
        if order and table_booking and table_booking_product:
            first_name = kw.get('first_name')
            last_name = kw.get('last_name')
            phone = kw.get('phone')
            email = kw.get('email')
            floor_id = kw.get('floor_id')
            table_id = kw.get('table_id')
            if kw.get('notification_enable') == "on":
                notification_enable = True
            else:
                notification_enable = False
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
            start_time = datetime.combine(booking_date, time_val)
            start_time = datetime.combine(booking_date, time_val) - Datetime.timedelta(hours=5, minutes=30)
            end_time = start_time + Datetime.timedelta(hours=00, minutes=float(reservation_time))
            end_time = end_time.replace(tzinfo=None)
            old_user = request.env['res.users'].sudo().search([('login', '=', str(email))])
            if old_user:
                new_partner1 = request.env['res.partner'].sudo().search([('id', '=', old_user.partner_id.id)])
                new_partner1.sudo().write({'phone': phone, 'email': str(email)})
                country = request.env['res.country'].sudo().search([('code', '=', 'AU')], limit=1).id
                company = request.env['res.company'].sudo().browse(1)
                state_id = request.env['res.country.state'].sudo().search([('code', '=', 'QLD')], limit=1).id

                val = {
                    'company_type': 'person',
                    'parent_id': new_partner1.id,
                    'type': 'delivery',
                    'name': str(first_name + ' ' + last_name),
                    'phone': int(phone),
                    'email': str(email),
                    'notification_enable': notification_enable
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
                floor_id = request.env['restaurant.floor'].sudo().search([('id', '=', floor_id)], limit=1)
                if floor_id:
                    table = floor_id.table_ids
                    if table:
                        booking = request.env['website.reservation.line'].sudo().create(
                            {'reservation_id': int(table_id), 'partner_id': child.id,
                             'no_of_people': select_person, 'date_reserved': start_time,
                             'date_reserved_end': end_time, 'occasion': occasion_val,
                             'special_request': special_request})
                        if booking:
                            sale_order_id.sudo().write({
                                'is_table_booked': True,
                                'table_booked': booking.id
                            });
                            sale_order_id.onchange_partner_shipping_id()
                            sale_order_id.sudo().write({'partner_id': child.id})
                            sale_order_id.sudo().write({'carrier_id': 1})
                            sale_order_id.sudo().write({
                                'partner_shipping_id': child.id,
                                'partner_invoice_id': child.id,
                                'public_partner': child.id,
                                'carrier_id': 1,
                            })
                            if sale_order_id.sudo().partner_id:
                                return True
            else:
                val = {
                    'name': str(first_name + ' ' + last_name),
                    'login': str(email),
                    'groups_id': [(4, request.env.ref('base.group_portal').id)],
                    'notification_enable': notification_enable
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
                             'special_request': special_request})
                        if booking:
                            sale_order_id.sudo().write({
                                'is_table_booked': True,
                                'table_booked': booking.id
                            });
                            sale_order_id.onchange_partner_shipping_id()
                            sale_order_id.sudo().write({'partner_id': new_user.partner_id.id})
                            sale_order_id.sudo().write({'carrier_id': 1})
                            sale_order_id.sudo().write({
                                'partner_shipping_id': new_user.partner_id.id,
                                'partner_invoice_id': new_user.partner_id.id,
                                'public_partner': new_user.partner_id.id,
                                'carrier_id': 1,
                            })
                            if sale_order_id.sudo().partner_id:
                                return True
            return True


    @http.route(['''/waiting_list/cancel/<int:id>/screen/<string:access_token>'''], type='http', auth="public", website=True)
    def waiting_list_cancels(self, id=None, access_token=None, **kw):
        if id:
            order = request.env['table.waiting.line'].sudo().search([('id', '=', id)], limit=1)
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info('rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr %s',id)
            order.sudo().write({'status': 'cancel'})
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info('rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr %s', order.status)
            return '/'

    @http.route(['''/waiting_list/confirm/<int:id>/screen/<string:access_token>'''], type='http', auth="public", website=True)
    def waiting_list_cancels(self, id=None, access_token=None, **kw):
        if id:
            order = request.env['table.waiting.line'].sudo().search([('id', '=', id)], limit=1)
            order.sudo().write({'status': 'confirmed'})
            return '/'


class WebsiteSaleInherits(WebsiteSale):

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        response = super(WebsiteSaleInherits, self).payment_confirmation(**post)
        if request.website.sale_get_order():
            print("request")
            _logger.info("request email to")
            return response
        else:
            if request.session['sale_last_order_id_session']:
                sale_order_id = request.env['sale.order'].sudo().browse(int(request.session['sale_last_order_id_session']))
                if sale_order_id:
                    order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id.id)])
                    template_id = request.env.ref('website_reservation.mail_template_table_reservation').id
                    template = request.env['mail.template'].sudo().browse(template_id)
                    email_to = order.table_booked.partner_id.email
                    template.email_to = email_to
                    sent_mail = template.send_mail(order.id, force_send=True)
                    return request.render("website_sale.confirmation", {'order': order})
                else:
                    return request.redirect('/shop')
            else:
                sale_order_id = request.website.sale_get_order(force_create=True).id - 1
                if sale_order_id:
                    order_id = request.env['sale.order'].sudo().browse(sale_order_id)
                    order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
                    _logger.info("order to")
                    _logger.info(order)
                    template_id = request.env.ref('website_reservation.mail_template_table_reservation').id
                    _logger.info("template_id")
                    _logger.info(template_id)
                    template = request.env['mail.template'].sudo().browse(template_id)
                    _logger.info("inside email to else")
                    email_to = order.table_booked.partner_id.email
                    _logger.info("email to")
                    _logger.info(email_to)
                    template.email_to = email_to
                    sent_mail = template.send_mail(order.id, force_send=True)
                    _logger.info("sent_mail")
                    _logger.info(sent_mail)
                    return request.render("website_sale.confirmation", {'order': order_id})
                else:
                    return request.redirect('/shop')
        return response