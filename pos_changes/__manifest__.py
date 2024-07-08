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
    'name': 'Pos Changes',
    'version': '14.0.0.1',
    'license': 'Other proprietary',
    'category': '',
    'images': ['static/description/cover.jpg',],
    'description': """
    """,
    'author': 'Uncannycs',
    'maintainer': 'Uncannycs',
    'website': 'http://www.uncannycs.com',
    'depends': ['point_of_sale','pos_mcd_open_order'],
    'data': [
        'views/res_company_view.xml',
        'views/assets.xml',
        'views/sale_details_report.xml'
    ],
    'demo': [
    ],
    'test': [
    ],
    'qweb': [
        'static/src/xml/receipt.xml',
    ],
    'installable': True,
    'auto_install': False,
}
