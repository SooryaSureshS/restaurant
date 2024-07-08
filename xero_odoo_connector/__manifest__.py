# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "Xero Connector OAuth2.0",
    "version": "14.0.0.7",
    "category": "Accounting",
    "summary": "Allow to sync data between odoo and xero",
    "description": """
    Sync all accounting related data from odoo to xero and also use same module
    to sync from xero to odoo.
    """,
    "author": "Warlock Technologies Pvt Ltd.",
    "website": "http://warlocktechnologies.com",
    "support": "support@warlocktechnologies.com",
    "depends": ["sale_management", "sale_stock", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/xero.xml",
        "views/partner.xml",
        "views/product.xml",
        "views/account.xml",
        "views/account_move.xml",
        "views/menus.xml",
    ],
    "images": ["images/screen_image.png"],
    "price": 300,
    "currency": "USD",
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    "external_dependencies": {
        "python": ["requests_oauthlib"],
    },
}
