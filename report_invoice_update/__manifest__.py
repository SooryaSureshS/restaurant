{
    'name': "Report Template custom",

    'summary': """Report Template custom update""",

    'description': """
       Report Template custom
    """,
    'category': 'Uncategorized',
    'version': '',

    # any module necessary for this one to work correctly
    'depends': ['base','web', 'account'],

    # always loaded
    'data': [
        'views/template.xml',
        'views/list_view_load.xml'
    ],
    # only loaded in demonstration mode
    'qweb': [

        ],
    'installable': True,

}
