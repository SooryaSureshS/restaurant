# -*- coding: utf-8 -*-

from odoo import fields, models, _


class AccountTax(models.Model):
	_inherit = "account.tax"

	charge_type = fields.Selection([
			('service_charge', _('Service Charge')),
			('gst_vat_charge', _('GST/VAT Charge')),
		], string="Charge Type", copy=False)
