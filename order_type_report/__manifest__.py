# -*- coding: utf-8 -*-

{
    'name': 'POS tender type report',
    'version': '1.0',
    'category': '',
    'sequence': 1,
    'summary': 'POS Tender Report',
    'description': """Pos Tender Report""",
    'depends': ['base', 'point_of_sale','website_delivery_type','store_sales_dashboard'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/order_tender.xml',
        'views/tender_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
}
