{
    'name': 'Pos Category Report',
    'version': '14.0',
    'summary': 'Report for Pos Category',
    'description': """
    """,
    'sequence': 1,
    'depends': ['sale','stock'],
    'data': ['security/ir.model.access.csv','wizard/pos_category.xml','views/pos_category_report.xml'
             ],
    'images': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}