# Company: giordano.ch AG
# Copyright by: giordano.ch AG
# https://giordano.ch/

{
    "name": "Gio Obstundgemuese Theme",
    "version": "15.0.1.0.0-beta1",
    "summary": "Custom Website Theme",
    "sequence": 10,
    "depends": [
        "base",
        "portal",
        "website",
        "website_sale",
        "mass_mailing",
        "sale",
        "payment",
        "website_sale_delivery",
        "hr",
        "appointment",
        "website_blog",
        "im_livechat",
        "http_routing"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/header.xml",
        "views/footer.xml",
        "views/res_company.xml",
        "views/product_filter.xml",
        "views/product_detail.xml",
        "views/impressum.xml",
        "views/home.xml",
        "views/mailing_contact.xml",
        "views/obst_panorama_config.xml",
        "views/login_register.xml",
        "views/panorama_hotspot.xml",
        # "views/portal.xml",
        "views/my_account.xml",
        "views/contactus.xml",
        "views/about.xml",
        "views/checkout.xml",
        "views/product_template.xml",
        "views/Privacy_template.xml",
        "views/agb_template.xml",
        "views/hr_employee_view.xml",
        "views/search_template.xml",
        "views/appointments.xml",
        "views/stories.xml",
        "views/obst_live_chat.xml",
        "views/blog_post.xml",
        "views/routing_template.xml",
        "views/performance_page.xml",
    ],
    "installable": True,
    "application": True,
    "assets": {
        "web.assets_frontend": [
            "/gio_obstgemuese_theme/static/src/*/*.js",
            "/gio_obstgemuese_theme/static/src/*/*.css",
            "/gio_obstgemuese_theme/static/src/*/*.scss",
            "/gio_obstgemuese_theme/static/src/css/pr_wizard.less",
            "https://kit.fontawesome.com/845364ebbe.js",
            # "https://cdnjs.cloudflare.com/ajax/libs/pannellum/2.5.6/pannellum.css",  # noqa
            # "https://cdnjs.cloudflare.com/ajax/libs/pannellum/2.5.6/pannellum.js",  # noqa
            "https://polyfill.io/v3/polyfill.min.js", # noqa
        ],
        "web.assets_backend": [
            "https://cdnjs.cloudflare.com/ajax/libs/pannellum/2.5.6/pannellum.css",  # noqa
            "https://cdnjs.cloudflare.com/ajax/libs/pannellum/2.5.6/pannellum.js",  # noqa
        ],
    },
    "auto_install": False,
    "pre_init_hook": "pre_init_check",
}
