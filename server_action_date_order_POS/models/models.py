# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields, _
from odoo.http import request
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderNewInherited(models.Model):
    _inherit = "pos.order"

    # date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")


    def action_change_date_POS(self):

        # for order in self:
        #     print("ssssssss",order)
        #     order.write({
        #         'date_order': '2021-10-10'
        #     })
        # return
        #     order._portal_ensure_token()
        composer_form_view_id = self.env.ref('server_action_date_order_POS.change_pos_date_order').id
        #
        # template_id = self._get_cart_recovery_template().id
        #
        list_sale = []
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'dateorder.report.pos',
            'view_id': composer_form_view_id,
            'target': 'new',
            'context': {
                'default_sale': self.ids,
                'active_ids': self.ids,
            },
        }

from odoo import models, fields, _, api


class OperationalReportWizardDateOrders(models.TransientModel):
    _name = "dateorder.report.pos"

    date_orders_trans = fields.Datetime(string="select date")
    sale = fields.Char()

    def print_report_date(self):
        if self.date_orders_trans:
            for i in self.sale.strip('][').split(', '):
                orders = self.env['pos.order'].search([('id','=',int(i))],limit=1)
                for order in orders:
                    order.write({
                        'date_order': self.date_orders_trans,
                    })