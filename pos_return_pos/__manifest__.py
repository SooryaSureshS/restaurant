# -*- coding: utf-8 -*-

{
    'name': 'POS Order Return SIGB',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 1,
    'summary': 'POS Order Return Line',
    'description': """
        This module allows the cashier to return each products 
    """,
    'depends': ['point_of_sale', 'product','sale'],
    'data': [
        'views/assets.xml',
        'views/views.xml',
        'views/view_config.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
}
