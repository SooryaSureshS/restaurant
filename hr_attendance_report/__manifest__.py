{
    'name': "HR Attendance Report",

    'category': 'Uncategorized',
    'version': '',

    'depends': ['base','web','sale','stock','contacts','hr_payroll_community','hr','hr_attendance'],

    'data': [
        'views/views.xml',
        'report/report.xml',
    ],

    'installable': True,

}
