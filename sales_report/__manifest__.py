{
    "name": "Sales Report",
    "author": "SIGB",
    "category": "Reporting",
    "version": "14.0.1.0.0",
    "depends": ["base", "web"],
    "data": [
        "views/reporting_menu.xml",
        "views/hourly_sales_reporting_menu.xml",
        "wizard/wizard.xml",
        "security/ir.model.access.csv",
        "report/report.xml",
        "report/report_pdf_template.xml",
    ],
    "installable": True,
    "application": True,
}
