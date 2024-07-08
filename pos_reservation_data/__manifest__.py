# -*- coding: utf-8 -*-

{
    'name': 'Reservation Details In POS Frontend',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 1,
    'summary': 'Table Reservation List',
    'description': """
        Table Reservation List
    """,
    'depends': ['pos_restaurant', 'website_reservation'],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
}
