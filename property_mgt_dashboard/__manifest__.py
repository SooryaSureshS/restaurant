# -*- coding: utf-8 -*-
#############################################################################
#
#    Socius Innovative Global Brains
#
#############################################################################
{
    'name': 'Property Management Dashboard',
    'summary': """Property Management Dashboard""",
    'version': '1.0.1',
    'depends': ['base', 'property_rental_mgt_app'],
    'license': 'AGPL-3',
    'data': [
        # 'security/ir.model.access.csv',
        'views/menu_action.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # admin_lte
            'property_mgt_dashboard/static/src/css/admin_lte/adminlte.css',
            # 'property_mgt_dashboard/static/src/css/admin_lte/alt/*.css',
            'property_mgt_dashboard/static/src/css/plugins/jquery-ui.min.css',
            ############
            'property_mgt_dashboard/static/src/css/high.css',
            ############
            'property_mgt_dashboard/static/src/js/prop_mgt_action.js',
        ],
        'web.assets_frontend': [
        ],
        'web.assets_qweb': [
            'property_mgt_dashboard/static/src/xml/userDashboard.xml',
            'property_mgt_dashboard/static/src/xml/sellerDashboard.xml',
            'property_mgt_dashboard/static/src/xml/featuredSaleOffers.xml',
            'property_mgt_dashboard/static/src/xml/navBar.xml',
            'property_mgt_dashboard/static/src/xml/propertiesOverview.xml',
            'property_mgt_dashboard/static/src/xml/renewContracts.xml',
            'property_mgt_dashboard/static/src/xml/saleAnalytics.xml',
            'property_mgt_dashboard/static/src/xml/scheduledMaintenance.xml',
            'property_mgt_dashboard/static/src/xml/scheduledPayments.xml',
            'property_mgt_dashboard/static/src/xml/prop_mgt_dashboard.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
