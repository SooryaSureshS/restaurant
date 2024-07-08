# -*- coding: utf-8 -*-

{
    'name': 'POS SessionReports',
    'version': '13',
    'category': 'POS',
    'summary': 'POS Session Reporting',
    'sequence': '10',
    'depends': ['pos_session_summary'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/monthly_report_wizard.xml',
        'wizards/monthly_report_template.xml',

    ],

}
