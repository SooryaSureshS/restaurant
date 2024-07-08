# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class res_users(models.Model):
    _inherit = "res.users"
    pos_delete_order = fields.Boolean(
        'Delete POS Orders',
        default=0)
    pos_security_pin = fields.Integer(
        string='POS Security PIN',
        help='A Security PIN used to protect sensible functionality in the Point of Sale')