# # -*- coding: utf-8 -*-
#
import base64
import datetime
import json
import re
import requests

from odoo import api, fields, models, _
from odoo.exceptions import Warning
from werkzeug import urls
from odoo.exceptions import ValidationError


class ActiveCampaignPartnerInherit(models.Model):
    _inherit = 'res.partner'

    active_campaign_contact_id = fields.Char()
    active_campaign_association_id = fields.Char()

#     @api.model
#     def create(self, vals_list):
#         res = super(ActiveCampaignPartnerInherit, self).create(vals_list)
#         # self._check_email()
#         self.env['active.campaign'].create_contact(vals_list)
#
#         return res
#
#     @api.onchange('email', 'name', 'phone', 'child_ids')
#     def upd_cont(self):
#         if self.active_campaign_contact_id:
#             data = {
#                 "email": self.email,
#                 "firstName": self.name,
#                 "lastName": " ",
#                 "phone": self.phone,
#             }
#             self.env['active.campaign'].update_contact(self, data)
#         else:
#             return
#
#     @api.onchange('function')
#     def upd_job_title(self):
#         if self.active_campaign_contact_id:
#             data = {
#                 "email": self.email,
#                 "firstName": self.name,
#                 "lastName": " ",
#                 "phone": self.phone,
#             }
#             self.env['active.campaign'].update_contact_job_title(self,self.function)
#         else:
#             return
#
#     # @api.constrains('email')
#     # def _check_email(self):
#     #     count_email = self.search_count([('email', '=', self.email)])
#     #     if count_email > 1 and self.email is not False:
#     #         raise ValidationError('The email already registered, please use another email!')
#
#     def unlink(self):
#         self.env['active.campaign'].delete_contact(self)
#         return models.Model.unlink(self)