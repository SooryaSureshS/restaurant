# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Pos Default Qty Disable',
    'version': '14',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': '',
    'description': """

This module remove pos default Qty.

""",
    'depends': ['point_of_sale'],
    "data": ["views/assets.xml"],
    # "qweb": ["static/src/xml/NumpadWidgets.xml"],
}
