# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Ps Order Remove Line',
    'version': '14',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': '',
    'description': """

This module remove order line in pos.

""",
    'depends': ['point_of_sale'],
    "data": ["views/assets.xml"],
    # "qweb": ["static/src/xml/orderline.xml"],
}
