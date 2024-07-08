{
    'name': 'Check Out Order Note',
    'version': '14.0',
    'category': 'Website',
    'summary': 'Check Order Note Type',
    'description': """
    """,
    'sequence': 1,
    'depends': ['website', 'website_sale', 'base', 'website_sale_delivery','website_delivery_type','website_product_options'],
    'author': 'Socius IGB',
    'data': [
        'views/view.xml',
        'views/assets.xml',
        'views/sale_order.xml',
        # 'views/delivery_details.xml',
        # 'views/address_template.xml',
    ],
    'images': [
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3'
}
