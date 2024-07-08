# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError


class PosLine(models.Model):
    _inherit = 'pos.order'

    lines = fields.One2many('pos.order.line', 'order_id', string='Order Lines', states={'draft': [('readonly', False)]},
                            readonly=False, copy=True)
    edit_line = fields.Boolean(string="Edit", compute='_edit_line')

    def _edit_line(self):
        for record in self:
            if self.env.user.has_group("pos_order_lines_inherit.group_pos_order_line_edit"):
                record.edit_line = True
            else:
                record.edit_line = False
