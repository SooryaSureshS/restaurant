# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

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
class PosConfigRecall(models.Model):
    _inherit = 'pos.config'

    recall_orders = fields.Boolean(string='Recall Orders', help='Allow the Recall.')
