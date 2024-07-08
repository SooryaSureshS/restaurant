# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound


from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.osv import expression

class website_add_note(http.Controller):

    @http.route(['/checkout/order/note'], type='json', auth="public", methods=['POST'], website=True)
    def cart_checkout_note(self, **kw):
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order:
            return sale_order.checkout_note
        else:
            return False

    @http.route(['/checkout/order/note/update'], type='json', auth="public", methods=['POST'], website=True)
    def cart_checkout_note_update(self, value, **kw):
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order:
            print("sale order", sale_order)
            sale_order.write({
                'checkout_note': value,
            })
            return sale_order.checkout_note
        else:
            return False