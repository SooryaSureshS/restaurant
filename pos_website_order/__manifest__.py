{
    'name': 'POS website',
    'version': '1.0.1',
    'category': 'Point of Sale',
    'description': """
    User can purchase giftcard, use giftcard and also recharge giftcard.
""",
    'author': "SIGB",

    'version': '1.0.1',
    'depends': ['website',
        'website_sale',
        'pos_restaurant',
        'table_booking',
        'website_reservation',
        'point_of_sale',],
    'data': [
    ],
    'installable': True,
    'auto_install': False,
}