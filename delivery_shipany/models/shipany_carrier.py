from odoo import models, fields


class ShipAnyCarrier(models.Model):
    _name = 'shipany.carrier'

    name = fields.Char(string="Carrier Name")
    carrier_uid = fields.Char(string="Carrier UID", help="Stores UID of Shipany Carriers")
