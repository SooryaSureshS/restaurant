{
    'name': "Stock Variation Report",

    'category': 'Uncategorized',
    'version': '',

    # any module necessary for this one to work correctly
    'depends': ['base','web','sale','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/stock_variation_report_wizard.xml',
        'reports/report.xml',
        'reports/custom_header.xml',
        'reports/stock_variation_template.xml'

    ],
    # only loaded in demonstration mode
    'qweb': [

    ],
    'installable': True,

}
