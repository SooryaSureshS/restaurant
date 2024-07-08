# -*- coding: utf-8 -*-
{
    'name': "POS Size Category",

    'summary': """
        This module is for POS Size Category""",

    'description': """
        This module is for POS Size Category
    """,

    'category': 'Uncategorized',
    'version': '14.0',

    'depends': ['base','point_of_sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/product.xml',
        'views/pos_size_categ.xml',
        'views/pos_assets.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
}
