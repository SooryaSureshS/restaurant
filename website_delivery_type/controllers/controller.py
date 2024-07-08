import base64
import json
import pytz
from odoo import http
from odoo.http import request
import googlemaps
from geopy.geocoders import GoogleV3
from geopy.geocoders import Nominatim
import datetime
import json
import geopy.distance

class UpdateOrderAddress(http.Controller):

    @http.route('/get/time/cooking/delivery', csrf=False, type='json', auth="public")
    def CookingTimeDelivery(self, **kw):


        picking_date = kw.get('picking_date','Today')
        print("ffffff",picking_date)
        current_uid = request.env.user
        tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
        if picking_date == 'Today':
            today = datetime.datetime.now(tz).strftime("%A")
        else:

            date= datetime.datetime.strptime(picking_date, "%m/%d/%Y")
            today = date.astimezone(tz).strftime("%A")

        res_config_settings = request.env['ir.config_parameter'].sudo()
        min_delivery_time = res_config_settings.get_param('website_sale_hour.delivery_time')
        minutes = float(min_delivery_time) * 60
        time =  datetime.datetime.now(tz)

        from_time_1 =''
        from_time_2 =''
        if today=='Sunday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_delivery_sunday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_delivery_sunday')
        elif today=='Monday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_delivery_monday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_delivery_monday')
        elif today=='Tuesday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_delivery_tuesday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_delivery_tuesday')
        elif today=='Wednesday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_delivery_wednesday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_delivery_wednesday')
        elif today=='Thursday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_delivery_thursday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_delivery_thursday')
        elif today=='Friday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_delivery_friday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_delivery_friday')
        elif today=='Saturday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_delivery_saturday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_delivery_saturday')

        time_from1 = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_1) * 60, 60))
        time_from2 = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_2) * 60, 60))

        pickup_date_val = time + datetime.timedelta(minutes=minutes)

        time_now = pickup_date_val.time().strftime('%H:%M')
        if picking_date == 'Today':
            picking_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')
        else:
            picking_date = datetime.datetime.strptime(picking_date, "%m/%d/%Y").date().strftime('%Y-%m-%d')

        return {'time_now': time_now,'picking_date':picking_date,'after_date':pickup_date_val.date().strftime('%Y-%m-%d'),'today_date':datetime.datetime.now(tz).date().strftime('%Y-%m-%d'), "from_time_1": time_from1, 'from_time_2': time_from2}

    @http.route('/save/time/cooking/delivery',website=True, csrf=False, type='json', auth="public")
    def CookingTimeDeliverySave(self, **kw):
        sale_order = request.website.sale_get_order()
        print("fffffffffffffffffffffffffffffffffff",sale_order)
        if sale_order:
            pickup_date = kw['pickup_date']
            pickup_time = kw['pickup_time']
            print("RRRRRRRRRRRRRRRRRRRRRRRR", pickup_date,pickup_time)
            if pickup_date == 'Today':
                pickup_date_val = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=00)
            else:
                pickup_date_val = datetime.datetime.strptime(pickup_date, '%m/%d/%Y').date() + datetime.timedelta(hours=10, minutes=00)
            if pickup_time:
                time_val = datetime.datetime.strptime(pickup_time, '%H:%M').time()
                pick_time_val = time_val
            if pickup_time and pickup_date:
                pickup_date_time = datetime.datetime.combine(pickup_date_val, time_val)
                pickup_date_string = pickup_date_time.strftime("%d/%m/%Y %H:%M")
                sale_order.sudo().write({'pickup_date':pickup_date_time,'pickup_date_string':str(pickup_date_string)})
        return True

    @http.route(['''/sale/<int:id>/update/address/<string:access_token>'''], type='http', auth="public", website=True)
    def UpdateAddress(self, id=None, access_token=None, **kw):
        if id:
            order = request.env['sale.order'].sudo().search([('id', '=', id)], limit=1)
            if order.token_random == access_token:
                order_line = order.order_line.filtered(
                    lambda line: line.product_id.type != 'service' and line.order_line_state not in ['cancel', 'return',
                                                                                                     'done'])
                if order_line:
                    return request.render('website_delivery_type.kerbside_order_address_update', {'order': order})
                else:
                    return request.render('website_delivery_type.kerbside_order_address_update',
                                          {'order': "delivered", "order_name": order.name})

    @http.route('/order/update/vehicle/details', type='json', csrf=False, auth="none")
    def UpdateSales(self, **kw):
        order_id = kw['order_id']
        try:
            sale_order = request.env['sale.order'].sudo().search([('id', '=', int(order_id))], limit=1)
            print("Order: ", sale_order)
            if sale_order:
                order_line = sale_order.order_line.filtered(
                    lambda line: line.product_id.type != 'service' and line.order_line_state not in ['cancel', 'return',
                                                                                                     'done'])
                print(order_line)
                if order_line:
                    location_name1 = kw['v_location']
                    location_notes = kw['location_note']
                    if location_name1:
                        location_name = request.env['vehicle.location'].sudo().search(
                            [('location_name', '=', str(location_name1))]).id
                        sale_order.sudo().write({'approximate_location': location_name,
                                                 'location_notes': str(location_notes),
                                                 'updated_location': True})
                        return True
                else:
                    return "delivered"
            else:
                return "no_order"
        except:
            return "no_order"

    @http.route(['''/sale/<int:id>/order/summary/<string:access_token>'''], type='http', auth="public", website=True)
    def OrderSummary(self, id=None, access_token=None, **kw):
        if id:
            order = request.env['sale.order'].sudo().browse(id)
            return request.render("website_sale.confirmation", {'order': order})
        else:
            return request.redirect('/shop')

    @http.route('/calculate/distance', csrf=False, type='http', auth="public")
    def CalculateDistance(self, **kw):
        # kw = request.httprequest.data
        latitude = kw['lat']
        longitude = kw['long']
        print(latitude)
        print(longitude)
        delivery_radius = 0
        valid = False
        delivery_locations = request.env['delivery.location'].sudo().search([])
        for loc in delivery_locations:
            delivery_location = (loc.latitude, loc.longitude)
            partner_latitude_map = str(latitude)
            partner_longitude_map = str(longitude)
            if partner_latitude_map and partner_latitude_map:
                partner_loaction = (partner_latitude_map, partner_longitude_map)

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

        if valid:
            geolocator = Nominatim(user_agent="OnItBurgers")
            location = geolocator.reverse(latitude + "," + longitude)
            location_data = location.raw
            data = {'status': 'success',
                    'house_no': location_data.get('address').get('house_number', False),
                    'road': location_data.get('address').get('road', False),
                    'suburb': location_data.get('address').get('suburb', False),
                    'city': location_data.get('address').get('city', False),
                    'postcode': location_data.get('address').get('postcode', False),
                    }
            print("asdad", data)
            return json.dumps(data)
        else:
            data = {'status': 'failed', 'distance': delivery_radius}
            return json.dumps(data)

    @http.route(['/order/feedback/update'], type='json', auth="public", website=True)
    def feedbackupdate(self, **kw):
        order_id = kw.get('order_id', False)
        if order_id:
            order = request.env['sale.order'].sudo().browse([int(order_id)])
            for i in order:
                vals= {'feedback_note':kw.get('feedback_message', False),'feedback_face':kw.get('feedback_face', False),'feedback_check':True}
                i.sudo().write(vals)
        return True

    @http.route(['''/feedback/order/<int:id>'''], type='http', auth="public", website=True)
    def FeedbackRedriection(self, id=None, **kw):
        if id:
            order = request.env['sale.order'].sudo().browse(id)
            return request.render("website_sale.confirmation", {'order': order})
        else:
            return request.redirect('/shop')


    @http.route(['/delivery/autofill'], type='json', auth="public", website=True)
    def DeliveryAutofill(self, id=None, **kw):
        uid = request.session.uid
        if uid:
            employee = request.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
            login_id = employee.partner_id
            details = {"name": login_id.name, 'mobile':login_id.phone, 'email': login_id.email,
                     }
            # 'vcolor': login_id.vehicle_color, 'plate_no': login_id.license_plate_no
            return details
        else:
            return False

    @http.route('/calculate/lat/lang', csrf=False, type='http', auth="public")
    def CalculateLatLangs(self, **kw):
        # kw = request.httprequest.data
        street1 = kw['street1']
        city = kw['city']
        zip = kw['zip']
        zip = kw['zip']
        order_id_country_name = kw['order_id_country_name']
        order_id_state = kw['order_id_state']
        order_company_id = kw['order_company_id']
        # self._geo_localize(partner.street,
        #                    partner.zip,
        #                    partner.city,
        #                    partner.state_id.name,
        #                    partner.country_id.name)
        geo_location = request.env['res.partner'].sudo()._geo_localize(street1,zip,city,order_id_state,order_id_country_name)
        print("geo location",geo_location)
        if geo_location:
            company = request.env['res.company'].sudo().search([('id','=',int(order_company_id))],limit=1)
            print("compamn",company)
            if company:
                if company.delivery_location:
                    if company.delivery_location.latitude and company.delivery_location.longitude:
                        company_cordinate = (company.delivery_location.latitude, company.delivery_location.longitude)
                        data = json.dumps(geopy.distance.distance(company_cordinate, geo_location).km)
                        if geopy.distance.distance(company_cordinate, geo_location).km >= company.delivery_location.delivery_radius:
                            result = {
                                "flag": 1,
                                "status": "Sorry we can't deliver to this location",
                                "distance": round(geopy.distance.distance(company_cordinate, geo_location).km, 2),
                            }
                            data = json.dumps(result)
                            return data
                        else:
                            result = {
                                "flag":2,
                                "status": "We can deliver to this location",
                                "distance": round(geopy.distance.distance(company_cordinate, geo_location).km, 2),

                            }
                            data = json.dumps(result)
                        return data
                    else:
                        return False
                else:
                    False
            else:
                return False
        else:
            return False