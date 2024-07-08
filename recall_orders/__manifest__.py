# -*- coding: utf-8 -*-

{
    'name': 'POS recall',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 1,
    'summary': 'POS Recall Line',
    'description': """
        This module allows to recall orders 
    """,
    'depends': ['point_of_sale'],
    'data': [
        'views/assets.xml',
        'views/views.xml',
        # 'views/product_template_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/receipt.xml',
    ],
    'installable': True,
}
