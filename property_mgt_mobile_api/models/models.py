# -*- coding: utf-8 -*-

from odoo import models, fields


class UsersInherit(models.Model):
    _inherit = 'res.users'

    user_otp = fields.Char(default="")

