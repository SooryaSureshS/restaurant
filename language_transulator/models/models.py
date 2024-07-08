# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from psycopg2 import sql

from odoo import tools
from odoo import api, fields, models, _
import translate
from translate import Translator

class LangTransulation(models.Model):
    _name = "lang.translation"
    _description = "Language Translation"
    # _auto = False
    _order = 'id desc'

    terms = fields.Char('Terms')
    to_language = fields.Many2one('res.lang')
    lang_code = fields.Char(related='to_language.code',  readonly=False)
    to_terms = fields.Char('Terms')

    @api.onchange('terms','to_language')
    def _onchange_categ_id(self):
        if self.terms:
            try:
                if self.to_language.iso_code == 'zh_HK':
                    translator = Translator(to_lang="ZH-tw")
                    translation = translator.translate(self.terms)
                    # translator = Translator(from_lang="chinese", to_lang="english")
                    # translation = translator.translate("Guten Morgen")
                    # translate fr en  'Bonjour, comment allez-vous!'
                    print("on chnage",self.terms)
                    print("on chnage",translation)
                    self.to_terms = translation
                else:
                    translator = Translator(to_lang=self.to_language.iso_code)
                    translation = translator.translate(self.terms)
                    # translator = Translator(from_lang="chinese", to_lang="english")
                    # translation = translator.translate("Guten Morgen")
                    # translate fr en  'Bonjour, comment allez-vous!'
                    print("on chnage", self.terms)
                    print("on chnage", translation)
                    self.to_terms = translation
            except:
                pass