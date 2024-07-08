{
    'name': 'Cyber Source Payment Acquirer',
    'version': '15.0.0.0.0',
    'depends': ['payment', 'website_sale'],
    'author': 'abhiram',
    'data': [
        'views/product.xml',
        'views/payment_templates.xml',
        'views/acquirer_form.xml',
        'views/res_company.xml',
        'data/payment_acquirer_data.xml',
        'views/shop_payment.xml',
    ],
    'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.assets_frontend': [
            'payment_cybersource/static/src/js/payment_form.js',
            'payment_cybersource/static/src/js/payment_card.js',
            'payment_cybersource/static/src/js/payment_delivery.js',
            'payment_cybersource/static/src/js/coupon_form.js',
        ],
    },
    'license': 'LGPL-3',
}
