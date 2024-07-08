{
    'name': "Yield Summary Report",

    'category': 'Uncategorized',
    'version': '',

    # any module necessary for this one to work correctly
    'depends': ['base','web','sale','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'reports/custom_header.xml',
        'wizards/yield_summary_report_wizard.xml',
        'reports/report.xml',
        'reports/yield_summary_template.xml'

    ],
    # only loaded in demonstration mode
    'qweb': [

    ],
    'installable': True,

}
