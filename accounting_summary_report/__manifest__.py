{
    'name': "Accounting Summary Report",

    'category': 'Uncategorized',
    'version': '',

    'depends': ['base','web','sale','stock'],

    'data': [
        'security/ir.model.access.csv',
        'wizards/accounting_summary_report_wizard.xml',
        'reports/report.xml',
        'reports/custom_header.xml',
        'reports/accounting_summary_template.xml'

    ],
    'qweb': [

    ],
    'installable': True,

}
