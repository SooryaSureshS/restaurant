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


class SaleLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        line = super(SaleLine, self).create(vals)
        if line.order_id.partner_id:
            total = 0
            points = line.order_id.partner_id.loyalty_points
            if line.product_uom_qty > 0:
                total = points + line.product_uom_qty
                line.order_id.partner_id.loyalty_points = total
            else:
                total = points
                line.order_id.partner_id.loyalty_points = total
        return line

    @api.model
    def write(self, vals):
        line = super(SaleLine, self).write(vals)
        if self.order_id.partner_id:
            partner = self.env['res.partner'].sudo().search([('id', '=', self.order_id.partner_id.id)])
            total = 0
            points = self.order_id.partner_id.loyalty_points
            if self.product_uom_qty > 0:
                total = points + self.product_uom_qty
                vals = {'loyalty_points': total}
                partner.sudo().write(vals)
            else:
                pass

        return line
