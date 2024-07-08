# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    "name": "Sale Return",
    "version": "16.0.1.1",
    "summary": """
        Sale Return Module allows user to efficiently track and manage Sale order along with their delivery returns, user can return products from Sale order itself without interacting with stock picking.
        Sale Return | Return Order | Sale Picking | In Picking | Return Picking | Return Sale Order | Sale RMA
    """,
    "description": """
Sale Return
====================
Using this Module user can return sale order directly from sale and stocks are managed automatically.
    Key Features
    -> Create Return
    -> Manage Stock
    -> Create Return Picking
""",
    "category": "Sales/Sales",
    "author": "Kanak Infosystems LLP.",
    "website": "https://www.kanakinfosystems.com",
    "images": ["static/description/banner.jpg"],
    "depends": ["sale_management", "stock", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "data/return_sequence_data.xml",
        "wizard/knk_sale_return_wizard_views.xml",
        "views/sale_views.xml",
        "views/sale_order_return_views.xml",
        "templates/sale_return.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            'knk_sale_return/static/src/js/returnProduct.js',
        ]
    },
    "license": "OPL-1",
    "installable": True,
    "application": False,
    "auto_install": False,
    "currency": "EUR",
    "price": "50",
}
