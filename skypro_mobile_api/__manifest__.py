{
    'name': 'Skypro Mobile',
    'summary': """Skypro mobile api integration""",
    'version': '1.0',
    'description': """Skypro mobile api integration""",
    'depends': ['base','product','sale','website_sale','website','payment'],
    'license': 'AGPL-3',
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_users_view.xml',
        'views/product_template_view.xml',
        'views/rescompany_form_inherit.xml',
        'views/sale_order_line_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}