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
from datetime import date


class WebsiteDeliveryTypeInherited(models.Model):
    _inherit = 'sale.order'


    checkout_note = fields.Char(string="Checkout Note")