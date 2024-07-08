import base64
import json
import pytz
from werkzeug.exceptions import Forbidden, NotFound
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http, api, fields, models, _
import datetime
from datetime import date
from odoo.addons.website_sale.controllers.main import WebsiteSale


class PickUp(http.Controller):

    @http.route('/get/options/group', csrf=False, type='json', auth="public")
    def OptionGroup(self, **kw):
        child_id = kw.get('child_id', False)
        if child_id:
            group = request.env['options.group'].sudo().search([('id','=',child_id)],limit=1)
            if group:
                return {"max":group.max_count}

    @http.route('/get/options/all/group', csrf=False, type='json', auth="public")
    def OptionGroupAll(self, **kw):
        child_id = kw.get('ids', False)
        if len(child_id)>0:
            vals = child_id[0]
            group = request.env['options.group'].sudo().search([('id', 'in', list(map(int,child_id[0].keys())))])
            if group:
                response = []
                for i in group:
                    response.append({'count':i.min_count,'selected':vals.get(str(i.id)),'id':str(i.id),'name':i.name})
                return response

    @http.route(['/shop/cart/update_option/bundle'], type='json', auth="public", methods=['POST'], website=True,
                multilang=False)
    def bundle_product(self, product_id, add_qty, checkout_note, choice_product_data, goto_shop=None, lang=None,
                       **kwargs):

        order = request.website.sale_get_order(force_create=True)
        if order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order(force_create=True)

        order_line = order.order_line
        # for i in range(0, add_qty):
        if add_qty > 0:
            bundle_pro = request.env['product.product'].sudo().search([('id', '=', product_id)])
            name = str(bundle_pro.name+' - Combo')
            bundle_data = order.order_line.sudo().create({'product_id': bundle_pro.id,
                                                          'name': name,
                                                          'order_id': order.id,
                                                          'bundle_parent': True,
                                                          'price_unit': bundle_pro.lst_price,
                                                          'product_uom_qty': add_qty,
                                                          'customer_lead': bundle_pro.sale_delay,
                                                          'checkout_note': checkout_note})
            print(bundle_data.bundle_parent)
            for data in choice_product_data:
                parent = ''
                parent_data = ''
                parent_prod = request.env['product.product'].sudo().search(
                    [('product_tmpl_id.id', '=', data['choice_product'])])
                print(parent_prod)
                parent_pro = parent_prod[0]
                if parent_pro:
                    parent_data = order.order_line.sudo().create({'product_id': parent_pro.id,
                                                                  'name': parent_pro.name,
                                                                  'order_id': order.id,
                                                                  'price_unit': parent_pro.product_tmpl_id.bundle_extra_price,
                                                                  'bundle_child': True,
                                                                  'bundle_option': True,
                                                                  'bundle_parent_id': bundle_data.id,
                                                                  'product_uom_qty': add_qty,
                                                                  'linked_line_id': bundle_data.id,
                                                                  'customer_lead': parent_pro.sale_delay})
                if data['variants']:
                    for variant in data['variants']:
                        variant_pro = request.env['product.product'].sudo().search([
                            ('product_tmpl_id.id', '=', int(variant))])
                        print(variant, variant_pro.name)
                        variant_line = order.order_line.sudo().create({'product_id': variant_pro.id,
                                                                       'name': variant_pro.name,
                                                                       'order_id': order.id,
                                                                       'price_unit': variant_pro.lst_price,
                                                                       'product_uom_qty': add_qty,
                                                                       'bundle_child': True,
                                                                       'linked_line_id': bundle_data.id,
                                                                       'bundle_parent_id': bundle_data.id,
                                                                       'customer_lead': variant_pro.sale_delay})
        if order.order_line:
            sorted_product = sorted(order.order_line, key=lambda x: x.product_id.pos_categ_id.sequence)
            print(sorted_product)
            seq = 0
            for k in sorted_product:
                print(k.product_id.name)
                k.sudo().write({'sequence': seq})
                for i in order.order_line:
                    if i.linked_line_id:
                        i.sudo().write({'sequence': i.linked_line_id.sequence})
                seq += 1

        if order:
            order_main = order.order_line.filtered(lambda line: len(line.linked_line_id) == 0)
            qty = int(sum(order_main.mapped('product_uom_qty')))
            return qty
        return False

    @http.route(['/shop/cart/update_option'], type='http', auth="public", methods=['POST'], website=True, multilang=False)
    def cart_options_update_json(self, product_and_options, checkout_note, goto_shop=None, lang=None, **kwargs):
        """This route is called when submitting the optional product modal.
            The product without parent is the main product, the other are options.
            Options need to be linked to their parents with a unique ID.
            The main product is the first product in the list and the options
            need to be right after their parent.
            product_and_options {
                'product_id',
                'product_template_id',
                'quantity',
                'parent_unique_id',
                'unique_id',
                'product_custom_attribute_values',
                'no_variant_attribute_values',
                'checkout_note'
            }
        """
        if lang:
            request.website = request.website.with_context(lang=lang)

        order = request.website.sale_get_order(force_create=True)
        if order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order(force_create=True)
        product_and_options_all = json.loads(product_and_options)
        product_and_options = product_and_options_all[0]
        products_alternative = product_and_options_all[1]
        if product_and_options:
            # The main product is the first, optional products are the rest
            main_product = product_and_options[0]
            if int(main_product['quantity']) == 1:
                value = order._cart_update(
                    product_id=main_product['product_id'],
                    add_qty=main_product['quantity'],
                    product_custom_attribute_values=main_product['product_custom_attribute_values'],
                    no_variant_attribute_values=main_product['no_variant_attribute_values'],
                )
                if value['line_id']:
                    line = value['line_id']
                    parent_line = request.env['sale.order.line'].sudo().search([('id', '=', line)])
                    parent_line.sudo().write({'checkout_note': checkout_note})
                option_parent = {main_product['unique_id']: value['line_id']}
                for option in product_and_options[1:]:
                    parent_unique_id = option['parent_unique_id']
                    option_value = order._cart_update(
                        product_id=option['product_id'],
                        set_qty=option['quantity'],
                        linked_line_id=option_parent[parent_unique_id],
                        product_custom_attribute_values=option['product_custom_attribute_values'],
                        no_variant_attribute_values=option['no_variant_attribute_values'],
                    )
                    option_parent[option['unique_id']] = option_value['line_id']
            else:
                # for i in range(1,main_product['quantity']+1):
                    value = order._cart_update(
                        product_id=main_product['product_id'],
                        add_qty=main_product['quantity'],
                        product_custom_attribute_values=main_product['product_custom_attribute_values'],
                        no_variant_attribute_values=main_product['no_variant_attribute_values'],
                    )
                    if value['line_id']:
                        line = value['line_id']
                        parent_line = request.env['sale.order.line'].sudo().search([('id', '=', line)])
                        parent_line.sudo().write({'checkout_note': checkout_note})
                    option_parent = {main_product['unique_id']: value['line_id']}

                    toppings=main_product.get('toppings',False)
                    if toppings:
                        toppings_opt = toppings[list(toppings.keys())[0]]
                        for opt in toppings_opt:
                            # parent_unique_id = option['parent_unique_id']
                            option_value = order._cart_update(
                                product_id=int(opt),
                                set_qty=int(list(toppings.keys())[0]),
                                linked_line_id=value['line_id'],
                                product_custom_attribute_values=main_product['product_custom_attribute_values'],
                                no_variant_attribute_values=main_product['no_variant_attribute_values'],
                            )
        if products_alternative:
            for option in products_alternative:
                value = order._cart_update(
                    product_id=option['product_id'],
                    add_qty=1,
                    product_custom_attribute_values=option['product_custom_attribute_values'],
                    no_variant_attribute_values=option['no_variant_attribute_values'],
                )
                if value:
                    print("ybqdef")

        if order.order_line:
            sorted_product = sorted(order.order_line, key=lambda x: x.product_id.pos_categ_id.sequence)
            print(sorted_product)
            seq = 0
            for k in sorted_product:
                print(k.product_id.name)
                k.sudo().write({'sequence': seq})
                for i in order.order_line:
                    if i.linked_line_id:
                        i.sudo().write({'sequence': i.linked_line_id.sequence})
                seq += 1

        return str(order.cart_quantity)

# class WebsiteSale(http.Controller):
    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        """This route is called when changing quantity from the cart or adding
        a product from the wishlist."""
        order = request.website.sale_get_order(force_create=1)
        if order.state != 'draft':
            request.website.sale_reset()
            return {}

        value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)

        if not order.cart_quantity:
            request.website.sale_reset()
            return value

        order = request.website.sale_get_order()
        value['cart_quantity'] = order.cart_quantity

        if not display:
            return value

        # Optional Product Quantity Change WRT The Parent Product.
        if order.order_line:
            for line in order.order_line:
                if line.linked_line_id:
                    line.product_uom_qty = line.linked_line_id.product_uom_qty

        if order.order_line:
            sorted_product = sorted(order.order_line, key=lambda x: x.product_id.pos_categ_id.sequence)
            print(sorted_product)
            seq = 0
            for k in sorted_product:
                print(k.product_id.name)
                k.sudo().write({'sequence': seq})
                for i in order.order_line:
                    if i.linked_line_id:
                        i.sudo().write({'sequence': i.linked_line_id.sequence})
                seq += 1

        value['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template("website_sale.cart_lines", {
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': order._cart_accessories()
        })
        value['website_sale.short_cart_summary'] = request.env['ir.ui.view']._render_template("website_sale.short_cart_summary", {
            'website_sale_order': order,
        })
        return value
