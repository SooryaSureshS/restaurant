# -*- coding: utf-8 -*-
{
    'name': "hr_scheduling",
    'author': "Socius IGB",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'resource', 'hr', 'hr_employee_shift', 'hr_skills', 'hr_contract','hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'security/scheduling_security.xml',
        'views/templates.xml',
        'views/resource.xml',
        'views/hr_employee.xml',
        'views/recurring_leave.xml',
        'report/custom_header.xml',
        'report/overdue_report_templates.xml',
        'report/overdue_report.xml',
    ],

}
