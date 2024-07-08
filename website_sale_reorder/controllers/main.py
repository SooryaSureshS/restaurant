# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class WebSaleOrderRepeat(http.Controller):

    @http.route('/myorder/repeat', type='http', auth="public", website=True)
    def repeat_sale_order(self, **kwargs):
        order_id = kwargs.get('id')
        repeat_order_id = request.env['sale.order'].sudo().browse(
            int(order_id))
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        add_qty = 0
        set_qty = 0
        for line1 in repeat_order_id.order_line:
            if line1.product_id.filtered(lambda line: line.type != 'service' and \
                                            line.default_code != 'Delivery_007'):
                if sale_order.order_line:
                    for line2 in sale_order.order_line:
                        if line2.product_id == line1.product_id:
                            add_qty = line1.product_uom_qty + line2.product_uom_qty
                            set_qty = add_qty
                            break
                        else:
                            add_qty = line1.product_uom_qty
                            set_qty = add_qty
                else:
                    add_qty = line1.product_uom_qty
                    set_qty = add_qty

                sale_order._cart_update(
                    product_id=int(line1.product_id.id),
                    add_qty=add_qty,
                    set_qty=set_qty,
                )
        return request.redirect("/shop/cart")

