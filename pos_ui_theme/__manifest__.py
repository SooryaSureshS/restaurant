# -*- coding: utf-8 -*-
# odoo v14
{
    'name': 'POS Theme',
    'version': '1.0.1',
    'category': 'Point of Sale',
    'summary': 'Easily Setup 7 different color POS UI Theme',
    'description': "This POS Module provides you better look of POS User Interface. In this theme module include 7 different color theme for POS UI. This is a Completely User Friendly and Easily setup.",
    'license': 'OPL-1',
    'price': 25.99,
    'currency': 'EUR',
    'images': ['static/description/main_screenshot.jpg'],
    'author': "Icon TechSoft Pvt. Ltd.",
    'website':"https://icontechnology.co.in",
    'support':  'team@icontechnology.in',
    'maintainer': 'Icon TechSoft Pvt. Ltd.',
    'depends': ['point_of_sale','base','web_editor'],
    'data': [
        'views/inherit_pos_config.xml',
        'views/pos_template_css.xml',
    ],    
    'installable': True,
    'application': True,
    
}
