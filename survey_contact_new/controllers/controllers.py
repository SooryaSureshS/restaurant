# -*- coding: utf-8 -*-
# from odoo import http


# class SurveyContact(http.Controller):
#     @http.route('/survey_contact/survey_contact/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/survey_contact/survey_contact/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('survey_contact.listing', {
#             'root': '/survey_contact/survey_contact',
#             'objects': http.request.env['survey_contact.survey_contact'].search([]),
#         })

#     @http.route('/survey_contact/survey_contact/objects/<model("survey_contact.survey_contact"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('survey_contact.object', {
#             'object': obj
#         })
