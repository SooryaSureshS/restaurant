# -*- coding: utf-8 -*-
{
    'name': "Operational Report",

    'summary': """
        Operational Excel Report""",

    'description': """
        This module allows to generate operational excel report
    """,

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','sale','report_xlsx'],

    'data': [
        'security/ir.model.access.csv',
        'views/report.xml',
    ],
    
}
