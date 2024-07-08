# -*- coding: utf-8 -*-

{
    'name': 'Point of Sale Delivery Type Color',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'Simple Kitchen order card view color in the Point of Sale ',
    'description': """
        This module allows you to change the color
        Kitchen order .
    """,
    'depends': ['point_of_sale', 'pos_restaurant', 'sale', 'base', 'kitchen_order'],
    'data': [
        'views/assets.xml',
        'views/pos_config.xml',
    ],
    'qweb': [
        # 'static/src/xml/kitchen_screen.xml',
    ],
    'installable': True,
}
