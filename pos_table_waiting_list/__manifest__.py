# -*- coding: utf-8 -*-
{
    'name': 'POS Table Waiting List',
    'category': 'Theme/eCommerce',
    'version': '14.0.0.4',
    'author': 'Socius',
    'website': 'http://www.jithesh.com',
    'summary': '''POS Table Waiting List''',
    'description': """POS Table Waiting List""",

    'depends': [
        'pos_restaurant',
        'point_of_sale',
        'pos_booking',
        'pos_open_orders',
    ],

    'data': [
        'views/data.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/reservation_mail.xml',
        'views/waiting_list.xml',
        'views/reservation.xml'
        # 'views/res_users.xml',
        # 'views/booking_config.xml',
        # 'views/sale_order.xml',
    ],
    'qweb': [
        'static/src/xml/add_to_wait_list.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

}
