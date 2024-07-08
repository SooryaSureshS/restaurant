from odoo import models, fields


class CustappConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    cod_available = fields.Selection([
        ('on', 'On'),
        ('off', 'Off')
    ], string="COD Available", readonly=False)

    def get_values(self):
        res = super(CustappConfig, self).get_values()
        res.update(
            cod_available=self.env['ir.config_parameter'].sudo().get_param(
                'umami_mobile.cod_available'),
        )
        return res

    def set_values(self):
        super(CustappConfig, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        cod_available = self.cod_available
        param.set_param('umami_mobile.cod_available', cod_available)
