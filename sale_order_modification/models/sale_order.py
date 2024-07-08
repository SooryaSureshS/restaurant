# -*- coding: utf-8 -*-

from odoo import models, fields, api
import phonenumbers, re


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    email = fields.Char('Email')
    phone = fields.Char('Phone')

    def action_confirm(self):

        res = super(SaleOrder, self).action_confirm()
        for order in self:

            if order.public_partner.phone:
                digits = order.public_partner.phone
                rule = re.compile(r'^(?:\+?61)?[07]\d{9,13}$')
                if not rule.search(digits):
                    my_number = phonenumbers.parse(digits, "AU")
                    international_f = phonenumbers.format_number(my_number,
                                                                 phonenumbers.PhoneNumberFormat.INTERNATIONAL)

                    order.phone = international_f
                    order.public_partner.phone = international_f

            else:
                pass

            if order.public_partner.email:
                order.email = order.partner_id.email

        # partner_obj = order.partner_id
        # partner_obj.write({'phone': [order.phone]})

        return res


    @api.model
    def create(self, vals):
        orders = super(SaleOrder, self).create(vals)
        # sale_order = self.env['sale.order'].sudo().search([('website_delivery_type', '!=', 'delivery')])
        for lines in orders.filtered(
                lambda order: order.website_delivery_type != 'delivery' and order.state != "sale"):
            delivery_line = lines.order_line.filtered(lambda line: line.product_id.type == 'service' and \
                                                                   line.product_id.default_code == 'Delivery_007')
            if delivery_line:
                delivery_line.sudo().unlink()
        return orders
