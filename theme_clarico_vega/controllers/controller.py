from datetime import datetime
from operator import itemgetter
from timeit import itertools
from itertools import groupby
from datetime import date
from odoo import http, api, fields, models, _
import datetime
from datetime import date
from dateutil import relativedelta
from datetime import timedelta
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class AddToCartProduct(WebsiteSale):

    @http.route('/shop/cart/quantity/custom', website=True, csrf=False, type='json', auth="public")
    def shop_cart_qty_custome(self):
        return request.website.sale_get_order().cart_quantity

    @http.route('/shop/cart/update/order', website=True, csrf=False, type='json', auth="public")
    def add_to_cart(self, product_id, add_qty, **kw):
        try:
            sale_order = request.website.sale_get_order(force_create=True)
            if sale_order.state != 'draft':
                request.session['sale_order_id'] = None
                sale_order = request.website.sale_get_order(force_create=True)
            product_product_id = request.env['product.product'].sudo().search([('product_tmpl_id.id', '=', product_id)],
                                                                              limit=1)
            produt_order_line = sale_order.order_line.filtered(lambda o: o.product_id.id == product_product_id.id)
            if produt_order_line:
                produt_order_line[0].product_uom_qty = produt_order_line[0].product_uom_qty + 1
            else:
                new_line = request.env['sale.order.line'].sudo().create({
                    'product_id': int(product_product_id.id),
                    'name': product_product_id.name,
                    'product_uom_qty': 1,
                    'price_unit': product_product_id.lst_price,
                    'order_id': sale_order.id
                })

            return True
        except:
            return False

    @http.route()
    def address(self, **kw):
        """
            Handle requests related to the customer's address.
            Args:
                **kw: A dictionary containing any additional keyword arguments passed to the function.
            Returns:
                A response object with the customer's address details, or a redirect to the checkout page if this is a
                POST request and the response is a redirection.
            """
        res = super(AddToCartProduct, self).address(**kw)
        if request.httprequest.method == "POST" and res.status_code == 303:
            return request.redirect('/shop/checkout')
        return res
