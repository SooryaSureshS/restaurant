# -*- coding: utf-8 -*-
{
    'name': "pos_logo_customization",

    'summary': """point of sale logo""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",


    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale','pos_logo_barcode_receipt'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml'
    ],
    'qweb': ['static/xml/orderReceipt.xml'],
}
