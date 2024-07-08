# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ast import literal_eval
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProductTemplateInherit(models.Model):
	_inherit = 'product.template'

	gift_card_type = fields.Selection([('ecard','Email Card'),('pcard','Physical Card')],required=True,default='ecard',)
	gift_ok = fields.Boolean("Is a GiftCard",default=False)
	template_id = fields.Many2one('mail.template','Mail template')
	card_validity = fields.Integer('Card Validity',default=0)
	validity_type = fields.Selection([('year','Year'),('month','Month')],default='year',required=True,)


class InvoiceInherit(models.Model):
	_inherit = 'account.move'

	# @api.multi
	def _post(self, soft=True):
		# lots of duplicate calls to action_invoice_open, so we remove those already open
		print("****************self********************",self)
		for invoice in self:
			print("****************invoice********************", invoice)
			if any(line.product_id.gift_ok == True for line in invoice.invoice_line_ids):
				for line in invoice.invoice_line_ids:
					print("****************line********************", line.product_id.gift_ok)
					if line.product_id.gift_ok == True:
						# if line.product_id.gift_card_type == 'ecard':
						expiry_checked = False
						exp_dat_show = False
						coupon_obj = self.env['web.gift.coupon']
						d = datetime.now()
						print(invoice.invoice_date,'invoice _date')
						issue_date = datetime.combine(d, datetime.min.time())
						if line.product_id.validity_type == 'month':
							value = line.product_id.card_validity
							expiry_checked = issue_date + relativedelta(months=int(value))
						elif line.product_id.validity_type == 'year':
							value = line.product_id.card_validity
							expiry_checked = issue_date + relativedelta(years=int(value))
						else:
							expiry_checked = False

						if expiry_checked :
							exp_dat_show = True

						coupon_prod = self.env['product.product'].search([('type', '=', 'service'),('is_coupon_product', '=', True)],limit=1).id
						if not coupon_prod :
							gp = self.env['product.product'].create({
								'is_coupon_product' : True,
								'name': 'Gift Product',
								'type': 'service',
								'categ_id': line.product_id.categ_id.id })
							coupon_prod = gp.id

						vals = {
							'name':line.product_id.name + ' ' + str(line.id),
							'coupon_apply_times':1,
							'product_id' : coupon_prod,
							'issue_date': issue_date,
							'amount':line.product_id.list_price,
							'amount_type':'fix',
							'exp_dat_show': exp_dat_show,
							'expiry_date':expiry_checked,
							'partner_id':invoice.partner_id.id,
							'partner_true':True,
							'max_amount':line.product_id.list_price,
							'active': True,
							'user_id': self.env.user.id,
						}

						template = None
						if line.product_id.template_id:
								template = line.product_id.template_id.id

						print("---------------------------line.product_id.gift_card_type--------",line.product_id.gift_card_type)
						if line.product_id.gift_card_type == 'ecard':
							coupon_id = coupon_obj.sudo().with_context(giftcard=True,template=template).create(vals)
						else:
							coupon_id = coupon_obj.sudo().create(vals)


		return super(InvoiceInherit, self)._post()


class GiftCoupanInherit(models.Model):
	_inherit = 'web.gift.coupon'

	@api.model
	def create(self, vals):
		res = super(GiftCoupanInherit, self).create(vals)
		if 'giftcard' in self._context:
			if self._context.get('giftcard') == True:
				auther = res.user_id.partner_id
				if self._context.get('template'):
					
					template_id = self.env['mail.template'].browse(int(self._context.get('template')))
					template_id.sudo().with_context(auther=auther).send_mail(res.id, force_send=True)
				else:
					
					template_id = self.env.ref('bi_website_gift_cards.email_template_edi_giftcard')
					template_id.sudo().with_context(auther=auther).send_mail(res.id, force_send=True)

		return res





class MailTemplate(models.Model):
	_inherit = 'mail.template'

	def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None):
		res = super(MailTemplate, self).send_mail(res_id, force_send=False, raise_exception=False, email_values=None)
		
		if self._context.get('auther'):
			self.env['mail.mail'].sudo().browse(res).author_id = self._context.get('auther').id # [(6,0,[self._context.get('attachment').id])]
		return res



class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	ecard_message = fields.Char("E-Gift Card Message",related="company_id.ecard_message",readonly=False)
	pcard_message = fields.Char("Physical Gift Card Message",related="company_id.pcard_message",readonly=False)


class Res_company_inherit(models.Model):
	_inherit = 'res.company'

	ecard_message = fields.Char("E-Gift Card Message")
	pcard_message = fields.Char("Physical Gift Card Message")

class WebsiteInherit(models.Model):
	_inherit = 'website'

	ecard_message = fields.Char("E-Gift Card Message",related="company_id.ecard_message")
	pcard_message = fields.Char("Physical Gift Card Message",related="company_id.pcard_message")
