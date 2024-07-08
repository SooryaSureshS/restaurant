# -*- coding: utf-8 -*-
#############################################################################
#
#    Socius Innovative Global Brains
#
#############################################################################
{
    'name': 'School Management Dashboard',
    'summary': """School Management Dashboard""",
    'version': '1.0.1',
    'depends': ['base', 'school'],
    'license': 'AGPL-3',
    'data': [
        # 'security/ir.model.access.csv',
        'views/menu_action.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # admin_lte
            'school_management_dashboard/static/src/css/admin_lte/adminlte.css',
            # 'school_management_dashboard/static/src/css/admin_lte/alt/*.css',
            'school_management_dashboard/static/src/css/plugins/jquery-ui.min.css',
            ############
            'school_management_dashboard/static/src/css/high.css',
            ############
            'school_management_dashboard/static/src/js/prop_mgt_action.js',
        ],
        'web.assets_frontend': [
        ],
        'web.assets_qweb': [
            'school_management_dashboard/static/src/xml/userDashboard.xml',
            'school_management_dashboard/static/src/xml/sellerDashboard.xml',
            'school_management_dashboard/static/src/xml/featuredSaleOffers.xml',
            'school_management_dashboard/static/src/xml/navBar.xml',
            'school_management_dashboard/static/src/xml/propertiesOverview.xml',
            'school_management_dashboard/static/src/xml/renewContracts.xml',
            'school_management_dashboard/static/src/xml/saleAnalytics.xml',
            'school_management_dashboard/static/src/xml/scheduledMaintenance.xml',
            'school_management_dashboard/static/src/xml/scheduledPayments.xml',
            'school_management_dashboard/static/src/xml/prop_mgt_dashboard.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
