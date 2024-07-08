
from odoo import models, fields, api


class SaleConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_busy_banner = fields.Boolean('Enable Busy Banner', default=True)
    busy_banner_display = fields.Float('Busy Banner Time', default=30.00)
    banner_title = fields.Char('Banner Title', default="HI")
    banner_body = fields.Char('Banner Body Message', default="Our kitchen is busy at this time and orders may be longer than expected")
    popup_timing = fields.Integer('Pop up Timing in min', default=5)


    def get_values(self):
        res = super(SaleConfig, self).get_values()
        res.update(
            busy_banner_display=self.env['ir.config_parameter'].sudo().get_param(
                'busy_banner.busy_banner_display'),
        )
        res.update(
            enable_busy_banner=self.env['ir.config_parameter'].sudo().get_param(
                'busy_banner.enable_busy_banner'),
        )
        res.update(
            banner_title=self.env['ir.config_parameter'].sudo().get_param(
                'busy_banner.banner_title'),
        )
        res.update(
            banner_body=self.env['ir.config_parameter'].sudo().get_param(
                'busy_banner.banner_body'),
        )
        res.update(
            popup_timing=self.env['ir.config_parameter'].sudo().get_param(
                'busy_banner.popup_timing'),
        )
        return res

    def set_values(self):
        super(SaleConfig, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        busy_banner_display = self.busy_banner_display
        enable_busy_banner = self.enable_busy_banner
        banner_title = self.banner_title
        banner_body = self.banner_body
        popup_timing = self.popup_timing
        param.set_param('busy_banner.busy_banner_display', busy_banner_display)
        param.set_param('busy_banner.enable_busy_banner', enable_busy_banner)
        param.set_param('busy_banner.banner_title', banner_title)
        param.set_param('busy_banner.banner_body', banner_body)
        param.set_param('busy_banner.popup_timing', popup_timing)
