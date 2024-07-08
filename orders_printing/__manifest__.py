# -*- encoding: utf-8 -*-
{
    "name": "Orders Printing",
    "version": "14.0",
    "author": "SIGB",
    "sequence": 0,
    "depends": ['point_of_sale', 'kitchen_order', 'web'],
    "data": [
        'views/views.xml',
        'views/assets.xml',
        # 'views/pos_config.xml',
    ],
    'qweb': [
        'static/src/xml/order_print_receipt.xml',
    ],
    "installable": True,
    "application": False,
}