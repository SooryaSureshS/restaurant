# -*- coding: utf-8 -*-

{
    "name": "Qilin Twilio SMS",
    "summary": "Send SMS using Twilio SMS Gateway, overwriting the default Odoo IAP SMS.",
    "description": """
    This plugin is used to overwrite the Odoo default SMS IAP with the Twilio SMS.
    
    To Configure:
        * Go to the Settings > General Settings. 
        * Search for Twilio Settings.
        * Add the Twilio Details like: Account SID, Auth Token, Number From.
        * Overwrite Odoo SMS if check then system will use Twilio SMS Settings, if not then Odoo SMS IAP. 
    """,
    "version": "1.0",
    "depends": [
        'sms', 'mass_mailing_sms', 'sms_notification'
    ],
    "category": "Tools",
    "website": "https://www.qilinlab.com",
    "author": "Qilin Software Lab",
    "url": "https://www.qilinlab.com",
    "data": [
        'views/configuration.xml',
        'views/sms_sms.xml',
    ],
    'external_dependencies': {"python": ['twilio']},
    "application": False,
    "installable": True,
    "active": True,
}
