# -*- coding: utf-8 -*-
from odoo import models,fields


class User(models.Model):
    _inherit = ['res.users']

    user_otp = fields.Char(string="OTP")
    notification=fields.Boolean(string="Enable Notiication")


class Partner(models.Model):
    _inherit = ['res.partner']

    first_name=fields.Char(string='First Name')
    last_name=fields.Char(string='Last Name')