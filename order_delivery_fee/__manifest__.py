{
    'name': 'Website order delivery fee',
    'version': '14.0',
    'category': 'Website',
    'summary': 'Website order delivery fee',
    'description': """
    """,
    'sequence': 1,
    'depends': ['sale','website_delivery_type','website_first_order_discount','base'],
    'data': ['views/sale_order.xml'

             ],
    'images': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
