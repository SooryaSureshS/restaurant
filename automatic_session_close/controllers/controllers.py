# -*- coding: utf-8 -*-
# from odoo import http


# class AutomaticSessionClose(http.Controller):
#     @http.route('/automatic_session_close/automatic_session_close/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/automatic_session_close/automatic_session_close/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('automatic_session_close.listing', {
#             'root': '/automatic_session_close/automatic_session_close',
#             'objects': http.request.env['automatic_session_close.automatic_session_close'].search([]),
#         })

#     @http.route('/automatic_session_close/automatic_session_close/objects/<model("automatic_session_close.automatic_session_close"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('automatic_session_close.object', {
#             'object': obj
#         })
