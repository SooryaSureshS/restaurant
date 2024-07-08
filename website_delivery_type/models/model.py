# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging
import psycopg2
import time
from odoo.tools import float_is_zero
from odoo import models, fields, api, tools, _,SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from datetime import datetime
from operator import itemgetter
from timeit import itertools
from itertools import groupby
from datetime import date
import random
from odoo.addons.sale.models.payment import PaymentTransaction


def _reconcile_after_transaction_done(self):
    # Override of '_set_transaction_done' in the 'payment' module
    # to confirm the quotations automatically and to generate the invoices if needed.
    sales_orders = self.mapped('sale_order_ids').filtered(lambda so: so.state in ('draft', 'sent'))
    for tx in self:
        tx._check_amount_and_confirm_order()
    # send order confirmation mail
    # sales_orders._send_order_confirmation_mail()
    # invoice the sale orders if needed
    self._invoice_sale_orders()
    res = super(PaymentTransaction, self)._reconcile_after_transaction_done()
    if self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice'):
        default_template = self.env['ir.config_parameter'].sudo().get_param('sale.default_email_template')
        if default_template:
            for trans in self.filtered(lambda t: t.sale_order_ids):
                trans = trans.with_company(trans.acquirer_id.company_id).with_context(
                    mark_invoice_as_sent=True,
                    company_id=trans.acquirer_id.company_id.id,
                )
                for invoice in trans.invoice_ids.with_user(SUPERUSER_ID):
                    if sales_orders:
                        invo_id = []
                        for sale in sales_orders:
                            if sale.invoice_ids:
                                if sale.website_delivery_type == 'dine_in':
                                    invo_id.append(invoice.id)
                        # if invoice.id not in invo_id:
                        #     invoice.message_post_with_template(int(default_template),
                        #                                        email_layout_xmlid="mail.mail_notification_paynow")
    # send order confirmation mail
    sales_orders._send_order_confirmation_mail()
    return res
PaymentTransaction._reconcile_after_transaction_done = _reconcile_after_transaction_done

class ResPartner(models.Model):
    _inherit = 'res.partner'

    user_lat = fields.Char("User Latitude")
    user_long = fields.Char("User Longitude")


class WebsiteDeliveryType(models.Model):
    _inherit = 'sale.order'

    def get_address_update_data(self):
        """Create portal url for user to update the scheduled date on purchase
        order lines."""
        if not self.token_random:
            sample_string = 'pqrstuvwxy'
            result = ''.join((random.choice(sample_string)) for x in range(50))
            self.token_random = result
        update_param = '/sale/'+str(self.id)+'/update/address/'+str(self.token_random)
        return update_param

    def get_order_summary(self):
        """Create portal url for user to update the scheduled date on purchase
        order lines."""
        if not self.token_random:
            sample_string = 'pqrstuvwxy'
            result = ''.join((random.choice(sample_string)) for x in range(50))
            self.token_random = result
        update_param = '/sale/'+str(self.id)+'/order/summary/'+str(self.token_random)
        return update_param

    website_delivery_type = fields.Selection([
        ('delivery', 'Delivery'),
        ('pickup', 'Pickup'), ('curb', 'Kerbside Pickup'), ('dine_in', 'Dine in')], string='Website Delivery Type',
        default='delivery')
    pickup_date = fields.Datetime(string="Pickup Date & Time")
    pickup_date_string = fields.Char(string="Pickup Date Time")
    vehicle_type = fields.Many2one(
        'vehicle.type',
        string='Vehicle Type',
    )
    vehicle_make = fields.Many2one(
        'vehicle.make',
        string='Vehicle Make',
    )
    approximate_location = fields.Many2one(
        'vehicle.location',
        string='Vehicle Location',
    )
    approximate_location_ids = fields.Many2many(
        'vehicle.location',
        string='Vehicle Location', compute='_get_default_approximate_location_ids')
    location_notes = fields.Char("Location Note")
    vehicle_color = fields.Char("Vehicle Color")
    license_plate_no = fields.Char("Licence Plate No.")
    delivery_time = fields.Float("Delivery Time", digits=(16, 2))
    updated_location = fields.Boolean('Updated Location', default=False)
    parent_id = fields.Many2one('sale.order', string='Sale order', index=True)

    @api.depends('website_delivery_type')
    def _get_default_approximate_location_ids(self):
        location_data = self.env['vehicle.location'].search([])
        self.approximate_location_ids = location_data.ids

    def action_location_update(self):
        for rec in self:
            rec.updated_location = False

    def _check_carrier_quotation(self, force_carrier_id=None):
        self.ensure_one()
        DeliveryCarrier = self.env['delivery.carrier']

        if self.only_services:
            self.write({'carrier_id': None})
            self._remove_delivery_line()
            return True
        else:
            self = self.with_company(self.company_id)
            # attempt to use partner's preferred carrier
            if not force_carrier_id and self.partner_shipping_id.property_delivery_carrier_id:
                force_carrier_id = self.partner_shipping_id.property_delivery_carrier_id.id

            carrier = force_carrier_id and DeliveryCarrier.browse(force_carrier_id) or self.carrier_id
            available_carriers = self._get_delivery_methods()
            if carrier:
                if carrier not in available_carriers:
                    carrier = DeliveryCarrier
                else:
                    # set the forced carrier at the beginning of the list to be verfied first below
                    available_carriers -= carrier
                    available_carriers = carrier + available_carriers
            if force_carrier_id or not carrier or carrier not in available_carriers:
                for delivery in available_carriers:
                    verified_carrier = delivery._match_address(self.partner_shipping_id)
                    if verified_carrier:
                        carrier = delivery
                        break
                self.write({'carrier_id': carrier.id})
            self._remove_delivery_line()
            if carrier:
                res = carrier.rate_shipment(self)
                if res.get('success'):
                    self.set_delivery_line(carrier, 0.0)
                    self.delivery_rating_success = True
                    self.delivery_message = res['warning_message']
                else:
                    self.set_delivery_line(carrier, 0.0)
                    self.delivery_rating_success = False
                    self.delivery_message = res['error_message']

        return bool(carrier)

    @api.model
    def delivery_type(self, order_id, delivery_type):
        order = int(order_id)
        delivery = str(delivery_type)
        method = ""
        if delivery == 'pickup':
            method = "pickup"
        elif delivery == 'delivery':
            method = "delivery"
        if order_id:
            order = self.env['sale.order'].sudo().search([('id', '=', order)])
            if order:
                order.sudo().write({'website_delivery_type': method})

    @api.model
    def pickup_time(self, pickup_date, pickup_time, order_id):

        pickup_date_time = ''
        pickup_date_val = ''
        if pickup_date == 'Today':
            pickup_date_val = date.today()
        else:
            pickup_date_val = datetime.strptime(pickup_date, '%m/%d/%Y').date()
        if pickup_time:
            time_val = datetime.strptime(pickup_time, '%H:%M').time()
            pickup_date_time = datetime.combine(pickup_date_val, time_val)
        if pickup_date and pickup_time and order_id:
            if order_id:
                order = self.env['sale.order'].sudo().search([('id', '=', int(order_id))])
                if order:
                    order.sudo().write({'pickup_date': pickup_date_time})

    feedback_face = fields.Selection([
        ('sad', 'Sad'),
        ('good', 'Good')], string='Feed back face')

    feedback_note = fields.Text(string="FeedBack Note")
    feedback_check = fields.Boolean(string="FeedBack Check")


    def get_urls_feedback(self):

        update_param = '/feedback/order/'+str(self.id)
        return update_param


class VehicleType(models.Model):
    _name = 'vehicle.type'
    _description = 'Vehicle Type'
    _rec_name = 'type_name'

    type_name = fields.Char('Type')


class VehicleMake(models.Model):
    _name = 'vehicle.make'
    _description = 'Vehicle Type'
    _rec_name = 'make_name'

    make_name = fields.Char('Make')


class VehicleLocation(models.Model):
    _name = 'vehicle.location'
    _description = 'Vehicle Location'
    _rec_name = 'location_name'

    location_name = fields.Char('Location')

    def ChangeToPortal(self):
        users = self.env['res.users'].sudo().search([('share','=',False)])
        print(users)
        for i in users:
            if i.login_date:
                pass
            else:
                i.sudo().write({'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]})

class VehicleLocation(models.Model):
    _name = 'suburb.location'
    _description = 'Vehicle Location'
    _rec_name = 'location_name'

    location_name = fields.Char('Location')
    # zip_code = fields.Char('zip code')
    suburb_id = fields.Many2one('res.company', string="Suburb ID")

class ResCompany(models.Model):
    _inherit = "res.company"

    # location_name = fields.Char('Location')
    suburb_location_ids = fields.One2many('suburb.location', 'suburb_id', string="Suburb Lines")
    location_picker = fields.Boolean(default=True)
    check_delivery_distance = fields.Boolean(default=True)


