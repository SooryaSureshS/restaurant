# -*- coding: utf-8 -*-
{
    'name': 'Website Table Booking',
    'category': 'Theme/eCommerce',
    'version': '14.0.0.4',
    'author': 'Socius',
    'website': 'http://www.jithesh.com',
    'summary': '''Theme Inherits''',
    'description': """Theme WineShop""",

    'depends': [
        'website',
        'website_sale',
        'theme_wineshop',
        'pos_restaurant'
    ],

    'data': [
        # 'data/data.xml',
        # 'security/ir.model.access.csv',
        'views/assets.xml',
        'views/booking.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,

}
