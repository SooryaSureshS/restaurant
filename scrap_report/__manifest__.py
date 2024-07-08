{
    'name': 'Scrap Report',
    'version': '14.0',
    'summary': 'Report for scrap Order',
    'description': """
    """,
    'sequence': 1,
    'depends': ['sale','stock'],
    'data': ['security/ir.model.access.csv','wizard/stock_scrap.xml','views/scrap_report.xml'
             ],
    'images': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}