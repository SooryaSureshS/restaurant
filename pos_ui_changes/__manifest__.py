# -*- coding: utf-8 -*-

{
    'name': 'POS UI Changes SIGB',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 1,
    'summary': 'POS Changes Line',
    'description': """
        This module to change the UI
    """,
    'depends': ['point_of_sale','pos_optional_products','kitchen_order','pos_restaurant','pos_open_orders'],
    'data': [
        'views/assets.xml',
        'views/product_category.xml',
        # 'views/view_config.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
}
