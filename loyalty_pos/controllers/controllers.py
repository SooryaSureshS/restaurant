# -*- coding: utf-8 -*-
# from odoo import http


# class LoyalityPos(http.Controller):
#     @http.route('/loyalty_pos/loyalty_pos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/loyalty_pos/loyalty_pos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('loyalty_pos.listing', {
#             'root': '/loyalty_pos/loyalty_pos',
#             'objects': http.request.env['loyalty_pos.loyalty_pos'].search([]),
#         })

#     @http.route('/loyalty_pos/loyalty_pos/objects/<model("loyalty_pos.loyalty_pos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('loyalty_pos.object', {
#             'object': obj
#         })
