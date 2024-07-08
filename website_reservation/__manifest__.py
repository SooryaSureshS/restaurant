# -*- coding: utf-8 -*-
{
    'name': "website_reservation",

    'summary': """
        website reservation""",

    'description': """
        used for backend configuration website
    """,

    'author': "Sigb jj",

    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website', 'pos_restaurant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/reservation_mail.xml',
        'views/cancel_reservation.xml',
    ],
    # only loaded in demonstration mode
}
