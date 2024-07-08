# -*- coding: utf-8 -*-
{
    'name': 'Pos Table Booking',
    'category': 'Point of Sale',
    'version': '14.0.0.4',
    'author': 'Socius',
    'website': 'http://www.jithesh.com',
    'summary': '''POS table booking Inherits''',
    'description': """pos table booking""",

    'depends': [
        'website',
        'website_sale',
        # 'theme_wineshop',
        'pos_restaurant',
        'table_booking',
        'website_reservation',
        'point_of_sale',
    ],

    'data': [
        # 'data/data.xml',
        # 'security/ir.model.access.csv',
        'views/assets.xml',
        'views/views.xml',
        'views/table.xml',
        'views/pos_order.xml',
        # 'views/sale_order.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/table.xml',
        'static/src/xml/receipts.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,

}
