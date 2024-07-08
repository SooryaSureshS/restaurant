# -*- coding: utf-8 -*-
from odoo import fields
from odoo.addons.payment import utils as payment_utils
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo.tools.json import scriptsafe as json_scriptsafe


class WebsiteSaleInherit(WebsiteSale):

    @http.route(['/shop/cart/update_json'], type='json', auth="public",
                methods=['POST'], website=True, csrf=False)
    def cart_update_json(
            self, product_id, line_id=None, add_qty=None, set_qty=None,
            display=True,
            product_custom_attribute_values=None,
            no_variant_attribute_values=None, **kw
    ):
        """
        This route is called :
            - When changing quantity from the cart.
            - When adding a product from the wishlist.
            - When adding a product to cart on the same page (without redirection).
        """
        order = request.website.sale_get_order(force_create=True)
        if order.state != 'draft':
            request.website.sale_reset()
            if kw.get('force_create'):
                order = request.website.sale_get_order(force_create=True)
            else:
                return {}

        if product_custom_attribute_values:
            product_custom_attribute_values = json_scriptsafe.loads(
                product_custom_attribute_values)

        if no_variant_attribute_values:
            no_variant_attribute_values = json_scriptsafe.loads(
                no_variant_attribute_values)

        values = order._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values,
            **kw
        )

        request.session['website_sale_cart_quantity'] = order.cart_quantity

        if not order.cart_quantity:
            request.website.sale_reset()
            return values

        values['cart_quantity'] = order.cart_quantity
        values['minor_amount'] = payment_utils.to_minor_currency_units(
            order.amount_total, order.currency_id
        ),
        values['amount'] = order.amount_total

        if not display:
            return values
        # changes starts here
        sale_order = request.website.sale_get_order()
        website_sale_order_grouped = dict()
        if sale_order:
            for line in sale_order.website_order_line:
                if line.product_id.product_tmpl_id.id in website_sale_order_grouped:
                    website_sale_order_grouped[
                        line.product_id.product_tmpl_id.id]['line'][
                        'qty'] += line.product_uom_qty
                    website_sale_order_grouped[
                        line.product_id.product_tmpl_id.id]['line'][
                        'total'] += line.price_subtotal
                    website_sale_order_grouped[
                        line.product_id.product_tmpl_id.id]['sublines'].append(
                        line)
                else:
                    website_sale_order_grouped[
                        line.product_id.product_tmpl_id.id] = dict()
                    website_sale_order_grouped[
                        line.product_id.product_tmpl_id.id]['line'] = {
                        'rec': line.product_id.product_tmpl_id,
                        'id': line.product_id.product_tmpl_id.id,
                        'name': line.product_id.product_tmpl_id.name,
                        'qty': line.product_uom_qty,
                        'total': line.price_subtotal,
                    }
                    website_sale_order_grouped[
                        line.product_id.product_tmpl_id.id]['sublines'] = [
                        line]
        # changes ends here
        values['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template(
            "website_sale.cart_lines", {
                'website_sale_order': order,
                'website_sale_order_grouped': website_sale_order_grouped,
                'date': fields.Date.today(),
                'suggested_products': order._cart_accessories()
            }
        )
        values['website_sale.short_cart_summary'] = request.env['ir.ui.view']._render_template(
            "website_sale.short_cart_summary", {
                'website_sale_order': order,
            }
        )
        return values

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        response = super(WebsiteSaleInherit, self).checkout(**post)
        sale_order = request.website.sale_get_order()
        lines = dict()
        if sale_order:
            for line in sale_order.website_order_line:
                if line.product_id.product_tmpl_id.id in lines:
                    lines[
                        line.product_id.product_tmpl_id.id]['line']['qty'] += line.product_uom_qty
                    lines[
                        line.product_id.product_tmpl_id.id]['line']['total'] += line.price_subtotal
                    lines[line.product_id.product_tmpl_id.id]['sublines'].append(line)
                else:
                    prod_att_data = self.prepare_product_data_bo(line.product_id.product_tmpl_id.id)
                    lines[
                        line.product_id.product_tmpl_id.id] = dict()
                    lines[line.product_id.product_tmpl_id.id]['line'] = {
                        'rec': line.product_id.product_tmpl_id,
                        'id': line.product_id.product_tmpl_id.id,
                        'name': line.product_id.product_tmpl_id.name,
                        'qty': line.product_uom_qty,
                        'total': line.price_subtotal,
                        'sizes': prod_att_data['size'],
                        'colors': prod_att_data['color'],
                        'prod_att_data': prod_att_data,
                    }
                    lines[
                        line.product_id.product_tmpl_id.id]['sublines'] = [line]
                color_ptav = line.product_id.product_template_variant_value_ids.filtered(
                    lambda x: x.attribute_id.bulk_attribute == 'color')
                size_ptav = line.product_id.product_template_variant_value_ids.filtered(
                    lambda x: x.attribute_id.bulk_attribute == 'size')
                if size_ptav or color_ptav:
                    if size_ptav and color_ptav:
                        lines[line.product_id.product_tmpl_id.id]['line']['prod_att_data']['color_size_variant_mapping'][
                            str(color_ptav[0].product_attribute_value_id.id) + '-' +
                            str(size_ptav[0].product_attribute_value_id.id)].append(line)
                    elif size_ptav and lines[line.product_id.product_tmpl_id.id]['line']['colors']:
                        lines[line.product_id.product_tmpl_id.id]['line']['prod_att_data']['color_size_variant_mapping'][
                            str(lines[line.product_id.product_tmpl_id.id]['line']['colors'][0][0]) + '-' +
                            str(size_ptav[0].product_attribute_value_id.id)].append(line)
                    elif color_ptav and lines[line.product_id.product_tmpl_id.id]['line']['sizes']:
                        lines[line.product_id.product_tmpl_id.id]['line']['prod_att_data']['color_size_variant_mapping'][
                            str(color_ptav[0].product_attribute_value_id.id) + '-' +
                            str(lines[line.product_id.product_tmpl_id.id]['line']['sizes'][0][0])].append(line)
        request.update_context(lines=lines)
        return response
    # @http.route(['/shop/cart'], type='http', auth="public", website=True,
    #             sitemap=False)
    # def cart(self, access_token=None, revive='', **post):
    #     """Inherit to create a new structure of order lines
    #         *****Structure**********
    #         *product.template(1)   *
    #         *    product.product(1)*
    #         *    product.product(2)*
    #         *    product.product(3)*
    #         ************************
    #     """
    #     res = super(WebsiteSaleInherit, self).cart(access_token=None,
    #                                                revive='', **post)
    #     sale_order = request.website.sale_get_order()
    #     website_sale_order_grouped = dict()
    #     if sale_order:
    #         for line in sale_order.website_order_line:
    #             if line.product_id.product_tmpl_id.id in website_sale_order_grouped:
    #                 website_sale_order_grouped[
    #                     line.product_id.product_tmpl_id.id]['line'][
    #                     'qty'] += line.product_uom_qty
    #                 website_sale_order_grouped[
    #                     line.product_id.product_tmpl_id.id]['line'][
    #                     'total'] += line.price_subtotal
    #                 website_sale_order_grouped[
    #                     line.product_id.product_tmpl_id.id]['sublines'].append(
    #                     line)
    #             else:
    #                 website_sale_order_grouped[
    #                     line.product_id.product_tmpl_id.id] = dict()
    #                 website_sale_order_grouped[
    #                     line.product_id.product_tmpl_id.id]['line'] = {
    #                     'rec': line.product_id.product_tmpl_id,
    #                     'id': line.product_id.product_tmpl_id.id,
    #                     'name': line.product_id.product_tmpl_id.name,
    #                     'qty': line.product_uom_qty,
    #                     'total': line.price_subtotal,
    #                 }
    #                 website_sale_order_grouped[
    #                     line.product_id.product_tmpl_id.id]['sublines'] = [
    #                     line]
    #     request.update_context(
    #         website_sale_order_grouped=website_sale_order_grouped)
    #     return res

    @http.route('/shop/cart/deleteProductGroup', type='json',
                auth="user", methods=['POST'], website=True)
    def delete_product_group(self, **post):
        sale_order = request.website.sale_get_order()
        if sale_order:
            for line in sale_order.website_order_line.filtered(
                lambda l: l.product_id.product_tmpl_id.id == int(post.get(
                    'prod_tmpl'))):
                line.unlink()

    @http.route(['/shop/cart/new_order_bulk_update'], type='json',
                auth="public", methods=['POST'], website=True)
    def new_order_bulk_update(self, **kw):
        for product_id, qty in kw.items():
            try:
                qty = float(qty)
            except ValueError:
                qty = 0
            if qty:
                request.website.sale_get_order(force_create=1)._cart_update(
                    product_id=int(product_id), set_qty=qty)
            else:
                sale_order = request.website.sale_get_order()
                if sale_order:
                    for line in sale_order.website_order_line.filtered(
                            lambda l: l.product_id.id == int(product_id)):
                        line.unlink()
        return True

    @http.route(['/get/product/template/data'], type='json', auth="public",
                methods=['POST'], website=True)
    def get_product_template_data(self, **kw):
        product_template_ids = request.env['product.template'].sudo().search_read([('id', '=', kw.get('id'))],['name', 'product_variant_ids'])
        return product_template_ids

    def prepare_product_data_bo(self, ptid):
        product_id = request.env['product.template'].sudo().browse(ptid)
        color_size_variant_mapping = {}
        for variant in product_id.product_variant_ids:
            variant_attribute_name = '-'
            for ptav in variant.product_template_attribute_value_ids:
                if ptav.attribute_id.bulk_attribute == 'color':
                    variant_attribute_name = str(ptav.product_attribute_value_id.id) + variant_attribute_name
                if ptav.attribute_id.bulk_attribute == 'size':
                    variant_attribute_name = variant_attribute_name + str(ptav.product_attribute_value_id.id)
            variant_price = request.env['product.pricelist']._price_get(variant, 1).get(
                request.env.user.partner_id.property_product_pricelist.id, False)
            color_size_variant_mapping.update(
                {variant_attribute_name: [variant.id, variant_price and variant_price or variant.lst_price,
                                          variant.qty_available]})
        size_data = []
        size_value_ids = product_id.attribute_line_ids.filtered(
            lambda x: x.attribute_id.bulk_attribute == 'size') and product_id.attribute_line_ids.filtered(
            lambda x: x.attribute_id.bulk_attribute == 'size').value_ids.filtered(
            lambda y: y.id not in product_id.hidden_color_attribute_value_ids.ids) or []
        for x in size_value_ids:
            size_data.append([x.id, x.name])
        color_data = []
        color_value_ids = product_id.attribute_line_ids.filtered(
            lambda x: x.attribute_id.bulk_attribute == 'color') and product_id.attribute_line_ids.filtered(
            lambda x: x.attribute_id.bulk_attribute == 'color').value_ids.filtered(
            lambda y: y.id not in product_id.hidden_color_attribute_value_ids.ids) or []
        for x in color_value_ids:
            color_data.append([x.id, x.name])
        data = {
            'size': size_data,
            'color': color_data,
            'color_size_variant_mapping': color_size_variant_mapping,
            'currency_symbol': product_id.currency_id.symbol
        }
        return data

    @http.route(['/get/all/product/data'], type='json', auth="public",
                methods=['POST'], website=True)
    def get_all_product_data(self, **kw):
        ptid = kw.get('id')
        data = self.prepare_product_data_bo(ptid)
        return data
