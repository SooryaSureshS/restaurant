{
    'name': 'Whatsapp Odoo POS Integration',
    'version': '14.0.8',
    'category': 'Connector',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://www.pragtech.co.in',
    'summary': 'Whatsapp pos Whatsapp point of sale whats app communication',
    'description': """
Whatsapp Odoo POS Integration
=============================
Whatsapp is an immensely popular chatting app used by 1.5 Billion people worldwide.
It has an easy interface and can be used powerfully with Odoo.
Pragmatic has developed an Odoo pos app which allows users to use the Whatsapp Application to send messages via Odoo.

Features of Whatsapp Odoo POS Integration App
----------------------------------------------
    * Whatsapp configuration for each POS.
    * Pre-defined whatsapp message templates.
    * Send whatsapp message from pos session.
    * Send order receipt through whatsapp.
    * Send whatsapp messages to single or group users.
    """,
    'depends': ['point_of_sale', 'pragmatic_odoo_whatsapp_integration'],
    'data': [
        'security/ir.model.access.csv',
        'views/whatsapp_message_template_views.xml',
        'views/pos_config_views.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/Popups/WhatsAppSendMsgPopup.xml',
        'static/src/xml/Popups/WhatsAppGroupSelectPopup.xml',
        'static/src/xml/Screens/ClientListScreen/ClientLine.xml',
        'static/src/xml/Screens/ProductScreen/ControlButtons/GroupWhatsappMessageButton.xml',
        'static/src/xml/Screens/RecieptScreen/ReceiptScreen.xml',
    ],
    'images': ['static/description/pos_whatsapp_gifanimation.gif'],
    #'images': ['static/description/end-of-year-sale-main.jpg'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=103&name=pos-whatsapp-integration',
    'price': 49,
    'currency': 'USD',
    'license': 'OPL-1',
    'application': False,
    'auto_install': False,
    'installable': True,
}
