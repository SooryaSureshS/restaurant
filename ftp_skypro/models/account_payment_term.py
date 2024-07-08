from odoo import models, api, fields


class AccountPaymentTermInherit(models.Model):
    _inherit = 'account.payment.term'

    english_explanation = fields.Char()
    chinese_explanation = fields.Char()
    code = fields.Char()
