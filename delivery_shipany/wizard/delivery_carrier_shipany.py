from odoo import fields, models


class ShipAnyCarrierType(models.TransientModel):
    _name = "delivery.carrier.shipany"
    _description = "Carrier Type"

    carrier_type = fields.Many2one('shipany.carrier', string="Carrier Type")
    delivery_carrier_id = fields.Many2one('delivery.carrier')

    # Select Carrier Type
    def action_validate(self):
        if self.carrier_type:
            parent_id = self.env.context.get('active_id')
            delivery_obj = self.env['delivery.carrier'].search([('id', '=', parent_id)])
            if delivery_obj:
                delivery_obj.write({
                    'shipany_delivery_type': self.carrier_type.id
                })
