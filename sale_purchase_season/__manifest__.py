# -*- coding: utf-8 -*-
{
    'name': 'Sale and Purchase Season',
    'category': 'Sale',
    'summary': """Sale and Purchase Season.""",
    'version': '16.0.1.1.0',
    'author': 'SIGB',
    'website': 'www.sociusus.com',
    'data': [
        'security/ir.model.access.csv',
        'datas/season_cron.xml',
        'views/purchase_view.xml',
        'views/sale_season_view.xml',
        'views/menu_actions.xml',
    ],
    'depends': ['base', 'sale', 'purchase'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
