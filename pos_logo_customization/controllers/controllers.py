# -*- coding: utf-8 -*-
# from odoo import http


# class PosLogoCustomization(http.Controller):
#     @http.route('/pos_logo_customization/pos_logo_customization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_logo_customization/pos_logo_customization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_logo_customization.listing', {
#             'root': '/pos_logo_customization/pos_logo_customization',
#             'objects': http.request.env['pos_logo_customization.pos_logo_customization'].search([]),
#         })

#     @http.route('/pos_logo_customization/pos_logo_customization/objects/<model("pos_logo_customization.pos_logo_customization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_logo_customization.object', {
#             'object': obj
#         })
