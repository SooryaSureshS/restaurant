from odoo import fields,models,api,_

class RestaurantFloor(models.Model):
    _inherit = "restaurant.floor"

    def open_wizard(self):
        context = self.env.context.copy()
        context.update({'floor_ids': self.ids})
        view_id = self.env.ref('pos_floor_table.floor_pos_view_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Floor Select'),
            'res_model': 'pos.floor.table',
            'target': 'new',
            'view_mode': 'form',
            'views': [[view_id, 'form']],
            'context': context,
        }