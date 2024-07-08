# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta

class HrOverdue(models.AbstractModel):
    _name = 'report.hr_scheduling.report_overdue'

    @api.model
    def _get_report_values(self, docids, data=None):
        contracts_ids = self.env['hr.contract'].search([('state', '=', 'open')])
        # contracts_ids = self.env['hr.contract'].search([('date_end', '>=', datetime.now() + relativedelta(days=-7)),
        #                                                 ('date_end', '<=', datetime.now()), ('state', '=', 'open')])
        return {
            'doc_ids': contracts_ids.ids,
            'doc_model': 'hr.employee',
            'docs': contracts_ids,
        }
