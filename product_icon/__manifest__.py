# -*- coding: utf-8 -*-
{
    'name': "Product Icon",
    'summary': """
        Product Icon""",
    'description': """
        Product Icon
    """,
    'version': '0.1',
    'depends': ['base', 'product','product_name_modification','website_sale', 'theme_wineshop','bi_website_add_product'],
    'license': 'AGPL-3',
    'data': [
        'views/view.xml',
        'views/icon.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
