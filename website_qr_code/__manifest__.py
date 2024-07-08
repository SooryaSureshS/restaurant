# -*- coding: utf-8 -*-
{
    'name': 'Website qrcode shopping',
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
        'ql_twilio_sms',
        'kitchen_order',
        'website_delivery_type',
        'sale_order_modification',
        'pos_restaurant'
    ],

    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/assets.xml',
        'views/tracking.xml',
        'views/base_config.xml',
    ],
    'external_dependencies': {"python": ['qrcode']},
    'installable': True,
    'auto_install': False,
    'application': False,

}
