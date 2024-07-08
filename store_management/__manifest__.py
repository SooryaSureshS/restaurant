# -*- coding: utf-8 -*-

{
    'name': "Store Mnagement",
    'summary': """Select Customer Primary Store""",
    'version': '1.0',
    'category': '',
    'sequence': 1,
    'description': """Select Customer Primary Store""",
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/partner.xml',
        'views/auth_signup_extend_views.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
    ],
    'installable': True,
}
