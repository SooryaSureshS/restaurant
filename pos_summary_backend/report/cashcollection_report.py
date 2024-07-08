# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, models, fields,_
from odoo.exceptions import ValidationError

class PosSummaryBack(models.AbstractModel):
    _name = 'report.pos_summary_backend.report_cashcollection'

    @api.model
    def _get_report_values(self, docids, data):
        data = {
            'start_date': data['start_date'],
            'end_date': data['end_date']
        }

        print("\n _______-data_______",data)

        pos_summary_ids = self.env['pos.session.summary'].search([('status', '=', 'approved'), ('closing_date', '>=', data['start_date']), ('closing_date', '<=', data['end_date'])])

        if len(pos_summary_ids) < 1:
            raise ValidationError(_('There is no approved cash collection in the date period, please check with other dates'))

        else:
            return {
                'doc_ids': pos_summary_ids.ids,
                'doc_model': 'pos.session.summary',
                'docs': pos_summary_ids,
                'data': data
            }
