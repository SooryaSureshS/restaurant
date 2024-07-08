# -*- coding: utf-8 -*-
{
    'name': 'Website qrcode Order Merge',
    'category': 'Theme/eCommerce',
    'version': '14.0.0.4',
    'author': 'Socius',
    'website': 'http://www.jithesh.com',
    'summary': '''Website Qr Code Merge Order''',
    'description': """Theme Qr order mergee""",

    'depends': [
        'website_qr_code',
        # 'website',
        # 'website_sale',
        # 'theme_wineshop',
        # 'ql_twilio_sms',
        # 'kitchen_order',
        # 'website_delivery_type',
        # 'sale_order_modification',
        # 'pos_restaurant'
    ],

    'data': [
        # 'data/data.xml',
        'security/ir.model.access.csv',
        'views/config.xml',
        'views/assets.xml',
        # 'views/assets.xml',
        # 'views/tracking.xml',
        # 'views/base_config.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,

}
