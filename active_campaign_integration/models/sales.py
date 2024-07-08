import base64
import datetime
import json
import re
import requests

from odoo import api, fields, models, _
from odoo.exceptions import Warning
from werkzeug import urls
from odoo.exceptions import ValidationError


class ActiveCampaignSalesInherit(models.Model):
    _inherit = 'sale.order'


    def write(self, vals):
        res = super(ActiveCampaignSalesInherit, self).write(vals)
        product_list = []
        if self.reference != False:
            for product in self.order_line:
                if product.product_id.type != 'service':
                    product_list.append(product.product_id.name)
                

            data = {
                "orderId": self.name,
                "productName": product_list,
                "totalAmount": self.amount_total

            }
            self.env['sale.order'].upd_cont(data)
        return res




    def upd_cont(self,data):
        data = {
                "orderId": data['orderId'],
                "productName": data['productName'],
                "totalAmount": data['totalAmount']
            }
        self.env['active.campaign'].update_order_data(self,data)


