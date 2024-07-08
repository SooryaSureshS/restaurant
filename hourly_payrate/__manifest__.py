{
    'name': "Hourly Payrate",

    'category': 'Uncategorized',
    'version': '',

    'depends': ['base','web','sale','stock','contacts','hr_payroll_community','hr', 'hubster_odoo_integration'],

    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/attendance.xml',

    ],

    'installable': True,

}
