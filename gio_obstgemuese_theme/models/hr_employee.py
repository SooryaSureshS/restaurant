# Company: giordano.ch AG
# Copyright by: giordano.ch AG
# https://giordano.ch/

from odoo import fields, models


class MailingContact(models.Model):
    _inherit = "hr.employee"

    is_website = fields.Boolean(string="Is On Website")
    website_order = fields.Integer(string="Website Order")

