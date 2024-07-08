# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Raw Material Stock Update",
    'summary': """This Module is used to update stock of raw materials""",
    'version': '14.0.0.0',
    'category': 'stock',
    'author': 'SIGB',
    'description': 'This Module is used to update stock of raw materials based on daily,weekly,monthly.',

    'depends': ['base', 'bi_website_add_product', 'stock', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/new_stock_inventory.xml',
        'views/product.xml',
        'views/stock_update.xml',
    ],

}
