{
    'name': 'Customer Loyalty Program for POS',
    'version': '14.0',
    'category': 'Sales/Point of Sale',
    'sequence': 7,
    'summary': 'Point of sale Customer Loyalty Program ',
    'description': """ Point of sale Customer Loyalty Program""",
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_loyalty_views.xml',
        'views/pos_loyalty_config_views.xml',
        'security/ir.model.access.csv',
        'views/pos_loyalty_templates.xml',
    ],
    'qweb': [
        'static/src/xml/OrderReceipt.xml',
        'static/src/xml/RewardButton.xml',
        'static/src/xml/PointsCounter.xml',
        'static/src/xml/Loyalty.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'AGPL-3',
}
