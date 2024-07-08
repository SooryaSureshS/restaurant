# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

# for Animations you need to extract the website_animate Module in the addons path

{
    'name': 'Website tips',
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
    ],

    'data': [
        'data/data.xml',
        'views/views.xml',
        'views/assets.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,

}
