# -*- coding: utf-8 -*-
from odoo import models

class BasePartnerMergeAutomaticWizard(models.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'

    def _get_summable_fields(self):
        res = super(BasePartnerMergeAutomaticWizard, self)._get_summable_fields()
        res.extend(['loyalty_points'])
        return res
