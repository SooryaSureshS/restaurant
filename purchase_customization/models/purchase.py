# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'PR'),
        ('sent', 'PR Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft',
        tracking=True)

    @api.constrains('order_line')
    def _check_order_line_constrainst(self):
        for rec in self:
            for line in rec.order_line.filtered(lambda x: x.product_id and x.product_id.seller_ids):
                supplier_info_id = line.product_id.seller_ids.filtered(
                    lambda x: x.name and x.name.id == rec.partner_id.id and x.min_qty > line.product_qty)
                if supplier_info_id:
                    raise ValidationError(_("You can order minimum quantity %s of %s from %s." % (
                    supplier_info_id[0].min_qty, line.product_id.name, rec.partner_id.name)))
