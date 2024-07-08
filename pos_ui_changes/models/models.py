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

class PosCategoryModelInherited(models.Model):
    _inherit = 'pos.category'

    color = fields.Char(string="Color", help="Choose your color")
    hide_in_categories = fields.Boolean()
