# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PosConfig(models.Model):
    _inherit = "pos.config"    
   
    
    custom_theme=fields.Selection([('custom1', 'Default'), ('custom2', 'Theme 1'),('custom3', 'Theme 2'),('custom4', 'Theme 3'),('custom5', 'Theme 4'),
                                   ('custom6', 'Theme 5'),('custom7', 'Theme 6'),('custom8', 'Theme 7')],
                        default='custom1', required=True)
    theme=fields.Boolean("theme",compute="set_ui_theme")

    def set_ui_theme(self):
        default=self.env.ref('pos_ui_theme.default')
        theme1_id=self.env.ref('pos_ui_theme.theme1')
        theme2_id=self.env.ref('pos_ui_theme.theme2')
        theme3_id=self.env.ref('pos_ui_theme.theme3')
        theme4_id=self.env.ref('pos_ui_theme.theme4')
        theme5_id=self.env.ref('pos_ui_theme.theme5')
        theme6_id=self.env.ref('pos_ui_theme.theme6')
        theme7_id=self.env.ref('pos_ui_theme.theme7')
        for pos_config in self:
            if pos_config.custom_theme == 'custom1':
                default.write({'active': True})
            else:
                default.write({'active': False})
            if pos_config.custom_theme == 'custom2':
                theme1_id.write({'active': True})            
            else:
                theme1_id.write({'active': False})
            if pos_config.custom_theme == 'custom3':
                theme2_id.write({'active': True})            
            else:
                theme2_id.write({'active': False})
            if pos_config.custom_theme == 'custom4':
                theme3_id.write({'active': True})            
            else:
                theme3_id.write({'active': False})
            if pos_config.custom_theme == 'custom5':
                theme4_id.write({'active': True})            
            else:
                theme4_id.write({'active': False})
            if pos_config.custom_theme == 'custom6':
                theme5_id.write({'active': True})            
            else:
                theme5_id.write({'active': False})
            if pos_config.custom_theme == 'custom7':
                theme6_id.write({'active': True})            
            else:
                theme6_id.write({'active': False})
            if pos_config.custom_theme == 'custom8':
                theme7_id.write({'active': True})            
            else:
                theme7_id.write({'active': False})
        self.theme = True
                
                