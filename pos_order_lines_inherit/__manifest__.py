# -*- coding: utf-8 -*-

{
    'name': 'POS Order Lines Inherit',
    'version': '14.0',
    'category': 'POS',
    'summary': 'Point Of Sale',
    'description': """
    """,
    'sequence': 1,
    'depends': ['kitchen_order'],
    'author': 'Produktive Consulting Pte. Ltd.',
    'data': [
        'security/pos_security_view.xml',
        'views/pos_order_view.xml'
    ],

    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3'
}