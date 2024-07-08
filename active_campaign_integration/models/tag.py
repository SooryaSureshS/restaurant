# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ActiveCampaignContactTags(models.Model):
    _inherit= 'res.partner.category'

    active_campaign_tag_id = fields.Char(string="Tag Name")

    @api.model
    def create(self, vals_list):
        res = super(ActiveCampaignContactTags, self).create(vals_list)
        self.env['active.campaign'].create_new_tags(vals_list)
        return res
