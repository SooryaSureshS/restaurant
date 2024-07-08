# -*- coding: utf-8 -*-

{
    'name': 'pos session inherit',
    'version': '1.0',
    'category': '',
    'sequence': 1,
  
    'depends': ['base', 'point_of_sale','pos_summary_backend'],
    'data': [
        'views/pos_session_inherit.xml',
    ],
    'qweb': [
    ],
    'installable': True,
}
