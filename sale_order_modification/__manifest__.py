# -*- coding: utf-8 -*-

{
    'name': 'Sales Order Modification',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 6,
    'summary': 'Sales Order Modification ',
    'description': """
        Sales Order Modification.
    """,
    'depends': ['sale'],
    'data': [
        'views/sale_order.xml',
        'views/order_line.xml',
        'views/sale_report.xml',
        'views/view.xml',
        'views/sale_customer_details.xml',
    ],
    'installable': True,
}
