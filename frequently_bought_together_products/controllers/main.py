# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID

from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)


class website_sale(WebsiteSale):
	
	@http.route(['/frequently/bought/add_to_cart'], type='json', auth="public",  website=True)
	def frequently_bought_add_to_cart(self, product_ids, **kw):
		order = request.website.sale_get_order(force_create=1)
		for product_id in product_ids:
			order._cart_update(
				product_id=int(product_id),
				add_qty=float(1),
				set_qty=float(1),
			)
		return True
		
	