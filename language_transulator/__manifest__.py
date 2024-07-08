# -*- coding: utf-8 -*-
{
    'name': 'Website Language Translation',
    'version': '15.0.1.0.1',
    'sequence': 0,
    'category': 'Website',
    "author": "Socius IGB Pvt.Ltd.",
    "website": "http://www.socius.com",
    'license': 'LGPL-3',
    'support': 'socius@services.com',
    'description':"""
               Website Language Translation
        """,
    'depends': ['base', 'product', 'sale', 'website_sale', 'sale_management', 'website',
                'point_of_sale', 'auth_oauth'],
    'assets': {
        'web.assets_frontend': [
            'language_transulator/static/src/js/jquery.translate.js',
            'language_transulator/static/src/js/transulate.js',
            'language_transulator/static/src/style.css',
        ],

    },
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/website_lang.xml'
    ],
    'external_dependencies': {
        'python': ['py-translate','translate'],
    },

    # 'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
