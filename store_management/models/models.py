from odoo import fields, models, api, _


class POSProgram(models.Model):
    _inherit = 'res.partner'

    primary_store = fields.Many2one('primary.store', string="Primary Store")


class StoreData(models.Model):
    _name = 'primary.store'

    name = fields.Char("Name")
    id = fields.Char("Value")


class Website(models.Model):
    _inherit = "website"

    @api.model
    def get_store_data(self):
        stores = self.env["primary.store"].sudo().search([])
        return stores
