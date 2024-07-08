from odoo import _, api, fields, models
import datetime
import pytz
from dateutil.relativedelta import relativedelta
from pytz import timezone
from datetime import datetime, timedelta
import random


class WebsiteWaitLine(models.Model):
    _name = 'table.waiting.line'
    _rec_name = 'name'

    name = fields.Char('Name', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    customer = fields.Char('Customer')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    no_of_people = fields.Integer(string='Seats')
    status = fields.Selection(
        [('waiting', "Waiting"), ('confirmed', 'Confirmed'), ('cancel', 'Cancelled')])

    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company,
        index=True, readonly=True, required=True,
        help='The company is automatically set from your user preferences.')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('waiting.list.sequence') or _('New')
        return super(WebsiteWaitLine, self).create(vals)

    @api.model
    def get_waiting_list(self):
        try:
            booking_date = datetime.now()
            current = self.env.company
            tz = pytz.timezone(current.tz)
            now = datetime.utcnow()
            utc = timezone('UTC')
            utc.localize(datetime.now())
            delta = utc.localize(now) - tz.localize(now)
            sec = delta.seconds
            total_minute = sec / 60
            res_config_settings = self.env['ir.config_parameter'].sudo()
            reservation_time = res_config_settings.get_param('website_reservation.reservation_time')
            signup_timeout = res_config_settings.get_param('website_reservation.signup_timeout')
            start_time = booking_date+timedelta(hours=5, minutes=30)
            end_time = start_time + relativedelta(minutes=float(reservation_time))
            all_tables = self.env['website.reservation.line'].sudo().search(
                [('date_reserved_end', '>=', start_time), ('date_reserved', '<=', start_time)])
            table = all_tables.mapped('reservation_id.id')
            table_not_selected = self.env['restaurant.table'].sudo().search([('id', 'not in', table)])
            list_of_avialable_table = []
            for rec in table_not_selected:
                list_of_avialable_table.append(
                    {'floor': rec.floor_id.name, 'id': rec.floor_id.id, 'seats': rec.seats,
                     'table_id': rec.id, 'table_name': rec.name})
            if len(list_of_avialable_table) <= 0:
                pass
            else:
                pass

            current_date = datetime.now()
            waiting = self.env['table.waiting.line'].sudo().search([('status', 'in', ['waiting','cancel','confirmed'])])
            waiting_list = []
            for i in waiting:
                data = {
                    'id': i.id,
                    'name': i.name,
                    'customer': i.customer,
                    'email': i.email or False,
                    'phone': i.phone,
                    'seats': i.no_of_people,
                    'status': i.status,
                }
                waiting_list.append(data)
            waiting_data = {'available_tables': list_of_avialable_table, 'waiting_list': waiting_list}
            return waiting_data
        except:
            return False

    @api.model
    def saveWaitListData(self, wait_list_name, wait_list_phone, wait_list_email, wait_list_party_size):
        try:
            if wait_list_name and wait_list_phone and wait_list_party_size:
                wait_list = self.env['table.waiting.line']
                wait_list.sudo().create(
                    {'customer': wait_list_name, 'phone': wait_list_phone, 'no_of_people': wait_list_party_size,
                     'email': wait_list_email, 'status': 'waiting'})
                current_date = datetime.now()
                booking_date = datetime.now()
                current = self.env.company
                tz = pytz.timezone(current.tz)
                now = datetime.utcnow()
                utc = timezone('UTC')
                utc.localize(datetime.now())
                delta = utc.localize(now) - tz.localize(now)
                sec = delta.seconds
                total_minute = sec / 60
                res_config_settings = self.env['ir.config_parameter'].sudo()
                reservation_time = res_config_settings.get_param('website_reservation.reservation_time')
                signup_timeout = res_config_settings.get_param('website_reservation.signup_timeout')
                start_time = booking_date + timedelta(hours=5, minutes=30)
                end_time = start_time + relativedelta(minutes=float(reservation_time))
                all_tables = self.env['website.reservation.line'].sudo().search(
                    [('date_reserved_end', '>=', start_time), ('date_reserved', '<=', start_time)])
                table = all_tables.mapped('reservation_id.id')
                table_not_selected = self.env['restaurant.table'].sudo().search([('id', 'not in', table)])
                list_of_avialable_table = []
                for rec in table_not_selected:
                    list_of_avialable_table.append(
                        {'floor': rec.floor_id.name, 'id': rec.floor_id.id, 'seats': rec.seats,
                         'table_id': rec.id, 'table_name': rec.name})
                if len(list_of_avialable_table) <= 0:
                    pass
                else:
                    pass

                current_date = datetime.now()
                waiting = self.env['table.waiting.line'].sudo().search([('status', 'in', ['waiting','cancel','confirmed'])])
                waiting_list = []
                for i in waiting:
                    data = {
                        'id': i.id,
                        'name': i.name,
                        'customer': i.customer,
                        'email': i.email or False,
                        'phone': i.phone,
                        'seats': i.no_of_people,
                        'status': i.status,
                    }
                    waiting_list.append(data)
                waiting_data = {'available_tables': list_of_avialable_table, 'waiting_list': waiting_list}
                return waiting_data
            else:
                return False
        except:
            return False

    @api.model
    def edit_waiting_list(self, waiting):
        try:
            waiting_edit = []
            waiting = self.env['table.waiting.line'].sudo().search([('id', '=', int(waiting))], limit=1)
            if waiting:
                data = {
                    'id': waiting.id,
                    'name': waiting.name,
                    'customer': waiting.customer,
                    'email': waiting.email or False,
                    'phone': waiting.phone,
                    'seats': waiting.no_of_people,
                    'status': waiting.status,
                }
                # waiting_edit.append(data)
                # waiting_data = {'waiting_edit': data}
                return data
            else:
                return False
        except:
            return False

    @api.model
    def confirm_waiting_list(self, waiting):
        try:
            waiting_edit = []
            waiting_line = self.env['table.waiting.line'].sudo().search([('id', '=', int(waiting))], limit=1)
            waiting_line.sudo().write({'status': 'confirmed'})
            # template_id = self.env.ref('pos_table_waiting_list.mail_template_waiting_list_confirm').id
            # template = self.env['mail.template'].sudo().browse(template_id)
            # email_to = waiting_line.email
            # template.email_to = email_to
            # sent_mail = template.send_mail(waiting_line.id, force_send=True)
            # if waiting_line:
            #     data = {
            #         'id': waiting_line.id,
            #         'name': waiting_line.name,
            #         'customer': waiting_line.customer,
            #         'email': waiting_line.email or False,
            #         'phone': waiting_line.phone,
            #         'seats': waiting_line.no_of_people,
            #         'status': waiting_line.status,
            #     }
            #     return data
            # else:
            #     return False

            current_date = datetime.now()
            booking_date = datetime.now()
            current = self.env.company
            tz = pytz.timezone(current.tz)
            now = datetime.utcnow()
            utc = timezone('UTC')
            utc.localize(datetime.now())
            delta = utc.localize(now) - tz.localize(now)
            sec = delta.seconds
            total_minute = sec / 60
            res_config_settings = self.env['ir.config_parameter'].sudo()
            reservation_time = res_config_settings.get_param('website_reservation.reservation_time')
            signup_timeout = res_config_settings.get_param('website_reservation.signup_timeout')

            start_time = booking_date + timedelta(hours=5, minutes=30)
            end_time = start_time + relativedelta(minutes=float(reservation_time))
            all_tables = self.env['website.reservation.line'].sudo().search(
                [('date_reserved_end', '>=', start_time), ('date_reserved', '<=', start_time)])
            table = all_tables.mapped('reservation_id.id')
            table_not_selected = self.env['restaurant.table'].sudo().search([('id', 'not in', table)])
            list_of_avialable_table = []
            for rec in table_not_selected:
                list_of_avialable_table.append(
                    {'floor': rec.floor_id.name, 'id': rec.floor_id.id, 'seats': rec.seats,
                     'table_id': rec.id, 'table_name': rec.name})
            if len(list_of_avialable_table) <= 0:
                pass
            else:
                pass

            current_date = datetime.now()
            waiting = self.env['table.waiting.line'].sudo().search([('status', '=', 'waiting')])
            waiting_list = []
            for i in waiting:
                data = {
                    'id': i.id,
                    'name': i.name,
                    'customer': i.customer,
                    'email': i.email or False,
                    'phone': i.phone,
                    'seats': i.no_of_people,
                    'status': i.status,
                }
                waiting_list.append(data)
            waiting_data = {'available_tables': list_of_avialable_table, 'waiting_list': waiting_list}
            template = self.env.ref(
                "pos_table_waiting_list.mail_template_waiting_list_confirm")
            template.sudo().send_mail(
                waiting_line.id, force_send=True
            )
            return waiting_data
        except:
            return False

    # def cancel_reservation_order(self):
    #     sample_string = 'pqrstuvwxy'
    #     result = ''.join((random.choice(sample_string)) for x in range(50))
    #     self.token_random = result
    #     update_param = '/waiting_list/cancel/'+ str(self.sudo().id)+'/'+str(self.token_random)
    #     return update_param
    # @api.model


    def confirm_waiting_list_mail(self):
        print("lklklklk")
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww %s', self.id)
        waiting_line = self.env['table.waiting.line'].sudo().search([('id', '=', self.id)], limit=1)
        waiting_line.sudo().write({'status': 'cancel'})
        _logger.info('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww %s', waiting_line.status)
        return '/'
    # @api.model
    def cancel_waiting_list_mail(self):
        print("rytrytr")
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww %s', self.id)
        waiting_line = self.env['table.waiting.line'].sudo().search([('id', '=', self.id)], limit=1)
        waiting_line.sudo().write({'status': 'confirmed'})
        _logger.info('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww %s', waiting_line.status)
        return '/'

    token_random = fields.Char()

    def cancel_reservation_order1(self):
        """Create portal url for user to update the scheduled date on purchase
        order lines."""
        if not self.token_random:
            sample_string = 'pqrstuvwxy'
            result = ''.join((random.choice(sample_string)) for x in range(50))
            self.token_random = result
        update_param = '/waiting_list/cancel/'+str(self.id)+'/screen/'+str(self.token_random)
        return update_param

    def confirm_reservation_order1(self):
        """Create portal url for user to update the scheduled date on purchase
        order lines."""
        if not self.token_random:
            sample_string = 'pqrstuvwxy'
            result = ''.join((random.choice(sample_string)) for x in range(50))
            self.token_random = result
        update_param = '/waiting_list/confirm/'+str(self.id)+'/screen/'+str(self.token_random)
        return update_param