{
    'name': 'Firebase Push Notification',
    'summary': """""",
    'version': '15.0.1.0.0',
    'description': """""",
    'depends': ['base','website','mask_cutomization'],
    'license': 'AGPL-3',
    'assets': {
        'web.assets_frontend': [
            'firebase_push_notification/static/src/js/firebaswe.js',
            # 'https://www.gstatic.com/firebasejs/7.14.6/firebase-app.js',
            # 'https://www.gstatic.com/firebasejs/7.14.6/firebase-messaging.js',
        ],
        # 'web.assets_qweb': [
        #     'mask_cutomization/static/src/xml/template.xml',
        # ],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/fpn_notification.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
