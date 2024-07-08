# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockMoveExt(models.Model):
    _inherit = 'stock.scrap'

    user_id = fields.Many2one('res.users', 'Users')