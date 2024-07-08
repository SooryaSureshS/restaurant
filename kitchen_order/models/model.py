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


# Enable this checkbox for using kitchen screen


_logger = logging.getLogger(__name__)


class PosConfigKitchen(models.Model):
    _inherit = 'pos.config'

    iface_kitchen_order = fields.Boolean(string='Kitchen Order', help='Allow the Kitchen Order.')
    kitchen_order_receipt = fields.Boolean(string='Kitchen Order Receipt')
    time_out_screens = fields.Integer(string='Time out screen', default=30)
    limit_reload = fields.Integer(string='Limit Reload', default=300)
    long_pooling_port = fields.Integer(string='Limit Reload', default=8072)
    ipaddress = fields.Char(string='Ip address', default='http://0.0.0.0:8069')
    send_message = fields.Boolean(string='Send Message to Kitchen')
    send_sms = fields.Boolean(string='Send SMS')
    collection_sound = fields.Boolean(string='Enable Collection Sound', default=True)
    collection_tune = fields.Selection([('error', 'Error'),
                                        ('bell', 'Default Odoo bell'),
                                        ('order_up', 'Order Up Message'),
                                        ('notification_ring', 'Notification Ring'),
                                        ('marimba', 'Marimba Ring Tune'),
                                        ('sweet_message', 'Sweet Message'),
                                        ('moto_e2', 'Moto e2'),
                                        ('simple_ring', 'simple ring'),
                                        ('old_phone', 'Old phone'),
                                        ('simple_ringtone1', 'Simple Ringtone1')], string='Collection Tune',
                                       required=True, default='sweet_message')
    waiting_sound = fields.Boolean(string='Enable Waiting Sound', default=True)
    waiting_tune = fields.Selection([('error', 'Error'),
                                     ('bell', 'Default Odoo bell'),
                                     ('order_up', 'Order Up Message'),
                                     ('notification_ring', 'Notification Ring'),
                                     ('marimba', 'Marimba Ring Tune'),
                                     ('sweet_message', 'Sweet Message'),
                                     ('moto_e2', 'Moto e2'),
                                     ('simple_ring', 'simple ring'),
                                     ('old_phone', 'Old phone'),
                                     ('simple_ringtone1', 'Simple Ringtone1')], string='Waiting Tune',
                                    required=True, default='notification_ring')
    kerbside_pickup_sound = fields.Boolean(string='Enable Kerbside Pickup Sound', default=True)
    kerbside_pickup_tune = fields.Selection([('error', 'Error'),
                                     ('bell', 'Default Odoo bell'),
                                     ('order_up', 'Order Up Message'),
                                     ('notification_ring', 'Notification Ring'),
                                     ('marimba', 'Marimba Ring Tune'),
                                     ('sweet_message', 'Sweet Message'),
                                     ('moto_e2', 'Moto e2'),
                                     ('simple_ring', 'simple ring'),
                                     ('old_phone', 'Old phone'),
                                     ('simple_ringtone1', 'Simple Ringtone1')], string='Kerbside Tune',
                                    required=True, default='notification_ring')
    new_order_sound = fields.Boolean(string='Enable New Order Sound', default=True)
    new_order_tune = fields.Selection([('error', 'Error'),
                                       ('bell', 'Default Odoo bell'),
                                       ('allison', 'Order Up by allison'),
                                       ('arnold', 'Order Up by arnold'),
                                       ('obama', 'Order Up by obama'),
                                       ('bill-gates', 'Order Up By bill gates'),
                                       ('donald-trump', 'Order Up By donald trump'),
                                       ('lee', 'Order Up By US lee'),
                                       ('leonard-nimoy', 'Order Up By US leonard nimoy'),
                                       ('tom', 'Order Up By US tom'),
                                       ('zoe', 'Order Up By US zoe'),
                                       ('order_up', 'Order Up Message'),
                                       ('notification_ring', 'Notification Ring'),
                                       ('marimba', 'Marimba Ring Tune'),
                                       ('sweet_message', 'Sweet Message'),
                                       ('moto_e2', 'Moto e2'),
                                       ('simple_ring', 'simple ring'),
                                       ('old_phone', 'Old phone'),
                                       ('simple_ringtone1', 'Simple Ringtone1')],
                                      string='New Order Tune', required=True,
                                      default='order_up')
    fried_product = fields.Boolean(string='Fried Product Screen')
    uhc_product = fields.Boolean(string='UHC Product Screen')
    kerbside_popup = fields.Boolean(string='Kerbside Popup')
    voice_assistance = fields.Boolean(string='Enable Voice Assistance', default=False)
    global_search = fields.Boolean(string='Enable Voice Assistance search global', default=False)
    show_only_delivery_order = fields.Boolean('Show Delivery Order Only')
    show_all_order_expect_delivery = fields.Boolean('Show All Order Expect Delivery Order')
    show_only_pos_order = fields.Boolean('Show Only Pos Orders')
    enable_pre_order = fields.Boolean()
    pre_order_time = fields.Integer('Pre Order Time')



# Extra status and note field for kitchen screen
class SaleLine(models.Model):
    _inherit = 'sale.order.line'

    order_line_note = fields.Char("Order Note")
    order_line_state = fields.Selection(
        selection=[("waiting", "Waiting"), ("preparing", "Preparing"), ("ready", "Ready for Delivery"),
                   ("delivering", "Deliver"), ("done", "Done"), ("cancel", "Cancel"), ("return", "Return")],
        default="preparing")
    pos_categ_id = fields.Char()
    order_product_name = fields.Char()

    @api.model
    def create(self, vals):
        product = self.env['product.product'].search([('id', '=', vals['product_id'])])
        vals['pos_categ_id'] = product.pos_categ_id.id
        vals['order_product_name'] = product.name
        orders = super(SaleLine, self).create(vals)
        return orders


class PosLine(models.Model):
    _inherit = 'pos.order.line'

    order_line_note = fields.Char("Order Note")
    order_line_state = fields.Selection(selection=[
        ("waiting", "Waiting"), ("preparing", "Preparing"),
        ("ready", "Ready for Delivery"),
        ("delivering", "Deliver"), ("done", "Done"),
        ("cancel", "Cancel"), ("return", "Return")], default="preparing")
    table = fields.Char("Table")
    floor = fields.Char("Floor")
    customer = fields.Many2one('res.partner')
    pos_categ_id = fields.Char()

    @api.model
    def create(self, values):
        pos_order = self.env['pos.order'].search([('id', '=', values['order_id'])])
        product = self.env['product.product'].search([('id', '=', values['product_id'])])
        values['table'] = pos_order.table_id.name
        values['floor'] = pos_order.table_id.floor_id.name
        values['pos_categ_id'] = product.pos_categ_id.id
        orders = super(PosLine, self).create(values)
        return orders


class ResUsers(models.Model):
    _inherit = 'res.users'

    kitchen_screen_user = fields.Selection([('cook', 'Cook'), ('manager', 'Manager'), ('admin', 'Admin')],
                                           string="Kitchen Screen User")
    pos_category_ids = fields.Many2many('pos.category', string="POS Categories")
    default_pos = fields.Many2one('pos.config', string="POS Config")
    cook_user_ids = fields.Many2many('res.users', 'cook_user_rel', 'user_id', 'cook_user_id', string='Cook Users')


class POSOrder(models.Model):
    _inherit = 'pos.order'

    start_order_time = fields.Datetime("Start Time")
    finish_order_time = fields.Datetime("Finish Time")
    delivery_order_time = fields.Datetime("Collect/Delivery TIme")
    done_order_time = fields.Datetime("Preparation TIme")
    recall_order = fields.Boolean("Recall Order",store=True)

    @api.model
    def _process_order(self, order, draft, existing_order):
        """Create or update an pos.order from a given dictionary.

        :param dict order: dictionary representing the order.
        :param bool draft: Indicate that the pos_order is not validated yet.
        :param existing_order: order to be updated or False.
        :type existing_order: pos.order.
        :returns: id of created/updated pos.order
        :rtype: int
        """
        order = order['data']
        pos_session = self.env['pos.session'].browse(order['pos_session_id'])
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':
            order['pos_session_id'] = self._get_valid_session(order).id

        pos_order = False
        if not existing_order:
            pos_order = self.create(self._order_fields(order))
        else:
            product_dict = {}
            pos_order = existing_order
            for line in pos_order.lines:
                product_dict[line.product_id.id] = line.order_line_state
            pos_order.lines.unlink()
            order['user_id'] = pos_order.user_id.id
            product_dict_key = product_dict.keys()
            # for rec in order:
            if order.get('lines', False):
                for r in order.get('lines', False):
                    e_line = r[2]
                    if e_line.get('product_id') in product_dict_key:
                        e_line['order_line_state'] = product_dict.get(e_line.get('product_id'))
            pos_order.write(self._order_fields(order))

        pos_order = pos_order.with_company(pos_order.company_id)
        self = self.with_company(pos_order.company_id)
        self._process_payment_lines(order, pos_order, pos_session, draft)

        if not draft:
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.DatabaseError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

        pos_order._create_order_picking()
        if pos_order.to_invoice and pos_order.state == 'paid':
            pos_order.action_pos_order_invoice()

        return pos_order.id

    @api.model
    def get_pos_lines(self, data):
        orders = self.env['pos.order.line'].search([('order_line_state', '!=', ['done', 'cancel'])])
        pos_orders = []
        if orders:
            for line in orders:
                vals = {
                    'id': line.id,
                    'name': line.full_product_name,
                    'qty': line.qty,
                    'table': line.table,
                    'floor': line.floor,
                    'create_date': line.create_date,
                    'state': line.order_line_state,
                    'none': line.note,
                }
                pos_orders.append(vals)
        return pos_orders

    @api.model
    def broadcast_order_data(self, new_order):
        notifications = []
        vals = {}
        pos_order = self.search([('lines.order_line_state', 'not in', ['cancel', 'done'])])
        manager_id = self.env['res.users'].search([('kitchen_screen_user', '=', 'manager')], limit=4)
        screen_table_data = []
        for order in pos_order:
            order_line_list = []
            for line in order.lines:
                order_line = {
                    'id': line.id,
                    'name': line.product_id.display_name,
                    'qty': line.qty,
                    'table': line.order_id.table_id.name,
                    'floor': line.order_id.table_id.floor_id.name,
                    'state': line.order_line_state,
                    'note': line.order_line_note,
                    'categ_id': line.product_id.product_tmpl_id.pos_categ_id.id,
                    'order': line.order_id.id,
                    'user': line.create_uid.id,
                    'route_id': line.product_id.product_tmpl_id.route_ids.active,
                }
                order_line_list.append(order_line)
            order_dict = {
                'order_id': order.id,
                'order_name': order.name,
                'table': order.table_id.name,
                'floor': order.table_id.floor_id.name,
                'customer': order.partner_id.name,
                'order_lines': order_line_list,
                'total': order.amount_total,
                'note': order.note,
                'user_id': order.user_id.id,
            }
            screen_table_data.append(order_dict)

        kitchen_group_data = {}
        sort_group = sorted(screen_table_data, key=itemgetter('user_id'))
        for key, value in itertools.groupby(sort_group, key=itemgetter('user_id')):
            if key not in kitchen_group_data:
                kitchen_group_data.update({key: [x for x in value]})
            else:
                kitchen_group_data[key] = [x for x in value]
        if kitchen_group_data:
            for user_id in kitchen_group_data:
                user = self.env['res.users'].browse(user_id)
                if user and user.cook_user_ids:
                    for cook_user_id in user.cook_user_ids:
                        if len(vals) > 0:
                            d1 = kitchen_group_data[user_id]
                            order_list = []
                            for each_order in d1:
                                order_list.append(each_order)
                            vals['orders'] = order_list
                        else:
                            vals = {
                                "orders": kitchen_group_data[user_id],
                            }
                        if new_order:
                            vals['new_order'] = new_order
                        notifications.append(
                            ((self._cr.dbname, 'pos.order.line', cook_user_id.id), {'screen_display_data': vals}))
                if user and user.kitchen_screen_user != 'manager':
                    for manager in manager_id:
                        notifications.append(
                            ((self._cr.dbname, 'pos.order.line', manager.id), {'screen_display_data': vals}))
        else:
            for manager in manager_id:
                notifications.append(
                    ((self._cr.dbname, 'pos.order.line', manager.id), {'screen_display_data': vals}))
            cook_user_ids = self.env['res.users'].search([('kitchen_screen_user', '=', 'manager')])
            if cook_user_ids:
                for each_cook_id in cook_user_ids:
                    notifications.append(
                        ((self._cr.dbname, 'pos.order.line', each_cook_id.id), {'screen_display_data': vals}))
        if notifications:
            self.env['bus.bus'].sendmany(notifications)
        return True

    def _broadcast(self, partner_ids):
        """ Broadcast the current channel header to the given partner ids
            :param partner_ids : the partner to notify
        """
        notifications = self._channel_channel_notifications(partner_ids)
        self.env['bus.bus'].sendmany(notifications)

    @api.model
    def update_state_kwargs(self, id, state):
        order_line = self.env['pos.order.line'].search([('id', '=', id)])
        order_line.order_line_state = state
        return True

    @api.model
    def update_sale_state_kwargs(self, id, state):
        order_line = self.env['sale.order.line'].sudo().search([('id', '=', id)])
        order_line.order_line_state = str(state)
        return True

    @api.model
    def load_order_details(self, order):
        lines = []
        data = {}
        if order['type'] == 'pos':
            line_obj = self.env['pos.order.line'].sudo().search([('name', '=', order['name'])])
            order_obj = self.env['pos.order'].sudo().search([('id', '=', line_obj.order_id.id)])
            if line_obj:
                data['id'] = line_obj.id
                data['create_date'] = line_obj.create_date
                data['customer'] = order_obj.partner_id.name
                data['is_pos_order'] = True
                data['line_name'] = line_obj.name
                data['product_id'] = line_obj.product_id.name
                data['subtotal'] = line_obj.price_subtotal_incl
                data['company_id'] = line_obj.company_id.name
                data['qty'] = line_obj.qty
                data['order_line_note'] = line_obj.order_line_note
                data['order_id'] = line_obj.order_id.id
                data['pos_reference'] = order_obj.pos_reference
                data['tabel_id'] = [order_obj.table_id.id, order_obj.table_id.name] if order_obj.table_id else False
                data[
                    'floor_id'] = order_obj.table_id.floor_id.name if order_obj.table_id and order_obj.table_id.floor_id else False
                lines.append(data)

            return lines
        # if order.type == 'sale':

    @api.model
    def load_order_line_details(self, line_id):
        data = {}
        line_obj = self.env['pos.order.line'].search_read([('id', '=', line_id)])
        if line_obj:
            order_obj = self.browse(line_obj[0].get('order_id')[0])
            data['id'] = line_obj[0].get('id')
            data['product_id'] = line_obj[0].get('product_id')
            data['uom_id'] = self.env['product.product'].browse(line_obj[0].get('product_id')[0]).uom_id.name
            data['company_id'] = line_obj[0].get('company_id')
            data['qty'] = line_obj[0].get('qty')
            data['order_line_note'] = line_obj[0].get('order_line_note')
            data['order_id'] = line_obj[0].get('order_id')
            data['state'] = line_obj[0].get('state')
            data['pos_reference'] = order_obj.pos_reference
            data['tabel_id'] = [order_obj.table_id.id, order_obj.table_id.name] if order_obj.table_id else False
            data[
                'floor_id'] = order_obj.table_id.floor_id.name if order_obj.table_id and order_obj.table_id.floor_id else False
        return [data]

    @api.model
    def load_sale_order_details(self, order):
        lines = []
        data = {}
        line_obj = self.env['sale.order.line'].sudo().search([('id', '=', int(order))])
        order_obj = self.env['sale.order'].sudo().search([('id', '=', line_obj.order_id.id)])
        if line_obj:
            data['id'] = line_obj.id
            data['create_date'] = line_obj.create_date
            data['customer'] = order_obj.partner_id.name
            data['is_pos_order'] = False
            data['line_name'] = line_obj.name
            data['product_id'] = line_obj.product_id.name
            data['subtotal'] = line_obj.price_subtotal
            data['company_id'] = line_obj.company_id.name
            data['qty'] = line_obj.product_uom_qty
            data['order_line_note'] = line_obj.order_line_note
            data['order_id'] = line_obj.order_id.id
            data['name'] = order_obj.name
            lines.append(data)
        return lines

    @api.model
    def load_sale_order_line_details(self, line_id):
        data = {}
        line_obj = self.env['sale.order.line'].sudo().search_read([('id', '=', line_id)])
        if line_obj:
            data['id'] = line_obj[0].get('id')
            data['product_id'] = line_obj[0].get('product_id')
            data['uom_id'] = self.env['product.product'].browse(line_obj[0].get('product_id')[0]).uom_id.name
            data['company_id'] = line_obj[0].get('company_id')
            data['qty'] = line_obj[0].get('product_uom_qty')
            data['order_line_note'] = line_obj[0].get('order_line_note')
            data['order_id'] = line_obj[0].get('order_id')
            data['state'] = line_obj[0].get('state')
            data['sale_reference'] = line_obj[0].get('order_id')[1]
        return [data]


class SaleOrdersLine(models.Model):
    _inherit = 'sale.order'

    preparation_time = fields.Integer("preparation Time", default=30)
    kitchen_screen = fields.Boolean("kitchen screen", default=True)
    preparation_date = fields.Datetime("Preparation Date", default=lambda self: fields.Datetime.now())
    token_random = fields.Char()
    order_sequence = fields.Integer( default=0,store=True)

    start_order_time = fields.Datetime("Start Time")
    finish_order_time = fields.Datetime("Finish Time")
    delivery_order_time = fields.Datetime("Collect/Delivery TIme")
    done_order_time = fields.Datetime("Preparation TIme")
    recall_order = fields.Boolean("Recall Order", store=True)
    is_printed = fields.One2many('receipt.kitchen.sale', 'sale_receipt_id', string="Is Printed")
    fried_state = fields.Selection(selection=[("preparing", "Preparing"), ("done", "Done"),
                                              ("finish", "Finish")], default="preparing")


class SaleReceiptPrint(models.Model):
    _name = 'receipt.kitchen.sale'
    _description = 'Sale Receipt'

    sale_receipt_id = fields.Many2one('sale.order')
    session = fields.Many2one('pos.session')


class POSReceiptPrint(models.Model):
    _name = 'receipt.kitchen.pos'
    _description = 'POS Receipt'

    pos_receipt_id = fields.Many2one('pos.order')
    session = fields.Many2one('pos.session')


class PosOrdersLine(models.Model):
    _inherit = 'pos.order'

    is_printed = fields.One2many('receipt.kitchen.pos', 'pos_receipt_id', string="Is Printed")
    preparation_time = fields.Integer("preparation Time", default=30)
    order_sequence = fields.Integer(default=0, store=True)

    kitchen_screen = fields.Boolean("kitchen screen", default=True)
    preparation_date = fields.Datetime("Preparation Date", default=lambda self: fields.Datetime.now())

    order_line_state = fields.Selection(selection=[("waiting", "Waiting"), ("preparing", "Preparing"),
                                                   ("ready", "Ready for Delivery"),
                                                   ("delivering", "Deliver"), ("done", "Done"),
                                                   ("cancel", "Cancel"), ("return", "Return")], default="preparing")
    fried_state = fields.Selection(selection=[("preparing", "Preparing"), ("done", "Done"),
                                              ("finish", "Finish")], default="preparing")
    preparation_ids = fields.One2many('pos.preparation', 'pos_order_id', string="Preparation Lines")
    rel_ids = fields.One2many('pos.rel', 'pos_id', string="Preparation Status")

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        new_orders = self.env['pos.rel'].search([('pos_id', '=', order.id)])
        if new_orders:
            for line in order.lines:
                for orderline in new_orders:
                    if orderline.product_id.id == line.product_id.id:
                        line.write({
                            'order_line_state': orderline.order_line_state,
                            'preparation_time': orderline.preparation_time,
                            'preparation_date': orderline.preparation_date
                        })
        res = super(PosOrdersLine, self)._payment_fields(order, ui_paymentline)
        return res

    @api.model
    def create(self, vals_list):
        res = super(PosOrdersLine, self).create(vals_list)
        if res:
            res.preparation_ids.create({
                'pos_order_id': res.id,
                'session': res.session_id.id
            })
            for line in res.lines:
                val = {
                    'pos_id': res.id,
                    'product_id': line.product_id.id,
                    'order_line_state': line.order_line_state,
                    'preparation_time': line.preparation_time,
                }
                exist = res.rel_ids.sudo().search([('pos_id', '=', res.id), ('product_id', '=', line.product_id.id)],
                                                  limit=1)
                if exist:
                    exist.write(val)
                else:
                    self.env['pos.rel'].sudo().create(val)
        return res


class PosOrdersLineUpdates(models.Model):
    _name = 'pos.rel'
    _description = 'Pos Reference'

    pos_id = fields.Many2one('pos.order')
    product_id = fields.Many2one('product.product')
    order_line_state = fields.Selection(
        selection=[("waiting", "Waiting"), ("preparing", "Preparing"), ("ready", "Ready for Delivery"),
                   ("delivering", "Deliver"),
                   ("done", "Done"), ("cancel", "Cancel"), ("return", "Return")], default="preparing")
    note = fields.Char()
    preparation_time = fields.Integer("preparation Time", default=30)
    preparation_date = fields.Datetime("Preparation Date", default=lambda self: fields.Datetime.now())


class PosOrdersPreparation(models.Model):
    _name = 'pos.preparation'
    _description = 'Pos Preparation'

    pos_order_id = fields.Many2one('pos.order')
    session = fields.Many2one('pos.session')
    preparation_time = fields.Integer("preparation Time", default=30)


class PosOrdersLinePreparation(models.Model):
    _inherit = 'pos.order.line'

    preparation_time = fields.Float("preparation Time", default=lambda self: round(
        float(self.env['ir.config_parameter'].sudo().get_param('website_sale_hour.pickup_time')) * 60))
    preparation_date = fields.Datetime("Preparation Date", default=lambda self: fields.Datetime.now())
    uhc_state = fields.Selection([('preparing', 'Preparing'), ('start', 'Start'),
                                  ('finish', 'Finish')], default='preparing')
    order_line_mark = fields.Boolean('Marked')
    fried_ids = fields.One2many('pos.kitchen.fried.line', 'pos_line_id', string='Fried items')


class SaleOrdersLinePreparation(models.Model):
    _inherit = 'sale.order.line'

    preparation_time = fields.Float("preparation Time", default=lambda self: round(
        float(self.env['ir.config_parameter'].sudo().get_param('website_sale_hour.pickup_time')) * 60))
    preparation_date = fields.Datetime("Preparation Date", default=lambda self: fields.Datetime.now())
    uhc_state = fields.Selection([('preparing', 'Preparing'), ('start', 'Start'),
                                  ('finish', 'Finish')], default='preparing')
    order_line_mark = fields.Boolean('Marked')
    fried_ids = fields.One2many('sale.kitchen.fried.line', 'sale_line_id', string='Fried items')


class MessageLineKitchen(models.Model):
    _name = 'message.kitchen'
    _description = 'Message To Kitchen'

    message = fields.Text('message')
    send = fields.Boolean('send', default=False)
    user_name = fields.Char('User')
    pos_session = fields.Many2one('pos.session')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_fried_product = fields.Boolean(string="Fried product")
    fried_products = fields.Many2many('product.template', 'fried_products_rel', 'src_id1', 'dest_id1',  string="Fried products")
    uhc_products = fields.Many2many('product.template', 'uhc_products_rel', 'src_id', 'dest_id', string="UHC products")


class RecallOrder(models.Model):
    _name = 'recall.order'
    _description = 'Recall Order'

    order_id = fields.Integer()
    type = fields.Selection([('pos', 'Pos'), ('sale', 'Sale')])
    recall_order = fields.Boolean("Recall Order", store=True)


class PosFriedLines(models.Model):
    _name = 'pos.kitchen.fried.line'
    _description = 'Kitchen Fried Lines'

    product_id = fields.Many2one('product.template', string='Product')
    pos_line_id = fields.Many2one('pos.order.line', string='POS order line')


class SaleFriedLines(models.Model):
    _name = 'sale.kitchen.fried.line'
    _description = 'Kitchen Fried Lines'

    product_id = fields.Many2one('product.template', string='Product')
    sale_line_id = fields.Many2one('sale.order.line', string='Sale order line')
