{
    'name': 'Pos Offline Order Managements',
    'version': '14.0',
    'category': 'Sales/Point of Sale',
    'sequence': 7,
    'summary': 'Point of sale Offline Managements ',
    'description': """ Point of sale Customer Offline Managements""",
    'depends': ['point_of_sale'],
    'data': [
        # 'views/pos_loyalty_views.xml',
        # 'views/pos_loyalty_config_views.xml',
        # 'security/ir.model.access.csv',
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/HeaderInherit.xml',
        'static/src/xml/offlinePopup.xml',
    ],
    'installable': True,

}
