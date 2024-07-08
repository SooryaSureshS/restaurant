{
    'name': "Promotion and Coupon Program Report",

    'category': 'Uncategorized',
    'version': '',

    # any module necessary for this one to work correctly
    'depends': ['base','web','sale','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/promotion_and_coupon_report_wizard.xml',
        'reports/custom_header.xml',
        'reports/report.xml',
        'reports/promotion_coupon_template.xml'

    ],
    # only loaded in demonstration mode
    'qweb': [

    ],
    'installable': True,

}
