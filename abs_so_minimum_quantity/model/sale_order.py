# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Raise the warning "Minimum order quantity of the product <Name> is <Quantity Value>."
    # if the order quantity is less than the 'Minimum Order Quantity' of the Product.
    # @api.constrains('order_line')
    # def check_constraint_quantity(self):
    #     for record in self:
    #         if record.order_line:
    #             for line in record.order_line:
    #                 product = line.product_id
    #                 minimum_order_qty = product.minimum_order_quantity
    #                 minimum_qty_step = product.minimum_quantity_step
    #                 if line.product_uom_qty < minimum_order_qty or (line.product_uom_qty % minimum_qty_step) != 0:
    #                     raise ValidationError(_('Minimum order quantity of the product ' + line.name+' is ' + str(minimum_order_qty) + 'and minimum quantity step is ' + str(minimum_qty_step)))
