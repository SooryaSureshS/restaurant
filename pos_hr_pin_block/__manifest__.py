{
    'name': 'Pos hr Pin block POS',
    'version': '14.0',
    'category': 'Sales/Point of Sale',
    'sequence': 7,
    'summary': 'Point of sale Pin Block ',
    'description': """ Point of sale Pin Block Program""",
    'depends': ['point_of_sale','pos_hr'],
    'data': [
        'views/assets.xml',
    ],

    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
