# -*- coding: utf-8 -*-

{
    'name': 'Point of Sale Kitchen Order',
    'version': '14.0.1.0.1',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'Simple Kitchen order in the Point of Sale ',
    'description': """
        This module allows the cashier to quickly give percentage-based
        Kitchecn order to a customer.
    """,
    'depends': ['point_of_sale', 'pos_restaurant', 'sale', 'base', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/view_config.xml',
        'views/pos_order.xml',
        'views/product_template.xml'
    ],
    'qweb': [
        'static/src/xml/kitchecn_order.xml',
        'static/src/xml/kitchen_screen_receipt.xml',
        'static/src/xml/updatepopup.xml',
        'static/src/xml/message.xml',
        'static/src/xml/receipt.xml',
    ],
    'installable': True,
}
