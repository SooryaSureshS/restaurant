{
    'name': 'POS Sales Details Excel Report',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Excel Report',
    'description': """
        This module allows the user to print pos sales details excel report 
    """,
    'depends': ['base', 'point_of_sale', 'sale'],

    'data': [
        'report/report.xml',
        'views/views.xml',
    ],

    'installable': True,
}
