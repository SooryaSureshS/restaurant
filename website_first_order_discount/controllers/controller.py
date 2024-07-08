from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
import geopy.distance
from odoo import http, api, fields, models, _
import requests, json
import googlemaps


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True, sitemap=False)
    def confirm_order(self, **post):
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection
        # try:
        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        request.website.sale_get_order(update_pricelist=True)
        extra_step = request.website.viewref('website_sale.extra_info_option')
        uid = request.session.uid
        user = order.partner_shipping_id
        partner_location = request.env['res.partner'].sudo().search([("id", "=", user.id)])

        partner_location.geo_localize()
        partner_latitude = partner_location.partner_latitude
        partner_longitude = partner_location.partner_longitude
        valid = False
        delivery_locations = request.env['delivery.location'].sudo().search([])
        for loc in delivery_locations:
            delivery_location = (loc.latitude, loc.longitude)
            partner_latitude_map = partner_location.user_lat
            partner_longitude_map = partner_location.user_long
            if partner_latitude_map and partner_latitude_map:
                partner_loaction = (partner_latitude, partner_longitude)

                api_key = 'AIzaSyCP8gcIkivceoSrgmYTq0_XxTHd6l5rNFM'
                gmaps = googlemaps.Client(key=api_key)

                origin = (loc.latitude, loc.longitude)
                destinations = (partner_latitude_map, partner_longitude_map)

                actual_distance = []

                # for destination in destinations:
                result = \
                gmaps.distance_matrix(origin, destinations, mode='driving')["rows"][0]["elements"][0]["distance"]["value"]
                result = result / 1000
                actual_distance.append(result)
                if actual_distance[0] <= loc.delivery_radius:
                    valid = True
                    break
            else:
                valid = False

        """First Order Discount"""
        if order:
            if order.partner_id.first_order_discount:
                # if not request.env['sale.order'].sudo().search([('partner_id','=',order.partner_id.id)]):
                product = request.env['product.product'].sudo().search([('name','=','First Order Discount')])
                if not product:
                    product= request.env['product.product'].sudo().create({
                        'name':'First Order Discount',
                        'type':'service',
                        'default_code':"First Order Discount",
                        'list_price':-5,
                    })
                request.env['sale.order.line'].sudo().create({'product_id':product.id,
                                                            'order_id':order.id,
                                                            'product_uom_qty':1,
                                                            'price_unit':product.list_price
                })
                order.partner_id.first_order_discount = False

        """first order discount end here"""

        if extra_step.active:
            return request.redirect("/shop/extra_info")
        data = request.env['res.partner'].sudo().search([("id", "=", user.id)])
        if valid:
            order.sudo().write({'valid_address': True})
            return request.redirect("/shop/payment")
        else:
            if order.website_delivery_type == 'pickup':
                return request.redirect("/shop/payment")
            else:
                order.sudo().write({'valid_address': False})
                return request.redirect("/shop/checkout")
        # except:
        #     order.sudo().write({'valid_address': False})
        #     return request.redirect("/shop/checkout")

    def _get_mandatory_billing_fields(self):
        # deprecated for _get_mandatory_fields_billing which handle zip/state required
        order = request.website.sale_get_order()
        if order.website_delivery_type == 'delivery':
            return ["name", "email", "street", "city", "country_id", "user_lat", "user_long"]
        else:
            return ["name", "email", "street", "city", "country_id"]

    def _get_mandatory_shipping_fields(self):
        # deprecated for _get_mandatory_fields_shipping which handle zip/state required
        order = request.website.sale_get_order()
        if order.website_delivery_type == 'delivery':
            return ["name", "street", "city", "country_id", "user_lat", "user_long"]
        else:
            return ["name", "street", "city", "country_id"]

