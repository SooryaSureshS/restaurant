# -*- coding: utf-8 -*-
from odoo import models,fields


class CompanyInherit(models.Model):
    _inherit = 'res.company'

    policy=fields.Text('Privacy Policy')
    about_us=fields.Text('Contact Us')
    payment_delivery=fields.Text('Payment Delivery')


