# -*- coding: utf-8 -*-
{
    'name': "pos_order_type_inherit",

    'depends': ['base','pos_order_type','point_of_sale','kitchen_order'],

    'data': [
        'views/views.xml',

    ],
    'qweb': [
        'static/src/xml/payment_screen_inherit.xml',
    ],
}
