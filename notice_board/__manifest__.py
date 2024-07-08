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
  "name"                 :  "Odoo Notice Board",
  "summary"              :  """Show all the necessary updates to your employees in Odoo""",
  "category"             :  "ODOO",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo.html",
  "description"          :  """This module helps to show Notice board on website.""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=notice_board",
  "depends"              :  [
                             'hr',
                             'website',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/template.xml',
                             'views/notice_view.xml',
                            ],
  "demo"                 :  ['data/demo.xml'],
  "qweb"                 :  ['static/src/xml/notice_widget.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  45,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}