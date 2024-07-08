{
    "name": "Reporting",
    "author": "SIGB",
    "category": "Reporting",
    "version": "14.0.1.0.0",
    "depends": ["base", "web", "sale"],
    "data": [
        "views/reporting_menu.xml",
        "views/hourly_sales_reporting_menu.xml",
    ],
    'qweb': ["static/src/xml/hourly_sales_reporting.xml"],
    "installable": True,
    "application": True,
}
