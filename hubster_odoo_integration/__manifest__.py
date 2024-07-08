# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Odoo Hubster Integration",
    'summary': """This Module integrates Hubster with Odoo""" ,
    'version': '14.0.0.0',
    'category': 'eCommerce',
    'author': 'Produktive Consulting Services Pte. Ltd.',
    'description': 'This module is used to perform integration of hubster with odoo',

    'depends': ['base', 'website_sale', 'kitchen_order'],
    'data'   : [
                'data/hubster_data.xml',
                'views/hubster_store_view.xml',
                'security/ir.model.access.csv'
    		],

}