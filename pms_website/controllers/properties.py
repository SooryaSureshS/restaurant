# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class WebsiteInherit(Website):

    @http.route('/', type='http', auth="public", website=True, sitemap=True)
    def index(self, **kw):
        top_menu = request.website.menu_id
        homepage_id = request.website._get_cached('homepage_id')
        homepage = homepage_id and request.env['website.page'].browse(homepage_id)
        if homepage and (homepage.sudo().is_visible or request.env.user.has_group(
                'base.group_user')) and homepage.url != '/':
            return request.env['ir.http'].reroute(homepage.url)
        website_page = request.env['ir.http']._serve_page()
        if website_page:
            properties = request.env['product.product'].sudo().search([
                ('is_property', '=', True)
            ])
            ctx = dict(request.context)
            ctx.update({'properties': properties})
            request.context = ctx
            return website_page
        else:
            first_menu = top_menu and top_menu.child_id and top_menu.child_id.filtered(lambda menu: menu.is_visible)
            if first_menu and first_menu[0].url not in ('/', '', '#') and (
                    not (first_menu[0].url.startswith(('/?', '/#', ' ')))):
                return request.redirect(first_menu[0].url)
        raise request.not_found()
