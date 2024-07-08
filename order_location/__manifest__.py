{
    'name': 'Website Order Location Filter',
    'version': '14.0',
    'category': 'Website',
    'summary': 'Website Order',
    'description': """
    """,
    'sequence': 1,
    'depends': ['website', 'website_sale', 'base', 'base_geolocalize'],
    'author': 'Socius IGB',
    'data': [
        'views/base_config_view.xml',
        'views/address_template.xml',
        'security/ir.model.access.csv',

    ],
    'images': [
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3'
}
