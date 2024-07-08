{
    'name': 'Product Bulk Order Metrix.',
    'category': 'Website/eCommerce',
    'summary': 'Multiple Product Variants add at a time multiple Qty.',
    'description': 'Multiple Product Variants add at a time multiple Qty.',
    'version': '16.0.1.0.0',
    'author': 'Tecspek',
    'data': [
        'views/product_attribute_views.xml',
        # 'views/cart_line_bulk_order.xml',
        'views/checkout.xml',
        'views/product_template_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'depends': [
        'website_sale',
        'stock',
    ],
    'demo': [
    ],
    'images': [
        'static/description/main.png',
        'static/description/full_screenshot.png',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_product_bulk_orders/static/src/js/new_order_popup.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 75,
    'currency': 'EUR',
    'live_test_url': '',
}
