# -*- coding: utf-8 -*-

{
    'name': 'POS Optional Products',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 1,
    'summary': 'POS Optional Products',
    'description': """
        This module allows the user to pick optional products. 
    """,
    'depends': ['point_of_sale', 'product'],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/bundle_product.xml',
        'static/src/xml/OptionalProductsPopupLarge.xml',
    ],
    'installable': True,
}
