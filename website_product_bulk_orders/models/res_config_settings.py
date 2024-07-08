from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_bulk_order = fields.Boolean("Product Bulk Order")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        config_params = self.env['ir.config_parameter'].sudo()
        config_params.set_param('website_product_bulk_orders.product_bulk_order', self.product_bulk_order)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_params = self.env['ir.config_parameter'].sudo()
        product_bulk_order = config_params.get_param('website_product_bulk_orders.product_bulk_order')
        res.update(product_bulk_order=product_bulk_order)
        return res

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     google_provider = self.env.ref('auth_oauth.provider_google', False)
    #     if google_provider:
    #         res.update(
    #             auth_oauth_google_enabled=google_provider.enabled,
    #             auth_oauth_google_client_id=google_provider.client_id,
    #             server_uri_google=self.get_uri())
    #     return res
    #
    # def set_values(self):
    #     super().set_values()
    #     google_provider = self.env.ref('auth_oauth.provider_google', False)
    #     if google_provider:
    #         google_provider.write({
    #             'enabled': self.auth_oauth_google_enabled,
    #             'client_id': self.auth_oauth_google_client_id,
    #         })
