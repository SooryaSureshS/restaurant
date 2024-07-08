# -*- coding: utf-8 -*-

{
    'name': 'POS MCD Changes Orders',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 1,
    'summary': 'POS MCD Changes',
    'description': """
        This for open orders manipulation
    """,
    'depends': ['pos_order_type','point_of_sale','pos_optional_products','kitchen_order','pos_restaurant','web','sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        # 'views/product_category.xml',
        'views/views.xml',
        'views/pos_config.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/receipt.xml',
        'static/src/xml/order_print_receipt.xml',
        'static/src/xml/SendToKitchen.xml',
    ],
    'installable': True,
}
