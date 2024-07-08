# -*- coding: utf-8 -*-
{
    'name': "automatic_session_close",

    'summary': """Automatic Session Close""",

    'description': """
        Used to close sessions on a particular time range
    """,
    'author': 'SIGB-JJ',

    'category':'Sales/Point of Sale',
    'version': '14.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
}
