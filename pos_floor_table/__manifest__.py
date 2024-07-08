# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Uncannycs LLP
#    Copyright (C) 2020 Uncannycs LLP (<http://uncannycs.com>).
#
##############################################################################
{
    'name': 'Pos Floor Table',
    'version': '14.0.0.1',
    'license': 'Other proprietary',
    'category': '',
    'description': """
    """,
    'author': 'Uncannycs',
    'maintainer': 'Uncannycs',
    'website': 'http://www.uncannycs.com',
    'depends': ['point_of_sale','pos_restaurant'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/pos_floor_table.xml',
        'views/restaurant_floor.xml',
    ],
    'installable': True,
    'auto_install': False,
}
