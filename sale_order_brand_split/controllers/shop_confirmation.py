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
            brand_order_split = request.env[
                'ir.config_parameter'].sudo().search(
                [('key', '=',
                  'sale_order_brand_split.brand_order_split')],
                limit=1).value
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if order and brand_order_split:
                order.split_order()
            split_order = [order.id]
            if order.split_order_ids:
                for split in order.split_order_ids:
                    split_order.append(split.id)
                order_object = request.env['sale.order'].sudo().browse(
                    split_order)
                return request.render("website_sale.confirmation",
                                      {'order': order_object,
                                       'split': len(split_order)})
        return response

    @http.route(['/shop/print/<int:line_id>'], type='http', auth='public',website=True,)
    def print_sale_order(self, line_id=None, **kwargs):
        if line_id:
            pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                'sale.action_report_saleorder', [line_id])
            pdfhttpheaders = [('Content-Type', 'application/pdf'),
                              ('Content-Length', u'%s' % len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.redirect('/shop')
