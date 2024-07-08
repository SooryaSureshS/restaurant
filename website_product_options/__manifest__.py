{
    'name': 'Website Product Options',
    'version': '14.0',
    'category': 'Website',
    'summary': 'Website Product Options',
    'description': """ Extra Product Options for Different Products
    """,
    'sequence': 1,
    'depends': ['website', 'website_sale', 'sale_product_configurator','stock'],
    'author': 'Socius IGB',
    'data': [
        'security/record_security.xml',
        'security/ir.model.access.csv',
        'views/product.xml',
        'views/product_options_inherit.xml',
        'views/assets.xml',

    ],
    'qweb': ['views/hide_free_product.xml'],

    'images': [
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3'
}
