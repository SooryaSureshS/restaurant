{
    'name': 'Umami Rider App API',
    'summary': """Umami Rider api integration""",
    'version': '1.0',
    'description': """Umami Rider api integration""",
    'depends': ['base','product','sale','website_sale','website','payment','umami_mobile'],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/sale.xml',
    ],
    'external_dependencies': {'python': ['geopy']},
    'installable': True,
    'auto_install': False,
    'application': True,
}