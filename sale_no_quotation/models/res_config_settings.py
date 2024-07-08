from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    website_sale_no_quotation = fields.Boolean(default=True)

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        config_params = self.env['ir.config_parameter'].sudo()
        config_params.set_param('sale_no_quotation.website_sale_no_quotation', self.website_sale_no_quotation)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_params = self.env['ir.config_parameter'].sudo()
        website_sale_no_quotation = config_params.get_param('sale_no_quotation.website_sale_no_quotation')
        res.update(website_sale_no_quotation=website_sale_no_quotation)
        return res
