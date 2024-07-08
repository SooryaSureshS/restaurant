from odoo import models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def ptav_wizard(self):
        rec = self.env['product.attribute.pricelist.wizard'].create({
            'pricelist_id': self.id
        })
        return {
            'type': 'ir.actions.act_window',
            'name': ('PTAV'),
            'res_model': 'product.attribute.pricelist.wizard',
            'res_id': rec.id,
            'view_mode': 'form',
            'target': 'new',
        }
