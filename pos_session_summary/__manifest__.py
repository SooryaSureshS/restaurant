# -*- coding: utf-8 -*-

{
    'name': 'POS Summary Report',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 1,
    'summary': 'POS Session-wise Report',
    'description': """
        POS Session-wise Report
    """,
    'depends': ['point_of_sale'],
    'data': [
        'views/assets.xml',
        'views/session_summary.xml',
        'views/report_template.xml',
        'views/report_pos_summary.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        'static/src/xml/SummaryButton.xml',
        'static/src/xml/reportScreen.xml',
    ],
    'installable': True,
}
