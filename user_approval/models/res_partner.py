from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    shop = fields.Char()
    business_registration = fields.Binary()
