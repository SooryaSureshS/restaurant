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

{
    'name': "Sales Order Minimum Quantity",
    'author': 'Ascetic Business Solution',
    'category': 'Sales',
    'summary': """Set minimum sales quantity limit on product""",
    'website': 'http://www.asceticbs.com',
    'description': """Sales Order Minimum Quantity""",
    'version': '15.0.1.0',
    'depends': ['base', 'sale_management', 'product', 'purchase', 'mask_cutomization'],
    'data': [
        'views/view_minimum_order_quantity.xml'
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',    
    'installable': True,
    'application': True,
    'auto_install': False,
}
