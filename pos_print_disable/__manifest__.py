# -*- coding: utf-8 -*-

{
    'name': "POS Disable Print",
    'summary': """Avoid printing of specific product from KVS receipt""",
    'version': '1.0',
    'category': '',
    'sequence': 1,
    'description': """Avoid printing of specific product fromKVS receipt""",
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/product_template.xml',
    ],
    'qweb': [
    ],
    'installable': True,
}
