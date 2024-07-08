# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Frequently Bought Together Products",
  "summary"              :  "The module provides the opportunity to up-sell by showing frequently together on the product pages of the Odoo website.",
  "category"             :  "Website",
  "version"              :  "1.0.2",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Frequently-Bought-Together-Products.html",
  "description"          :  """Odoo Frequently Bought Together Products
Odoo upsell products
Odoo cross sell products
Cross-sell products
Odoo related prorducts
Sell frequently bought products
""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=frequently_bought_together_products",
  "depends"              :  [
                             'website_sale',
                             'website_webkul_addons',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/product_view.xml',
                             'views/res_conf_view.xml',
                             'views/webkul_addons_config_inherit_view.xml',
                             'views/template.xml',
                            ],
  "demo"                 :  ['data/demo.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  59,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}
