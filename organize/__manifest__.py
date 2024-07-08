# -*- coding: utf-8 -*-
{
   'name': "Scheduling",
   'version': '1.0',
   'depends': ['base','hr', 'backend_gant', 'employee_gantt', 'employee_shift_approval'],
   'data': [
       'security/organize_security.xml',
       'security/ir.model.access.csv',
       'wizard/organize_send_views.xml',
       'wizard/organize_copy_week_views.xml',
       'wizard/organize_report.xml',
       'wizard/organize_action.xml',
       'wizard/organize_action_duplicate.xml',
       'wizard/organize_schedule_time_off.xml',
       'views/assets.xml',
       'views/organize_report.xml',
       'views/hr_views.xml',
       'views/organize_template_views.xml',
       'views/organize_views.xml',
       'views/organize_report_views.xml',
       'views/res_config_settings_views.xml',
       'views/organize_templates.xml',
       'views/note_views.xml',
       'data/organize_cron.xml',
       'data/mail_data.xml',
   ],
   'application': True,
   'qweb': [
       'static/src/xml/organize_gantt.xml',
   ]
}


