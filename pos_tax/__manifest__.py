# -*- coding: utf-8 -*-

{
    'name': 'POS Tax',
    'category': 'Point of Sale',
    'version': '14.0.0.0',
    'author': 'Dhaval',
    'website': 'https://uncannycs.com',
    'summary': 'POS Tax',
    'description': "POS Tax",
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/account_views.xml',
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
