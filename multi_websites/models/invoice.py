# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)
class AccountInvoice(models.Model):
    _inherit = "account.move"
    
    website_id = fields.Many2one('website',
    	string='Website',
    	help='Website through which this invoice was created.',
   	    readonly=True
   	)

    @api.model
    def create(self,vals):
        res = super(AccountInvoice, self).create(vals)
        if vals.get('invoice_origin'):
            order_id = self.env['sale.order'].search([('name','=',vals.get('invoice_origin'))], limit=1)
            if order_id and order_id.website_id:
                res.website_id = order_id.website_id.id
        return res
