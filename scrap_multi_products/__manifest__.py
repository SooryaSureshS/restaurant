# -*- coding: utf-8 -*-
{
    'name': "Scrap Multiple Products",
    'summary': '''
        Create a Bulk Scrap Operation and Scrap Multiple Products At Once.''',
    "license": "OPL-1",
    'author': 'Socius IGB',
    'maintainer': 'Socius IGB',
    'category': 'Stock Management',
    'version': '0.1',
    'depends': ['stock'],
    'data': [
        'views/scrap_product_view.xml',
        'views/stock_scrap.xml',
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv'
    ],
    'images': ['static/description/scrap_multi_products_app_coverpage.png'],
    'currency' : 'EUR',
    'price' : 0.00,
    'installable': True,
    'auto_install': False,
    'application': True,
}
