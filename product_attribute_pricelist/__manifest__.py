{
    'name': 'Product Attribute based Pricelist',
    'summary': """""",
    'version': '15.0.1.0.0',
    'description': """""",
    'depends': ['base', 'product'],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/product_pricelist.xml',
        'wizards/product_attribute_pricelist_wizard.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
