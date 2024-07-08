from odoo import fields, models, api, _


class POSProgram(models.Model):
    _inherit = 'product.template'

    disable_print = fields.Boolean("Disable KVS Receipt Print")

