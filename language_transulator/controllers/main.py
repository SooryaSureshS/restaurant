# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import http
import requests
from odoo.http import request
_logger = logging.getLogger(__name__)

class LanguageTranslators(http.Controller):


    @http.route(['/language/transition'], type='json', auth='none')
    def get_lang_tansition(self):
        print("lang", request.env.lang)
        print("lang", request.httprequest.cookies.get('frontend_lang'))
        trans = request.env['lang.translation'].sudo().search([])
        trans_dict = dict()
        for tran in trans:
            if tran.terms in trans_dict:
                trans_dict[tran.terms][tran.to_language.code] = tran.to_terms
            else:

                trans_dict[tran.terms] = dict()
                trans_dict[tran.terms][tran.to_language.code] = tran.to_terms
        print("trans_dict>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(trans_dict)
        c = {
            'code': request.httprequest.cookies.get('frontend_lang'),
            'language': trans_dict
        }
        return c

