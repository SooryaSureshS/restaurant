# -*- coding: utf-8 -*-

{
    'name': 'POS Open Orders',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 1,
    'summary': 'POS Open orders Line',
    'description': """
        This for open orders manipulation
    """,
    'depends': ['pos_order_type','point_of_sale','pos_optional_products','kitchen_order','pos_restaurant','web'],
    'data': [
        'views/assets.xml',
        # 'views/product_category.xml',
        'views/views.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
}
