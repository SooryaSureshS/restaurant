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


class PosConfigOpenorder(models.Model):
    _inherit = 'pos.config'

    open_order = fields.Boolean()


class PosOrderFetchingInherited(models.Model):
    _inherit = 'pos.order'

    open_order_ref = fields.Char(string="Open Order Ref",help="Choose your color")
    order_parse_json = fields.Char(string="Open Order Ref",help="Choose your color")
    old_order_reference = fields.Char()
    delivery_type = fields.Selection(selection_add=[('phone', 'Phone')])


    @api.model
    def get_pos_open_order(self,session_id):
        orders = self.search([('session_id','=', session_id),('state','=','draft'),('delivery_type','in',['phone'])])
        list_order = []
        for i in orders:
            data = {
                'name': i.name,
                'partner_id': [i.partner_id.id or False, i.partner_id.name or False],
                'date_order': i.date_order,
                'amount_total': i.amount_total,
                'amount_tax': i.amount_tax,
                'pos_reference': i.pos_reference,
                'lines': i.lines,
                'state': i.state,
                'session_id': i.session_id.id,
                'company_id': i.company_id.id,
                'return_ref': i.return_ref,
                'return_status': i.return_status,
                'id': i.id,
                'delivery_type': i.delivery_type,
                'table_name': i.table_name
            }
            list_order.append(data)
        return list_order

    @api.model
    def get_pos_open_order_by_id(self, order, context):
        orders = self.search([('id', '=', order)],limit=1)
        return self._export_for_ui_opened(orders, context)

    def _export_for_ui_opened(self, order, context):
        print(context,"context")
        timezone = pytz.timezone(context.get('tz') or self.env.user.tz or 'UTC')
        return {
            'lines': [line for line in order.lines.export_for_ui()],
            'orderlines': [],
            'statement_ids': [],
            'name': order.pos_reference,
            'uid': order.pos_reference[6:],
            'amount_paid': order.amount_paid,
            'amount_total': order.amount_total,
            'amount_tax': order.amount_tax,
            'amount_return': order.amount_return,
            'pos_session_id': order.session_id.id,
            'is_session_closed': order.session_id.state == 'closed',
            'pricelist_id': order.pricelist_id.id,
            'partner_id': order.partner_id.id,
            'user_id': order.user_id.id,
            'sequence_number': order.sequence_number,
            'creation_date': order.date_order.astimezone(timezone),
            'fiscal_position_id': order.fiscal_position_id.id,
            'to_invoice': order.to_invoice,
            'state': order.state,
            'account_move': order.account_move.id,
            'id': order.id,
            'is_tipped': order.is_tipped,
            'tip_amount': order.tip_amount,
            'table': order.table_id.id or False,
            'delivery_type': order.delivery_type or False
        }

    # def _order_fields(self, ui_order):
    #     order = super(PosOrderFetchingInherited, self)._order_fields(ui_order)
    #     print("ordereee", ui_order)
    #     # old_order_ref = ui_order.get('open_order_ref')
    #     open_order_id = ui_order.get('open_order_id')
    #     current_order_ref = ui_order.get('name')
    #     open_order_ref = ui_order.get('open_order_ref', False)
    #     print("QQQQQQQQQQQQq", open_order_ref)
    #     if open_order_ref:
    #         old_order = self.search([('id','=',int(open_order_id))])
    #         if old_order:
    #             product_dict = {}
    #             for line in old_order.lines:
    #                 product_dict[line.product_id.id] = line.order_line_state
    #             product_dict_key = product_dict.keys()
    #             # for rec in order:
    #             if order.get('lines', False):
    #                 for r in order.get('lines', False):
    #                     e_line = r[2]
    #                     if e_line.get('product_id') in product_dict_key:
    #                         e_line['order_line_state'] = product_dict.get(e_line.get('product_id'))
    #             # try:
    #             #     old_order.unlink()
    #             # except:
    #             #     pass
    #             # self.env.cr.commit()
    #             # except:
    #             #     pass
    #     return order


    @api.model
    def create_from_ui(self, orders, draft=False):
        """ Create and update Orders from the frontend PoS application.

        Create new orders and update orders that are in draft status. If an order already exists with a status
        diferent from 'draft'it will be discareded, otherwise it will be saved to the database. If saved with
        'draft' status the order can be overwritten later by this function.

        :param orders: dictionary with the orders to be created.
        :type orders: dict.
        :param draft: Indicate if the orders are ment to be finalised or temporarily saved.
        :type draft: bool.
        :Returns: list -- list of db-ids for the created and updated orders.
        """
        order_ids = []
        for order in orders:
            existing_order = False
            if 'server_id' in order['data']:
                existing_order = self.env['pos.order'].search(['|', ('id', '=', order['data']['server_id']), ('pos_reference', '=', order['data']['name'])], limit=1)
            if (existing_order and existing_order.state == 'draft') or not existing_order:
                open_order_id = order['data'].get('open_order_id',False)
                if open_order_id:
                    existing_order = self.search([('id', '=', int(open_order_id))])
                    if existing_order:
                        order['data']['name']=existing_order.pos_reference
                        order['data']['uid']=existing_order.pos_reference
                        order['data']['sequence_number']=existing_order.sequence_number
                order_ids.append(self._process_order(order, draft, existing_order))
        return self.env['pos.order'].search_read(domain = [('id', 'in', order_ids)], fields = ['id', 'pos_reference'])