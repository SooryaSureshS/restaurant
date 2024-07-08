# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)
class ProductTemplate(models.Model):
	_inherit = 'product.template'

	wk_frequently_bought_products = fields.Many2many('product.template',
		'sorc_id',
		'dest_id',
		'relt_id',
		string="Frequently Bought"
	)

	@api.model
	def get_fbp_total_price(self):
		def_price = self._get_combination_info().get('list_price')
		web_price = self._get_combination_info().get('price')
		for temp_id in self.wk_frequently_bought_products:
			def_price += temp_id._get_combination_info().get('list_price')
			web_price += temp_id._get_combination_info().get('price')
		return {'def_price':def_price,'web_price':web_price}

class ProductProduct(models.Model):
	_inherit = 'product.product'

	@api.model
	def get_variant_attribute_string(self):
		AttString = ''
		for attribute_id in self.product_template_attribute_value_ids:
			AttString += "%s, "%attribute_id.name
		AttString = AttString.rstrip(', ')
		return AttString
