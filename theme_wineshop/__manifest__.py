# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

#for Animations you need to extract the website_animate Module in the addons path

{
    'name': 'Theme WineShop',
    'category': 'Theme/eCommerce',
    'version': '14.0.0.4',
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'http://www.bizople.com',
    'summary': '''Theme WineShop''',
    'description': """Theme WineShop""",

    'depends': [
        'theme_default',
	    'website',
        'mass_mailing',
        'website_crm',
        'website_blog',
        'portal',
        'web_editor',
        'website_sale',
        'website_sale_wishlist',
        'website_sale_comparison',
        'sale_management',

    ],

   'data': [
    'security/ir.model.access.csv',
	'views/assets.xml',
    'views/inherits/product_view_inherit.xml',
    'views/homepage.xml',
    'views/whisky_homepage.xml',
    'views/vodka_homepage.xml',
    'views/our_wines.xml',
    'views/estate.xml',
    'views/restaurant.xml',
    'views/header.xml',
    'views/footer.xml',
    'views/inherits/shop_page_inherit.xml',
    'views/inherits/product_page_inherit.xml',
    'views/inherits/blog_page_inherit.xml',
    'views/inherits/customize_inherit.xml',
    'views/inherits/snippet_inherit.xml',
    'views/dynamicslider.xml',
    'views/product_label_view.xml',
    'views/snippets.xml',
    'views/index.xml',
    'data/menu_data.xml',
    'views/product.xml',

    # snippets
    'views/snippets/s_homepage_wine.xml',
    'views/snippets/s_homepage_whisky.xml',
    'views/snippets/s_homepage_vodka.xml',
    'views/snippets/s_restaurant_page.xml',
    'views/snippets/s_estate_page.xml',
    'views/snippets/s_our_wines_page.xml',

    'views/snippets/s_wine_banner.xml',
    'views/snippets/s_wine_counter_left.xml',
    'views/snippets/s_wine_counter_right.xml',
    'views/snippets/s_wine_current_release.xml',
    'views/snippets/s_wine_instagram.xml',
    'views/snippets/s_wine_maker.xml',
    'views/snippets/s_wine_single_product.xml',
    'views/snippets/s_wine_tasting.xml',
    'views/snippets/s_wine_visit.xml',

    'views/snippets/s_whisky_banner.xml',
    'views/snippets/s_whisky_brands.xml',
    'views/snippets/s_whisky_sale.xml',
    'views/snippets/s_whisky_service.xml',
    'views/snippets/s_whisky_testimonial.xml',

    'views/snippets/s_vodka_banner.xml',
    'views/snippets/s_vodka_maker.xml',
    'views/snippets/s_vodka_parallex.xml',
    'views/snippets/s_vodka_sale.xml',
    'views/snippets/s_vodka_service.xml',

    'views/snippets/s_restaurant_banner.xml',
    'views/snippets/s_restaurant_about.xml',
    'views/snippets/s_restaurant_contact.xml',
    'views/snippets/s_restaurant_gallary.xml',
    'views/snippets/s_restaurant_menu.xml',
    'views/snippets/s_restaurant_reservation.xml',
    'views/snippets/s_restaurant_time.xml',
    'views/snippets/s_restaurant_title.xml',

    'views/snippets/s_estate_banner.xml',
    'views/snippets/s_estate_about.xml',
    'views/snippets/s_estate_gallary.xml',
    'views/snippets/s_estate_info.xml',
    'views/snippets/s_estate_location.xml',
    'views/snippets/s_estate_tasting.xml',
    'views/snippets/s_estate_title.xml',

    'views/snippets/s_our_wines_banner.xml',
    'views/snippets/s_our_wines_award.xml',
    'views/snippets/s_our_wines_cellar.xml',
    'views/snippets/s_our_wines_counter_left.xml',
    'views/snippets/s_our_wines_counter_right.xml',
    'views/snippets/s_our_wines_title.xml',


    
   ],
    'images': [
        'static/description/wineshop_poster.jpg',
        'static/description/wineshop_screenshot.png',
    ],
    
    'live_test_url': 'https://bit.ly/theme-wineshop-bizople',
    
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
    'price': 99,
    'currency': 'EUR',
}
