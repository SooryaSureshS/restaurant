{
    'name': "Quality Cost Report",

    'category': 'Uncategorized',
    'version': '',

    # any module necessary for this one to work correctly
    'depends': ['base','web','sale','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/quality_cost_report_wizard.xml',
        'reports/report.xml',
        'reports/quality_cost_template.xml'

    ],
    # only loaded in demonstration mode
    'qweb': [

    ],
    'installable': True,

}
