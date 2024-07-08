# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound


from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.osv import expression

class website_add_product_tips(http.Controller):

    @http.route(['/shop/website/tip/check'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_qty_data_tips(self, **kw):
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        tip = False;
        config = False;
        if sale_order:
            for i in sale_order.order_line:
                if i.product_id.name == 'Website Tips':
                    tip = i.tip_data

            if request.env['ir.config_parameter'].sudo().get_param('website_tips.website_tipproduct'):
                if int(request.env['ir.config_parameter'].sudo().get_param('website_tips.website_tip_product_id'))> 0:
                    config = True
            return [tip,config]
        else:
            return False

    @http.route(['/shop/website/tip/update'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_tips_data(self, tip, tip_data, **kw):
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        tip_amount = 0
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        if sale_order: 
            id = sale_order.id
            tip_products = request.env['product.product'].sudo().search([('name', '=', 'Website Tips')], limit=1).id
            objs = request.env['sale.order.line'].sudo().search([('order_id','=',id),('product_id','=', tip_products)])
            for line in objs:
                line.sudo().unlink()
            amount_untaxed = sale_order.amount_untaxed
            self.calculateSurcharge(sale_order)
            if tip:
                if amount_untaxed >0:
                    amount = amount_untaxed * float(tip)
                    tip_amount = amount/100
                    if tip_data == 'tip_other':
                        vals = {
                            'product_id': tip_products,
                            'product_uom_qty': 1,
                            'price_unit': float(tip),
                            'order_id': id,
                            'tip_data': tip_data,
                            'is_coupon_type': False,
                        }
                    else:
                        vals = {
                            'product_id': tip_products,
                            'product_uom_qty': 1,
                            'price_unit': tip_amount,
                            'order_id': id,
                            'tip_data': tip_data,
                            'is_coupon_type': False,
                        }
                    obj = request.env['sale.order.line'].sudo().create(vals)
                    if obj:
                        return True
        return False

    def calculateSurcharge(self, order):
        if order:
            holiday_surcharge = request.env['ir.config_parameter'].sudo().get_param('bi_website_add_product.holiday_surcharge')
            surcharge_product = request.env['ir.config_parameter'].sudo().get_param('bi_website_add_product.surcharge_product')
            start_date = request.env['ir.config_parameter'].sudo().get_param('bi_website_add_product.start_date')
            end_date = request.env['ir.config_parameter'].sudo().get_param('bi_website_add_product.end_date')
            start_date_date_time_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_date_time_obj = datetime.strptime(end_date, '%Y-%m-%d')
            if surcharge_product and holiday_surcharge and order:
                for line in order.order_line:
                    if int(surcharge_product) == int(line.product_id.id):
                        line.sudo().unlink()
            if holiday_surcharge and surcharge_product and order:
                now = fields.Datetime.now()
                order.date_order = now
                order_date = order.date_order.date()
                from_date = start_date_date_time_obj.date()
                to_date = end_date_date_time_obj.date()
                if order_date >= from_date and order_date <= to_date:
                    choose_price = request.env['ir.config_parameter'].sudo().get_param(
                            'bi_website_add_product.choose_price')
                    if choose_price == 'percentage':
                        percentage_amount = float(request.env['ir.config_parameter'].sudo().get_param('bi_website_add_product.percentage'))
                        if percentage_amount != 0:
                            if order.amount_total > 0:
                                amount_percentage = order.amount_total * (percentage_amount / 100)
                                print(amount_percentage, "hkhkj")
                            if amount_percentage > 0:
                                print(amount_percentage)
                                surcharge_product_product = request.env['product.product'].sudo().search([('id','=',surcharge_product)])
                                request.env['sale.order.line'].sudo().create({
                                    'order_id': order.id,
                                    'customer_lead': 1,
                                    'product_id': surcharge_product_product.id,
                                    'product_uom_qty': 1.0,
                                    'price_unit': amount_percentage
                                })
                    if choose_price == 'amount':
                        amount = float(request.env['ir.config_parameter'].sudo().get_param('bi_website_add_product.amount'))
                        surcharge_product_product = request.env['product.product'].sudo().search([('id', '=', surcharge_product)])
                        request.env['sale.order.line'].sudo().create({
                            'order_id': order.id,
                            'customer_lead': 1,
                            'product_id': surcharge_product_product.id,
                            'product_uom_qty': 1.0,
                            'price_unit': amount
                        })
            return True
