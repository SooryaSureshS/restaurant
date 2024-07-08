# -*- coding: utf-8 -*-
# Email: shivoham.odoo@gmail.com
{
    'name': 'Change multiple product tax | Mass editing in product tax | Change product tax in multiple way',
    'version': '14.0',
    'category': 'Product',
    'license': 'LGPL-3',
    'author': 'Shivoham',
    'price': '6.0',
    'currency': 'USD',
    'support': 'shivoham.odoo@gmail.com',
    'summary': """This module allow you to change multiple product taxes at a time. Also you can change the product tax 
                in multiple way and you also change customer tax and vendor tax of product.""",
    'sequence': '1',
    'description': """
            Change Multiple Product taxes at a time in multiple way.
    """,
    'depends': ['stock', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/change_product_tax_form_view.xml',
        'views/change_product_tax_menu.xml',
    ],
    'images': [
#                 'static/description/icon.png',
                'static/description/banner.gif'   
              ],
    'application': True,
    'installable': True,
    'auto_install': False
}
