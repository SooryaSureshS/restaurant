# -*- coding: utf-8 -*-
{
    'name': "Odoo Multi Company",
    'summary': """
        odoo multi company""",
    'description': """
        odoo_multi_company
    """,
    'version': '14.0.1',
    'depends': ['product','point_of_sale'],
    'license': 'AGPL-3',
    'data': [
        'security/record_security.xml',
        'views/product_view.xml',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
