from odoo.http import request
import pytz
from odoo import http, api, fields, models, _

from datetime import timedelta
from datetime import datetime


class PosSessionReport(http.Controller):

    @http.route('/pos/session_report', type='http', auth='user')
    def print_session_report(self, **kw):

        print("ddd", kw)
        closed_session = kw['closed_session']
        print("fghjkl", closed_session)
        r = request.env['report.pos_session_summary.report_pos_session_summary_pos']
        pdf, _ = s.env.ref('pos_session_summary.action_pos_session_summary').with_context(id=int(closed_session))._render_qweb_pdf(r)
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)


