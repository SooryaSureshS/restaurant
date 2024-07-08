from odoo import fields,models,api


class POSFloorTable(models.TransientModel):
    _name = 'pos.floor.table'

    pos_config_ids = fields.Many2one('pos.config', string="POS Config")

    def set_floor_pos(self):
        floor_list = self._context.get('floor_ids')
        floor_ids = self.env['restaurant.floor'].sudo().search([('id','in',floor_list)])
        for floor in floor_ids:
            if floor.pos_config_id.id != self.pos_config_ids.id:
                new_floor_dict = floor.copy_data()[0]
                new_floor_dict.update({
                    'pos_config_id':self.pos_config_ids.id
                })
                new_floor_id = self.env['restaurant.floor'].sudo().create(new_floor_dict)
                for table in floor.table_ids:
                    new_table_id = table.copy()
                    new_table_id['floor_id'] = new_floor_id.id
