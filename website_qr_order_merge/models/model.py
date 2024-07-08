from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class SaleConfigWebsiteQr(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_qr_code_merge = fields.Boolean("Enable Qr Order Merge")
    qr_code_merge_time = fields.Float("Qr Merge Code", default=2.00)
    kvs_display_time = fields.Float("KVS Display Time", default=0.00)


    def get_values(self):
        res = super(SaleConfigWebsiteQr, self).get_values()
        res.update(
            enable_qr_code_merge=self.env['ir.config_parameter'].sudo().get_param(
                'website_qr_order_merge.enable_qr_code_merge'),
            qr_code_merge_time=self.env['ir.config_parameter'].sudo().get_param(
                'website_qr_order_merge.qr_code_merge_time'),
            kvs_display_time=self.env['ir.config_parameter'].sudo().get_param(
                'website_qr_order_merge.kvs_display_time')

        )
        return res

    def set_values(self):
        super(SaleConfigWebsiteQr, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        enable_qr_code_merge = self.enable_qr_code_merge
        qr_code_merge_time = self.qr_code_merge_time
        kvs_display_time = self.kvs_display_time
        param.set_param('website_qr_order_merge.enable_qr_code_merge', enable_qr_code_merge)
        param.set_param('website_qr_order_merge.qr_code_merge_time', qr_code_merge_time)
        param.set_param('website_qr_order_merge.kvs_display_time', kvs_display_time)


class SaleWebsiteQrNewMerge(models.Model):

    _name = 'sale.merge'
    _description = 'Sale Order Merge'

    name = fields.Char()
    order = fields.Many2one('sale.order', string='Sale Order')
    # merge_time = fields.Many2one

class SaleWebsiteQrMegeInherit(models.Model):

    _inherit = 'sale.order'

    parent_id = fields.Many2one('sale.order', string='Sale order', index=True)
    merge_order = fields.Boolean(string='Merged Order')
    # rel_child = fields.Many2one('sale.order')




