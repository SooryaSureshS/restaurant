# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Safe Count',
    'version': '1.0',
    'author': 'SIGB',
    'category': 'Safe Counts',
    'summary': """Counting the Amount""",
    'description': """

        Counting the cash using Safe counts

    """,
    'depends': [],
    'data': [

        'security/safe_count_security_groups.xml',
        'security/ir.model.access.csv',
        'views/safe_count_view.xml',
        'reports/safe_count_report.xml',
        'reports/safe_count_report_template.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,

}
