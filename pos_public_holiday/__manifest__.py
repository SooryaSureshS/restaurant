# -*- coding: utf-8 -*-

{
    'name': 'POS Public Holiday',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 1,
    'summary': 'POS Public Holiday',
    'description': """
        This fpublic Holidays manipulation
    """,
    'depends': ['point_of_sale','pos_optional_products','kitchen_order','pos_restaurant','web','pos_order_type','sale'],
    'data': [
        'views/assets.xml',
        # 'data/data.xml',
        'views/view.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
}
