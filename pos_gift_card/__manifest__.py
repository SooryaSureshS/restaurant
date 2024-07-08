{
    'name': 'POS Gift Card',
    'version': '1.0.1',
    'category': 'Point of Sale',
    'summary': 'This module allows user to purchase giftcard,use giftcard and also recharge giftcard.',
    'description': """
    User can purchase giftcard, use giftcard and also recharge giftcard.
""",
    'author': "SIGB",

    'version': '1.0.1',
    'depends': ['web', 'point_of_sale', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets_gift_card.xml',
        'views/point_of_sale.xml',
        'views/gift_card.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'auto_install': False,
}