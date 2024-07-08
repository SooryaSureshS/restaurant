{
    'name': 'Pizza & Pasta Reporting',
    'version': '14.0',
    'summary': 'Pizza & Pasta Reporting',
    'description': """
    """,
    'sequence': 1,
    'depends': ['sale','stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/pizza_pasta_report.xml',
        'views/pizza_pasta_template.xml'
             ],
    'images': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}