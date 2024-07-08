# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging
import psycopg2
import time
from odoo.tools import float_is_zero
from odoo import models, fields, api, tools, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from datetime import datetime
from operator import itemgetter
from timeit import itertools
from itertools import groupby


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_optional_product = fields.Boolean('Optional Product')
    is_sold_out = fields.Boolean('Sold Out')
    not_available_for_pickup = fields.Boolean('Not Available For Pickup')

# class SaleLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     def get_sale_order_line_multiline_description_sale(self, product):
#         description = super(SaleLine, self).get_sale_order_line_multiline_description_sale(product)
#         if self.linked_line_id:
#             description += "\n" + _("Addon: %s     : $ %s", self.linked_line_id.product_id.display_name)
#         if self.option_line_ids:
#             description += "\n" + '\n'.join([_("Addon: %s    : $ %s", option_line.product_id.display_name) for option_line in self.option_line_ids])
#         return description


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_cart_info(self):
        super(SaleOrder, self)._compute_cart_info()
        for order in self:
            order_main = order.order_line.filtered(lambda line: line.product_template_id.is_optional_product != True)
            order.cart_quantity = int(sum(order_main.mapped('product_uom_qty')))
            order.only_services = all(l.product_id.type in ('service', 'digital') for l in order.website_order_line)
