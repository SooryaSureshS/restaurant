# -*- coding: utf-8 -*-
# from odoo import http


# class PosSizeCategory(http.Controller):
#     @http.route('/pos_size_category/pos_size_category/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_size_category/pos_size_category/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_size_category.listing', {
#             'root': '/pos_size_category/pos_size_category',
#             'objects': http.request.env['pos_size_category.pos_size_category'].search([]),
#         })

#     @http.route('/pos_size_category/pos_size_category/objects/<model("pos_size_category.pos_size_category"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_size_category.object', {
#             'object': obj
#         })
