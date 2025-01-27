{
    'name': 'Social Media Base',
    'version': '14.0.1.0.0',
    'category': 'Extra Tools',
    'author': 'SIGB',
    'website': 'https://www.sociusus.com',
    'license': '',
    'summary': 'Social Media Base Module',
    'description': 'Social Media Base Module',

    'depends': ['base'],
    'license': 'AGPL-3',
    'data': [
        #
        'security/ir.model.access.csv',
        # 'data/ir_cron_data.xml',
        'views/assets.xml',
        'views/social_media_menu.xml',
        'views/social_media_type_views.xml',
        'views/social_media_account_views.xml',
        'views/social_media_post.xml',
        'views/social_media_error_view.xml',
        'views/social_media_dashboard_view.xml',
        'views/res_config_settings_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}