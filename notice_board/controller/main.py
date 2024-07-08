# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

from datetime import datetime
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo import http

class Notices(http.Controller):

    def search_notices(self):
        return request.env["notice.board"].sudo().search([
                ("start_date", "<=", datetime.today().strftime(DF)), ('end_date', '>=', datetime.today().strftime(DF)),('active','=', True),('is_published','=',True)], order='create_date desc')

    @http.route(['/get/notices'], type='json', auth='user', csrf=False)
    def get_notices(self, notice_count, **post):
        vals = []
        for record in self.search_notices():
            vals.append({'id':record.id, 'name': record.name, 'image':record.image , 'event_date':record.event_date, 'participation_link': record.participation_link , 'venue':record.venue, 'message':record.message})
        template = request.env.ref('notice_board.notice_records')._render({'records': vals, 'notice_count': notice_count})
        result = {
            'records' : vals,
            'template': template,
            'notice_count': notice_count
        }
        return result

    @http.route(['/get/notice/records'], type='json', auth='user', csrf=False)
    def get_notice_record(self, **post):
        result = []
        for record in self.search_notices():
            event_date = record.event_date.strftime("%d/%m/%Y") if record.event_date else False
            result.append({'name': record.name,'event_date':event_date,'create_date':record.create_date})
        result = sorted(result, key=lambda x: x.get('create_date'))[::-1]
        return result
