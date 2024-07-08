from odoo import models, api, fields


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    upload_your_image_tiff = fields.Binary()
    product_pack_image_tiff = fields.Binary()
    packaging_image_tiff = fields.Binary()
    product_carton_image_tiff = fields.Binary()
    carton_packaging_image_tiff = fields.Binary()