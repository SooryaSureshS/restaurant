{
    'name': "loyalty_pos",

    'summary': """Loyality Pos""",

    'description': """
        Long description of module's purpose
    """,
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale','website_loyalty_management'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [
            'static/src/xml/Counter.xml',
            'static/src/xml/Loyalty.xml',
            'static/src/xml/RewardButton.xml',
        ],
    'installable': True,

}
