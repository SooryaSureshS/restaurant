from odoo import fields, models


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order.line'

    mask_image = fields.Binary(string='Mask Image')
    print_area = fields.Selection([('logo', 'Logo'), ('full', 'Full'), ('adult', 'Adult')])
    with_nose_pad = fields.Boolean('With nose pad', default=False)
