from odoo import models,fields


# This class is used to store the Locations(Locker)
class ServiceLocations(models.Model):
    _name = 'shipany.service.locations'
    _rec_name = 'cour_name'

    url = fields.Char(string="URL")
    cour_type = fields.Char(string="Courier type")
    cour_uid = fields.Char(string="Courier UID")
    cour_name = fields.Char(string="Courier Name")
    stock_picking_id = fields.Many2one('stock.picking',string="Stock Picking ID")
