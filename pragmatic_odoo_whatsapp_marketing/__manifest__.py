{
    'name': 'Odoo Whatsapp Marketing',
    'version': '14.0.5',
    'category': 'Connector',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'pragtech.co.in',
    'summary': 'whatsapp connector whatsapp integration odoo Whatsapp crm Whatsapp lead Whatsapp task Whatsapp sale order Whatsapp purchase order Whatsapp invoice Whatsapp mass messages Whatsapp bulk messages',
    'description': """
    Pragmatic Odoo Whatsapp Marketing
    """,
    'depends': ['pragmatic_odoo_whatsapp_integration', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/whatsapp_msg_marketing.xml',
        'views/odoo_group_view.xml',
        'views/whatsapp_contact_view.xml',
        'views/whatsapp_group_view.xml',
        'views/whatsapp_marketing_view.xml',
        'views/whatsapp_marketing_scheduler.xml',
        'wizard/whatsapp_message_schedule_date_views.xml',
        'views/whatsapp_message_view.xml'
    ],
    'qweb': [
    ],
    'images': ['static/description/whatsapp_message_marketing_campaignsbanner.jpg'],
    #'images': ['static/description/end-of-year-sale-main.jpg'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=103&name=odoo-whatsapp-marketing',
    'price': 99,
    'currency': 'USD',
    'license': 'OPL-1',
    'application': False,
    'auto_install': False,
    'installable': True,
}
