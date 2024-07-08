{
    'name': "Ending Inventory Report",

    'category': 'Uncategorized',
    'version': '',

    'depends': ['base','web','sale','stock'],

    'data': [
        'views/product_template_inherit.xml',
        'views/product_category_type.xml',
        'security/ir.model.access.csv',
        'wizards/ending_inventory_report_wizard.xml',
        'reports/report.xml',
        'reports/custom_header.xml',
        'reports/ending_inventory_template.xml'

    ],
    'qweb': [

    ],
    'installable': True,

}
