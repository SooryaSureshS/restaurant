# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, models, fields
import logging
_logger = logging.getLogger(__name__)


class Website(models.Model):
	_inherit = 'website'

	product_check_default = fields.Boolean(
		string="Allow Default Product Selection",
		help="After enabling this user will be able to add or remove the product from the selection list."
	)

	fbtp_header = fields.Char(
		string="Header Message",
		required=True,
	)

	description = fields.Text(
		string="Description On Website"
	)

	cart_button_text = fields.Char(
		string="Add To Cart Button Text",
		required=True,
	)
