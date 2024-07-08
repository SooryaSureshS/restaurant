# -*- coding: utf-8 -*-

{
    'name': 'User Approval',
    'summary': """User approval""",
    'version': '16.0.1.0.0',
    'author': 'SIGB',
    'website': 'www.sociusus.com',
    'depends': ['base'],
    'data': [
        'views/auth_signup.xml',
        'views/res_partner_view.xml',
        'views/res_user_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'user_approval/static/src/css/hideWrapwrap.css',
            'user_approval/static/src/js/redirectPublicUser.js',
            'user_approval/static/src/js/signupForm.js',
        ]
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
