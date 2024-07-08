# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Timesheet Approval",
    "author": "Softhealer Technologies",
    "website": "http://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Human Resources",
    "license": "OPL-1",
    "summary": "Timesheet Manager Approve Timesheets Module, Timesheet Rejection By Timesheet Manager, Bulk Timesheet Reject, All Timesheet Reject In Single Click Odoo",
    "description": """Currently, in odoo timesheet submitted directly without any conformation so to restrict this, we made a module to approve user timesheet. The timesheet approval module will allow to approve or reject timesheet by the managers. When timesheet create that will put it in the 'Draft' state by default and then after the manager can move in approve or reject state. This module gives the facility to the manager to select multiple timesheets means mass approval or mass reject timesheets. Once the timesheet is approved or rejects the person gets an email notification.""",
    "version": "14.0.1",
    "depends": [
        "project",
        "hr",
        "hr_timesheet",
        "sale_timesheet"
    ],
    'images': ['static/description/background.png', ],
    "application": True,
    "data": [
        'security/ir.model.access.csv',
        'data/sh_approve_timesheet_mail_template.xml',
        'data/sh_reject_timesheet_mail_template.xml',
        'views/sh_timesheet_view.xml',
        'wizard/sh_timesheet_reject_wizard_view.xml',
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url": "https://youtu.be/A6XPh0KQpPU",
    "price": 50,
    "currency": "EUR"
}
