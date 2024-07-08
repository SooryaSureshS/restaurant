# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class PosSizeCategory(models.Model):
    _name = "pos.size.category"
    _description = "POS Size Category"
    _order = "sequence, name"

    
    name = fields.Char(string='Category Name', required=True, translate=True)
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of product categories.")

    
