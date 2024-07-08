# -*- coding: utf-8 -*-

from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    brand_order_split = fields.Boolean(default=True)

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        config_params = self.env['ir.config_parameter'].sudo()
        config_params.set_param('sale_order_brand_split.brand_order_split',
                                self.brand_order_split)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_params = self.env['ir.config_parameter'].sudo()
        brand_order_split = config_params.get_param(
            'sale_order_brand_split.brand_order_split')
        res.update(brand_order_split=brand_order_split)
        return res
