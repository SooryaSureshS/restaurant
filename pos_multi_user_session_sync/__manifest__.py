# -*- encoding: utf-8 -*-
{
    "name": "Multi user single session sync",
    "version": "14.0.0.0.1",
    "author": "SIGB",
    "sequence": 0,
    "depends": ['base', 'point_of_sale', 'pos_restaurant'],
    "data": [
        'views/assets.xml',
        'views/res_users.xml',
        'views/pos_config.xml',
    ],
    'qweb': [],
    "installable": True,
    "application": False,
}
