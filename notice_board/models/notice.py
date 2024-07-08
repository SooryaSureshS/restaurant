# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2016-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# License URL :<https://store.webkul.com/license.html/>
##########################################################################

from odoo import api, fields, models, _

class NoticeBoard(models.Model):
    _name = "notice.board"
    _inherit = ['mail.thread']
    _description = "Notice Board"
    _order = "write_date desc"

    name = fields.Char("Title", required=True, tracking=True)
    event_date = fields.Date(string="Event Date", default=fields.Date.context_today, tracking=True)
    participation_link = fields.Char(string="Participation Link", tracking=True, help="Link url related to notice.")
    start_date = fields.Date(string="Start Date", default=fields.Date.context_today, required=True, tracking=True, help="Start date to be shown on Notice Board.")
    end_date = fields.Date(string="End Date", default=fields.Date.context_today, tracking=True, help="End date to show on Notice Board. After which it will be removed from notice board.")
    venue = fields.Char(string="Venue", tracking=True, help="Location or venue related to notice.(if there is one)")
    message = fields.Text(tracking=True)
    image = fields.Binary(string="Image")
    active = fields.Boolean("Active",default=True)
    is_published = fields.Boolean('Published', default=True)

    def toggle_published(self):
        self.is_published = not self.is_published
