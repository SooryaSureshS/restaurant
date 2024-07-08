from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError


class UberConfig(models.Model):
    _name = 'uber.config'
    name = fields.Char('Uber Name')
    client_id = fields.Char("Client ID")
    client_secret = fields.Char('Client Secret')
    pos_session = fields.Many2one('pos.session',domain="[('state','=','opened')]")

