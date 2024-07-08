
{
    'name': 'Active Campaign Integration',
    'version': '12.0.1.0.0',

    'author': 'Socius',
    'license': 'AGPL-3',
    'depends': ['base','sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/active_campaign_configuration.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'auto_install': False,
}
