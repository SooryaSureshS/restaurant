# -*- coding: utf-8 -*-

{
    'name': 'Pos Paper Cost',
    'version': '14.0.0',
    'category': 'Point of Sale',
    'sequence': 1,
    'summary': '',
    'description': """ """,
    'depends': ['point_of_sale','product', 'pos_order_type'],
    "data": [
        'security/ir.model.access.csv',
        'views/product.xml',
        'data/product_data.xml',
        'views/paper_cost_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
