# -*- coding: utf-8 -*-

{
    'name': 'POS Summary Backend',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 1,
    'summary': 'POS Session-wise Report',
    'description': """
        POS Session-wise Report
    """,
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'report/cashcollection_report.xml',
        'report/cashcollection_report_templates.xml',
        'report/custom_header.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/views.xml',
        'views/employee_pin_wizard.xml',
        'views/cash_collection.xml',
        'views/cash_collection_report.xml',

    ],
    'qweb': [
        'static/src/xml/closeSummary.xml',
        'static/src/xml/chromeInherit.xml',
    ],
    'installable': True,
}
