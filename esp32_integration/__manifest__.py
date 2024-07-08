{
    'name': 'Esp32 Rfid Integration',
    'version': '15.0.0.0.0',
    'depends': ['sale','base'],
    'author': 'jithesh',
    'data': [
        # 'views/payment_templates.xml',
        'security/security.xml',
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/website_lang.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # 'payment_cybersource/static/src/js/payment_form.js',
            # 'payment_cybersource/static/src/js/payment_card.js',
        ],
    },
    'license': 'LGPL-3',
}
