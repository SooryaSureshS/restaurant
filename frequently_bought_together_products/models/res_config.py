# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, models, fields
import logging
_logger = logging.getLogger(__name__)


class FrequentlyBoughtProductsConf(models.TransientModel):
	_name = 'frequently.bought.products.conf'
	_inherit = 'webkul.website.addons'

	product_check_default = fields.Boolean(
		string="Allow Default Product Selection",
		help="After enabling this user will be able to add or remove the product from the selection list.",
		related='website_id.product_check_default',
		readonly=False
	)

	fbtp_header = fields.Char(
		string="Header Message",
		required=True,
		related='website_id.fbtp_header',
		readonly=False
	)

	description = fields.Text(
		string="Description On Website",
		related='website_id.description',
		readonly=False
	)

	cart_button_text = fields.Char(
		string="Add To Cart Button Text",
		required=True,
		related='website_id.cart_button_text',
		readonly=False
	)
	# @api.multi
	# def set_values(self):
	# 	super(FrequentlyBoughtProductsConf, self).set_values()
	# 	IrDefault = self.env['ir.default'].sudo()
	# 	IrDefault.set('frequently.bought.products.conf','product_check_default', self.product_check_default)
	# 	IrDefault.set('frequently.bought.products.conf','header', self.header) or 'FREQUENTLY BOUGHT TOGETHER PRODUCTS'
	# 	IrDefault.set('frequently.bought.products.conf','description', self.description)
	# 	IrDefault.set('frequently.bought.products.conf','cart_button_text', self.cart_button_text) or 'ADD SELECTED TO CART'
	#
	# @api.multi
	# def get_values(self):
	# 	res = super(FrequentlyBoughtProductsConf, self).get_values()
	# 	IrDefault = self.env['ir.default'].sudo()
	# 	res.update({
	# 		'product_check_default':IrDefault.get('frequently.bought.products.conf','product_check_default'),
	# 		'header':IrDefault.get('frequently.bought.products.conf','header') or 'FREQUENTLY BOUGHT TOGETHER PRODUCTS',
	# 		'description':IrDefault.get('frequently.bought.products.conf','description'),
	# 		'cart_button_text':IrDefault.get('frequently.bought.products.conf','cart_button_text') or 'ADD SELECTED TO CART',
	# 	})
	# 	return res
