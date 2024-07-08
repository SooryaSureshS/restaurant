# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    v = fields.Boolean(string='V')
    gf = fields.Boolean(string='GF')
    veg = fields.Boolean(string='VEG')
    df = fields.Boolean(string="DF")

    @api.model
    def create(self, vals):
        result = super(ProductTemplate, self).create(vals)
        if result.v or result.gf or result.veg:
            name = []
            if result.v:
                name.append('(V)')
            if result.gf:
                name.append('(GF)')
            if result.veg:
                name.append('(VEG)')
            result.name += " "+" ".join(name)
        return result

    def write(self, vals):
        if 'v' in vals and vals['v'] or 'gf' in vals and vals['gf'] or 'veg' in vals and vals['veg']:
            name = []
            if 'v' in vals and vals['v']:
                name.append('(V)')
            if 'gf' in vals and vals['gf']:
                name.append('(GF)')
            if 'veg' in vals and vals['veg']:
                name.append('(VEG)')
            self.name += " "+" ".join(name)

        result = super(ProductTemplate, self).write(vals)
        return result

    @api.onchange('v')
    def _onchange_v(self):
        for vals in self:
            if vals.v == False:
                product_name = str(vals.name).replace('(V)','')
                vals.name = product_name
        return

    @api.onchange('gf')
    def _onchange_gf(self):
        for vals in self:
            if vals.gf == False:
                product_name = str(vals.name).replace('(GF)','')
                vals.name = product_name
        return

    @api.onchange('veg')
    def _onchange_veg(self):
        for vals in self:
            if vals.veg == False:
                product_name = str(vals.name).replace('(VEG)','')
                vals.name = product_name
        return


