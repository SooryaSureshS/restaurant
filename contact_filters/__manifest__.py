{
    'name': 'CONTACT FILTER AND MERGE',
    'summary': 'CONTACT SEGMENTS/FILTERS AND MERGE CONTACT',
    'version': '14.0.0.1',
    'category': '',
    'license': 'AGPL-3',
    'author': 'SIGB',
    'depends': ['sale', 'base', 'contacts', 'website_delivery_type', 'website_sale', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/contacts_filters.xml',
        'wizard/purchase_filter.xml',

    ],
    'qweb': ['static/src/xml/tepm.xml'],
    'demo': [],
    'installable': True,

}
