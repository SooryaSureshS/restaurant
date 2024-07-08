# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleInherit(WebsiteSale):

    @http.route('/shop/confirmation', type='http', auth="public", website=True)
    def shop_payment_confirmation(self, **post):
        response = super(WebsiteSaleInherit, self).shop_payment_confirmation(
            **post)
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            website_sale_no_quotation = request.env['ir.config_parameter'].sudo().search(
                [('key', '=',
                  'sale_no_quotation.website_sale_no_quotation')],
                limit=1).value
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if order.state == 'sent' and website_sale_no_quotation:
                order.action_confirm()
        return response
