# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)
class StockPicking(models.Model):
	_inherit = "stock.picking"

	website_id = fields.Many2one(
		comodel_name="website",
		string="Website",
		help="Website from which the order actually came"
	)

	@api.model
	def create(self, vals):
		res = super(StockPicking, self).create(vals)
		if res.origin:
			order_id = self.env['sale.order'].search([('name','=',vals.get('origin'))], limit=1)
			if order_id.website_id:
				res.website_id = order_id.website_id.id
		return res

class StockMove(models.Model):
	_inherit = "stock.move"

	def _get_new_picking_values(self):
		res = super(StockMove, self)._get_new_picking_values()
		for rec in self:
			order_id = rec.env['sale.order'].sudo().search([('name','=',rec.origin)], limit=1)
			if order_id and order_id.website_id:
				res['website_id'] = order_id.website_id.id
			return res
