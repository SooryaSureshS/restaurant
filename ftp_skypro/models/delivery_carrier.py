from odoo import models, api, fields


class DeliveryCarrierInherit(models.Model):
    _inherit = 'delivery.carrier'

    english_explanation = fields.Char()
    chinese_explanation = fields.Char()
    code = fields.Char()
