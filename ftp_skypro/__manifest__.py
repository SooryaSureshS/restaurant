{
    'name': 'Skypro FTP',
    'summary': """Skypro FILE TRANSFER""",
    'version': '1.0',
    'description': """Skypro FILE TRANSFER""",
    'depends': ['base', 'sale', 'delivery', 'stock'],
    'license': 'AGPL-3',
    'data': [
        "security/ir.model.access.csv",
        'views/res_config_view_form.xml',
        'views/account_payment_terms.xml',
        'views/delivery_carrier.xml',
        'views/shipping_terms.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}