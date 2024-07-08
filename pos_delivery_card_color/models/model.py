# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
from odoo import models, fields, api, tools, _

_logger = logging.getLogger(__name__)

class PosConfigDeliveryColor(models.Model):
    _inherit = 'pos.config'

    iface_delivery_type = fields.Boolean(string='Delivery Type color', help='Allow the Delivery Type Color')

    """Take away Color coding"""

    pos_take_away_font_color = fields.Char(string="Take Away Color",help="Choose your color")
    pos_take_away_background_color = fields.Char(string="Take Away Background Color",help="Choose your color")
    pos_take_away_border_color = fields.Char(string="Take Away Border Color",help="Choose your color")
    pos_take_away_font_family = fields.Char(string="Take Away Font Family")
    pos_take_away_header_color = fields.Char(string="Take Away Header Color")

    """Pos config dine in  order color"""

    pos_dine_in_font_color = fields.Char(string="Dine In Font color")
    pos_dine_in_background_color = fields.Char(string="Dine In Background color")
    pos_dine_in_border_color = fields.Char(string="Dine In Border color")
    pos_dine_in_font_family = fields.Char(string="Take Away Font Family")
    pos_dine_in_header_color = fields.Char(string="Take Away Header Color")

    """Pos config delivery  order color"""
    pos_delivery_font_color = fields.Char(string="Delivery Font color")
    pos_delivery_background_color = fields.Char(string=" Delivery Background color")
    pos_delivery_border_color = fields.Char(string="Delivery Border color")
    pos_delivery_font_family = fields.Char(string="Take Away Font Family")
    pos_delivery_header_color = fields.Char(string="Take Away Header Color")

    """Pos config phone  order color"""
    pos_phone_font_color = fields.Char(string="Phone Order Font color")
    pos_phone_background_color = fields.Char(string=" Phone Order Background color")
    pos_phone_border_color = fields.Char(string="Phone Order Border color")
    pos_phone_font_family = fields.Char(string="Phone Font Family")
    pos_phone_header_color = fields.Char(string="Phone Header Color")

    """Pos config pickup  order color"""
    pos_pickup_font_color = fields.Char(string="Pickup Order Font color")
    pos_pickup_background_color = fields.Char(string=" Pickup Order Background color")
    pos_pickup_border_color = fields.Char(string="Pickup Order Border color")
    pos_pickup_font_family = fields.Char(string="Pickup Font Family")
    pos_pickup_header_color = fields.Char(string="Pickup Header Color")




    # iface_delivery_type_sale = fields.Boolean(string='Delivery Type color', help='Allow the Delivery Type Color')

    """Pos config Kerbside  order color"""
    pos_kerbside_font_color = fields.Char(string=" kerbside Font color")
    pos_kerbside_background_color = fields.Char(string=" kerbside Background color")
    pos_kerbside_border_color = fields.Char(string=" kerbside Border color")
    pos_kerbside_font_family = fields.Char(string="kerbside Font Family")
    pos_kerbside_header_color = fields.Char(string="kerbside Header Color")


    pos_kvs_size_adjustments = fields.Float(string="KVS card adjustment", default='80')

