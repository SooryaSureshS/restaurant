# -*- coding: utf-8 -*-

{
    'name': 'POS Session Access',
    'version': '1.0',
    'category': '',
    'sequence': 1,
    'summary': 'POS Session Access',
    'description': """pos cook logout""",
    'depends': ['base', 'point_of_sale', 'pos_order_delete', 'pos_session_summary'],
    'data': [
        'security/ir.model.access.csv',
        'views/SessionPrivilegePOS.xml',
    ],
    'qweb': [
    ],
    'installable': True,
}
