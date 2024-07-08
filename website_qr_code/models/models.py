from odoo import models, fields, api
from twilio.rest import Client
import threading
import random
import string
import pytz
_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]
def _tz_get(self):
    return _tzs


class SaleConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    dine_in_list_table = fields.Boolean("List Table For Dine In")

    def get_values(self):
        res = super(SaleConfig, self).get_values()
        res.update(
            dine_in_list_table=self.env['ir.config_parameter'].sudo().get_param(
                'website_qr_code.dine_in_list_table'),
        )
        return res

    def set_values(self):
        super(SaleConfig, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        dine_in_list_table = self.dine_in_list_table
        param.set_param('website_qr_code.dine_in_list_table', dine_in_list_table)


class SaleOrderQrcode(models.Model):
    _inherit = 'sale.order'

    qrcode_order = fields.Boolean(default=False)
    dine_in = fields.Boolean(default=False)
    take_away = fields.Boolean(default=False)
    dine_in_table = fields.Many2one('restaurant.table')
    dine_in_enable = fields.Boolean()

class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    counters = fields.Many2one("product.counters", string="Counters")

class FoodCounters(models.Model):
    _name = 'product.counters'
    _rec_name = "name"
    _description = "Food Counter"

    name = fields.Char()
    description = fields.Char()

class SaleOrderMessage(models.Model):
    _inherit = 'sale.order.line'

    message_sent = fields.Boolean(default=False)
    preparation_time_delivery = fields.Float("preparation Time", default=lambda self: round(
        float(self.env['ir.config_parameter'].sudo().get_param('website_sale_hour.delivery_time')) * 60))
    preparation_date_delivery = fields.Datetime("Preparation Date", default=lambda self: fields.Datetime.now())


class SaleOrderMessages(models.Model):
    _inherit = 'pos.order.line'

    message_sent = fields.Boolean(default=False)

class WeborderStaus(models.Model):

    _inherit = 'pos.order'

    @api.model
    def update_state_kwargs(self, id, state):
        print("twil pos", id, state)
        order_line = self.env['pos.order.line'].search([('id', '=', id)])
        order_line.order_line_state = state
        # counter = False
        # if order_line.product_id:
        #     for ecateg in order_line.product_id.public_categ_ids:
        #         if ecateg.counters:
        #             counter = ecateg.counters
        #
        # if counter and order_line.partner_id.phone:
        #     self.send_messages(order_line.partner_id.phone,counter,order_line.partner_id.name)
        return True

    @api.model
    def update_sale_state_kwargs(self, id, state):
        print("twilo sale", id, state)
        order_line = self.env['sale.order.line'].sudo().search([('id', '=', id)])
        order_line.order_line_state = str(state)
        if state == 'ready':
            counter = False
            if order_line.product_id:
                for ecateg in order_line.product_id.public_categ_ids:
                    if ecateg.counters:
                        counter = ecateg.counters.name

            if counter and order_line.order_id.partner_id.phone:
                self.send_messages(order_line.order_id.partner_id.phone, counter, order_line.order_id.partner_id.name)
        return True

    def send_prepared_messages(self,partner_id_name,phone,product):
        param_obj = self.env['ir.config_parameter']
        twilio_account_sid = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_account_sid')
        twilio_auth_token = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_auth_token')
        twilio_from_number = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_from_number')

        client = Client(twilio_account_sid, twilio_auth_token)
        message_body = "Hi " + str(
            partner_id_name) + ",your order [" + product + "] is ready to deliver."
        try:
            response = client.messages.create(body=message_body, from_=twilio_from_number, to=phone)
            if response.error_message:
                state = 'error'
                error_message = response.error_message
            else:
                state = 'sent'
                error_message = None
        except Exception as e:
            state = 'error'
            error_message = e.msg or e.__str__()

    def send_message_for_in_hotel(self,order_name,name,phone):
        param_obj = self.env['ir.config_parameter']
        twilio_account_sid = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_account_sid')
        twilio_auth_token = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_auth_token')
        twilio_from_number = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_from_number')

        client = Client(twilio_account_sid, twilio_auth_token)
        message_body = "Hi " + str(
            name) + ",your order [" + order_name + "] is ready to deliver."
        try:
            response = client.messages.create(body=message_body, from_=twilio_from_number, to=phone)
            if response.error_message:
                state = 'error'
                error_message = response.error_message
            else:
                state = 'sent'
                error_message = None
        except Exception as e:
            state = 'error'
            error_message = e.msg or e.__str__()

    def send_messages(self,phone,counter,name):
        param_obj = self.env['ir.config_parameter']
        twilio_account_sid = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_account_sid')
        twilio_auth_token = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_auth_token')
        twilio_from_number = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_from_number')

        client = Client(twilio_account_sid, twilio_auth_token)
        message_body = "Hi "+str(name)+",your order is ready to deliver ,please collect from "+str(counter)
        try:
            print("out",phone,counter,name)
            response = client.messages.create(body=message_body, from_=twilio_from_number, to=phone)
            if response.error_message:
                state = 'error'
                error_message = response.error_message
            else:
                state = 'sent'
                error_message = None
        except Exception as e:
            state = 'error'
            error_message = e.msg or e.__str__()

    def send_message_time_updation(self,partner,time, phone, name):
        param_obj = self.env['ir.config_parameter']
        twilio_account_sid = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_account_sid')
        twilio_auth_token = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_auth_token')
        twilio_from_number = param_obj.sudo().get_param('ql_scheduler_reminder.twilio_from_number')

        client = Client(twilio_account_sid, twilio_auth_token)
        message_body = "Hi " + str(partner) + ",your order Delivery time is changed to "+time+" [" + str(name)+"]"
        try:
            response = client.messages.create(body=message_body, from_=twilio_from_number, to=phone)
            if response.error_message:
                state = 'error'
                error_message = response.error_message
            else:
                state = 'sent'
                error_message = None
        except Exception as e:
            state = 'error'
            error_message = e.msg or e.__str__()
        # rec_id.write({'error_message': error_message, 'state': state})
class WeborderStausSale(models.Model):
    _inherit = 'sale.order'

    token_random = fields.Char()

    def get_urls_data(self):
        """Create portal url for user to update the scheduled date on purchase
        order lines."""
        if not self.token_random:
            sample_string = 'pqrstuvwxy'
            result = ''.join((random.choice(sample_string)) for x in range(50))
            self.token_random = result
        update_param = '/sale/'+str(self.id)+'/screen/'+str(self.token_random)
        return update_param

    # @api.model
    # def create(self, vals_list):
    #     res = super(WeborderStausSale, self). create(vals_list)
    #     if res:
    #         sample_string = 'pqrstuvwxy'
    #         result = ''.join((random.choice(sample_string)) for x in range(50))
    #         vals_list['token_random'] = result
    #         res.token_random=result
    #         self.env.cr.commit()
    #     return res


class WeborderResCompany(models.Model):
    _inherit = 'res.company'

    tz = fields.Selection(_tz_get, string='Timezone', default=lambda self: self._context.get('tz'),
                          help="When printing documents and exporting/importing data, time values are computed according to this timezone.\n"
                               "If the timezone is not set, UTC (Coordinated Universal Time) is used.\n"
                               "Anywhere else, time values are computed according to the time offset of your web client.")

    tz_offset = fields.Char(compute='_compute_tz_offset', string='Timezone offset', invisible=True)