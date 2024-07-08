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
from odoo.exceptions import ValidationError



# Enable this checkbox for using kitchen screen


_logger = logging.getLogger(__name__)

class PosConfigPublHoliday(models.Model):
    _inherit = 'pos.config'

    iface_holiday = fields.Boolean(string='Kitchen Order', help='Allow the Kitchen Order.')
    surcharge_product = fields.Many2one('product.product',string='Surcharge', help='Surcharge Product.')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='Start Date')
    pricing_method = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')], default='percentage')
    amount = fields.Float(string='Amount/percentage')

    @api.onchange('pricing_method')
    def _onchange_pricing_methods(self):
        self.amount = False

    @api.constrains('iface_holiday', 'end_date', 'start_date', 'choose_price', 'percentage', 'amount')
    def end_date_checking(self):
        if self.iface_holiday is True:
            if not self.start_date:
                raise ValidationError(
                    _("Please choose start date"))
            if not self.end_date:
                raise ValidationError(
                    _("Please choose end date"))
            if self.start_date > self.end_date:
                raise ValidationError(
                    _("End date must be greater than the start date"))
            if (self.end_date - self.start_date).days >= 365:
                raise ValidationError(
                    _("Maximum available period is 1 year."))
            if not self.pricing_method:
                raise ValidationError(
                    _("Please choose a price method"))
            if self.pricing_method == 'percentage':
                if self.amount <= 0:
                    raise ValidationError(
                        _("Amount value must be greater than 0"))
            if self.pricing_method == 'amount':
                if self.amount <= 0:
                    raise ValidationError(
                        _("Amount value must be greater than 0"))
