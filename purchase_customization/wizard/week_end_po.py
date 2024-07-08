# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class WeekEndWizard(models.TransientModel):
    _name = "week.end.wizard"
    _description = "week end po"

    def _default_po_line(self):
        product_ids = self.env['product.product'].sudo().search([('type', '=', 'product')])
        po_list = []
        for product_id in product_ids:
            new_datetime = datetime.now() + timedelta(weeks=-6)
            total_order_qty = sum(self.env['stock.move'].sudo().search([
                ('product_id', 'in', product_id.ids),
                ('picking_type_id.code', '=', 'outgoing'),
                ('date', '>=', new_datetime),
                ('state', 'not in', ['cancel'])
            ]).mapped('product_uom_qty'))
            val = {
                'product_tmpl_id': product_id.product_tmpl_id.id,
                'product_id': product_id.id,
                'partner_id': product_id.seller_ids[0].name.id if product_id.seller_ids else False,
                'qty': round(total_order_qty / 6),
                'purchase_qty': round(total_order_qty / 6)
            }
            def_extra_percentage = 10
            if def_extra_percentage:
                ex_total = (def_extra_percentage * val.get('purchase_qty')) / 100
                qty_purchase_qty = round(val.get('purchase_qty') + ex_total)
                val.update({'purchase_qty': qty_purchase_qty})
            po_list.append((0, 0, val))
        return po_list

    week_end_product_ids = fields.One2many('week.end.po', 'wizard_id', string='week end po', default=_default_po_line)

    def create_week_end_products(self):
        for i in self.week_end_product_ids:
            if not i.purchase_qty:
                raise UserError(_("Purchase quantity should be greater than 0 on %s product line.")%i.product_tmpl_id.name)
            if not i.partner_id:
                raise UserError(_("Set vendor on %s product line.")%i.product_tmpl_id.name)
        for i in self.week_end_product_ids:
            i.create_po_order()

class WeekEndPo(models.TransientModel):
    _name = "week.end.po"
    _description = "week end po"

    wizard_id = fields.Many2one('week.end.wizard', string='Wizard', ondelete='cascade') #required=True,
    product_tmpl_id = fields.Many2one('product.template', string='Product Template') #required=True,
    product_id = fields.Many2one('product.product', string='Product')
    partner_id = fields.Many2one('res.partner', string='Vendor') #required=True,
    extra_percentage = fields.Float('Extra %', default=10, digits=(16, 2))
    qty = fields.Float('Qty', digits="Product Unit Of Measure") #required=True,
    purchase_qty = fields.Float('Purchase Quantity', digits="Product Unit Of Measure") #required=True,
    purchase_uom = fields.Many2one('uom.uom', 'Unit of Measure', related='product_tmpl_id.uom_po_id')

    @api.onchange('qty')
    def _onchange_qty(self):
        self.purchase_qty = self.qty

    @api.onchange('extra_percentage')
    def _onchange_extra_percentage(self):
        if self.extra_percentage:
            ex_total = (self.extra_percentage * self.qty) / 100
            self.purchase_qty = round(self.qty + ex_total)
        else:
            self.purchase_qty = round(self.qty)

    def create_po_order(self):
        if self.purchase_qty:
            purchase_order = self.env['purchase.order'].create({'partner_id': self.partner_id.id})
            purchase_order.onchange_partner_id()
            purchase_order_line = self.env['purchase.order.line'].create({
                'name': self.product_tmpl_id.product_variant_id.name,
                'product_id': self.product_tmpl_id.product_variant_id.id,
                'product_qty': self.purchase_qty,
                'product_uom': self.product_tmpl_id.product_variant_id.uom_id.id,
                'price_unit': self.product_tmpl_id.product_variant_id.list_price,
                'order_id': purchase_order.id,
                'taxes_id': False,
            })
            purchase_order_line.onchange_product_id()
            purchase_order_line.product_qty = self.purchase_qty
            if not self.product_id:
                return {
                    'name': _('Purchase Request'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'purchase.order',
                    'res_id': purchase_order.id,
                    'context': self.env.context
                }
        else:
            raise UserError(_("Purchase quantity should be greater than 0."))
