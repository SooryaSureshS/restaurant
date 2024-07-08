from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    session_sync_timeout = fields.Integer('Session sync timeout', default=5)
