# -*- coding: utf-8 -*-
from datetime import datetime, date
from dateutil import relativedelta
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import pytz


class PurchaseFilterWizzard(models.TransientModel):
    _name = 'purchase.filter.wizard'

    date_from = fields.Datetime(string="start date",)
    date_to = fields.Datetime(string="end date",)
    product_name = fields.Char(string="Product Name",)
    product_specific_filter = fields.Boolean(string="Product Specific Filter")
    purchased_on_bool = fields.Boolean(string="Purchased on b")
    purchased_on = fields.Datetime(string="Purchased on")

    @api.onchange('product_specific_filter')
    def change_boolean_product_specific_filter(self):
        if self.product_specific_filter:
            self.purchased_on_bool = False

    @api.onchange('purchased_on_bool')
    def change_boolean_purchased_on_bool(self):
        if self.purchased_on_bool:
            self.product_specific_filter = False

    @api.onchange('date_from,date_to')
    def validation_date(self):
        if self.date_from > self.date_to:
            raise ValidationError(_('end date should be greater than start date'))
        if self.date_from > datetime.now():
            raise ValidationError(_(' future dates are not allowed '))
        if self.date_to > datetime.now():
            raise ValidationError(_(' future dates are not allowed '))

    def action_apply(self):
        if self.product_specific_filter:
            rec = self.env['res.partner'].search([('sale_order_ids.order_line.product_id.name', 'ilike', self.product_name),
                                                  ('sale_order_ids.date_order', '>=', self.date_from),
                                                  ('sale_order_ids.date_order', '<=', self.date_to)])
            val = [x.id for x in rec]
        if self.purchased_on_bool:
            rec = self.env['res.partner'].search([('sale_order_ids.date_order', '=', self.purchased_on)])
            val = [x.id for x in rec]
        return {
            'type': 'ir.actions.act_window',
            'name': 'product purchase filter',
            'view_mode': 'tree',
            'domain': [('id', 'in', val)],
            'view_id': self.env.ref('base.view_partner_tree').id,
            'res_model': 'res.partner',
            'target': 'current',
        }
