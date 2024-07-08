{
    'name': 'Website Orders',
    'version': '13.0',
    'category': 'Website',
    'summary': 'Website Order',
    'description': """
    """,
    'sequence': 1,
    'depends': ['website_sale', 'portal', 'sale'],
    'author': 'Socius IGB',
    'data': [
        'views/assets.xml',
        'views/order_history.xml',
        'views/sale_order_communication.xml',
    ],
    'qweb': [
        # 'static/src/xml/feedback.xml',
    ],
    'images': [
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3'
}
