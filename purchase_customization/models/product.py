# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, _


class ProductTemplatePo(models.Model):
    _inherit = "product.template"

    def create_week_end_po(self):
        new_datetime = datetime.now() + timedelta(weeks=-6)
        total_order_qty = sum(self.env['stock.move'].sudo().search([
            ('product_id', 'in', self.product_variant_id.ids),
            ('picking_type_id.code', '=', 'outgoing'),
            ('date', '>=', new_datetime),
            ('state', 'not in', ['cancel'])
        ]).mapped('product_uom_qty'))
        context = self.env.context.copy()
        context.update({'default_partner_id': self.seller_ids[0].name.id if self.seller_ids else False,
                        'default_product_tmpl_id': self.id,
                        'default_qty': round(total_order_qty / 6)})
        view = self.env.ref('purchase_customization.view_week_end_po_form')
        return {
            'name': _('Create PR'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'week.end.po',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context
        }


class ProductProductPo(models.Model):
    _inherit = "product.product"

    def create_week_end_po(self):
        new_datetime = datetime.now() + timedelta(weeks=-6)
        total_order_qty = sum(self.env['stock.move'].sudo().search([
            ('product_id', 'in', self.ids),
            ('picking_type_id.code', '=', 'outgoing'),
            ('date', '>=', new_datetime),
            ('state', 'not in', ['cancel'])
        ]).mapped('product_uom_qty'))
        context = self.env.context.copy()
        context.update({'default_partner_id': self.seller_ids[0].name.id if self.seller_ids else False,
                        'default_product_tmpl_id': self.product_tmpl_id.id,
                        'default_qty': round(total_order_qty / 6)})
        view = self.env.ref('purchase_customization.view_week_end_po_form')
        return {
            'name': _('Create PR'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'week.end.po',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context
        }
