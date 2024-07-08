{
    'name': "Store Sales Dashboard",
    'version': '14.0.1.0.3',
    'summary': """Store Sales Dashboard""",
    'description': """Store Sales Dashboard""",
    'depends': ['base', 'sale', 'website'],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'data': [
        'views/dashboard_views.xml',
    ],
    'qweb': ["static/src/xml/hrms_dashboard.xml"],
    'installable': True,
    'application': True,
}
