# -*- coding: utf-8 -*-
{
    'name': 'Sale No Quotation',
    'category': 'Website/eCommerce',
    'summary': """When an order is completed through website, the corresponding
     order status changes directly to 'sale' (confirming sale order)""",
    'version': '16.0.1.0.0',
    'author': 'SIGB',
    'website': 'www.sociusus.com',
    'data': [
        'security/security.xml',
        'views/menus.xml',
        'views/res_config_settings_views.xml',
        'views/sale_portal_templates.xml',
    ],
    'depends': [
        'website',
        'website_sale',
        'sale',
        'portal',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
