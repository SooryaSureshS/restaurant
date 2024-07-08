# -*- encoding: utf-8 -*-
{
    "name": "Employee Access",
    "version": "14.0",
    "author": "SIGB",
    "sequence": 0,
    "depends": ['base', 'mail', 'organize', 'hide_menu_user'],
    "data": [
        # 'security/security.xml',
        'datas/employee_group.xml',
        'views/published_scheduling.xml',
    ],
    "installable": True,
    "application": False,
}