from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    docket_category_break = fields.Boolean('Enable Docket Category Break')
