# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Brand Splitting',
    'category': 'Website/eCommerce',
    'summary': """Split sale order based on brand.""",
    'version': '16.0.1.0.0',
    'author': 'SIGB',
    'website': 'www.sociusus.com',
    'data': [
        'views/res_config_settings_views.xml',
        'views/sale_order_view.xml',
        'views/shop_confirmation.xml',
    ],
    'depends': ['base', 'sale', 'emipro_theme_base'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
