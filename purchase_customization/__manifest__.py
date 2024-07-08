# -*- coding: utf-8 -*-
{
    'name': "Purchase Customization",
    'summary': """
        Purchase Module Changes""",
    'description': """
        Purchase module changes
    """,
    'version': '0.1',
    'depends': ['base', 'purchase', 'stock'],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/week_end_po.xml',
        'views/purchase_view.xml',
        'views/product_view.xml',
        'report/purchase_reports.xml',
        'report/purchase_quotation_templates.xml',
    ],
    'qweb': [
        "static/src/xml/purchase_dashboard.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
