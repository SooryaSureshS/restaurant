{
    'name': "Employee Shift Approval",

    'category': 'Uncategorized',
    'version': '',
    'depends': ['base','hr','hr_timesheet','hr_contract','hr_attendance','report_xlsx'],

    'data': [
        'data/cron.xml',
        'views/employee_timesheet_details_view.xml',
        'security/ir.model.access.csv',
        'reports/report.xml',
        'reports/daily_timesheet_summary_template.xml',
        'wizards/timesheet_summary_report_wizard.xml',
        'reports/timesheet_summary.xml'

    ],
    'qweb': [

    ],
    'installable': True,

}
