# -*- coding: utf-8 -*-
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

class WebsiteBooking(http.Controller):

    @http.route(['/sale/line/note'], type='json', auth="public", methods=['POST'], website=True)
    def sale_note_line(self, **kw):
        order = request.env['sale.order.line'].sudo().search([('id','=',kw.get('order_id'))],limit=1)
        data = {
            'id': order.id,
            'product_id': order.product_id.id,
            'checkout': order.checkout_note or '',
        }

        return data

    @http.route(['/sale/line/note/create'], type='json', auth="public", methods=['POST'], website=True)
    def sale_note_line_create(self, **kw):
        order = request.env['sale.order.line'].sudo().search([('id', '=', kw.get('order_id'))], limit=1)
        order.sudo().write({
            'checkout_note':kw.get('text')
        })

        return True