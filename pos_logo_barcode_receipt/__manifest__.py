# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Pos Logo Barcode Receipt',
    'version': '10.0.0.1',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'maintainer': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'category': 'Point Of Sale',
    'description': 'This module provide company logo and barcode in receipt.',
    'summary': 'Print company logo and barcode in pos receipt',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_logo_barcode_receipt_view.xml',
        'views/templates.xml',
    ],
    'qweb': ['static/src/xml/pos_logo_barcode_receipt.xml'],
    'images': ['static/description/pos_logo_barcode.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 29,
    'currency': 'EUR',
}
