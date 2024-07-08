# -*- coding: utf-8 -*-
from odoo import api, fields, models
import datetime

class ResCompany(models.Model):
    _inherit = 'res.company'

    branch_name = fields.Char(String="Branch Name", help="branch name.")
    branch_code = fields.Char(string="Branch Code", help="It will be used in Order Name for POS")