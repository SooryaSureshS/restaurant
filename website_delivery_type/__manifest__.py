{
    'name': 'Website Order Delivery Type',
    'version': '14.0',
    'category': 'Website',
    'summary': 'Website Order Delivery Type',
    'description': """
    """,
    'sequence': 1,
    'depends': ['website', 'website_sale', 'base', 'website_sale_delivery', 'website_sale_hour'],
    'author': 'Socius IGB',
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/delivery_details.xml',
        'views/address_template.xml',
        'views/confirm_template.xml',
        'views/order_confirm_page.xml',
        'views/kerbside_order_address_update.xml',
        'views/report_feedback.xml',
        'views/res_company.xml',

    ],
    'images': [
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3'
}
