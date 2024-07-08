# -*- coding: utf-8 -*-
{
    'name': "PMS Website",
    'sequence': -100,
    'summary': "Property Management System Website",
    'author': "SIGB",
    'version': '15.0.1.0.1',
    'depends': ['base', 'website', 'property_rental_mgt_app', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/login.xml',
        'views/header.xml',
        'views/footer.xml',
        'views/homepage.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pms_website/static/src/css/login.css',
            'pms_website/static/src/css/header.css',
            'pms_website/static/src/css/homepage.css',
        ],
        'web.assets_qweb': [],
    }
}
