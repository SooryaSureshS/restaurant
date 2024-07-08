# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def write(self, vals):
        if self and self.company_id:
            company_record = self.env['res.company'].sudo().browse(self.company_id.id)
            if company_record:
                company_record.sudo().write({'logo': vals.get('pos_logo')})
        return super(PosConfig, self).write(vals)

    @api.model
    def create(self, vals):
        if vals and vals.get('company_id'):
            company_record = self.env['res.company'].sudo().browse(
                vals.get('company_id'))
            if company_record and vals.get('pos_logo'):
                company_record.sudo().write({'logo': vals.get('pos_logo')})
        res = super(PosConfig, self).create(vals)
        return res

    pos_logo = fields.Binary(string="Company Logo")
    pos_receipt_logo = fields.Binary(string="POS Receipt Logo")

