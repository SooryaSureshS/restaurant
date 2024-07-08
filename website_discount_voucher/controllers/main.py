# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


import werkzeug
import odoo
from odoo import addons
from odoo import models, fields, api
from odoo import SUPERUSER_ID
from odoo import http, tools, _
from odoo.http import request
from odoo.tools.translate import _
import odoo.http as http
from odoo.http import request
from datetime import datetime, timedelta

import werkzeug.urls
import werkzeug.wrappers
from odoo.addons.website_sale.controllers.main import WebsiteSale


class voucher_discount(http.Controller):

	@http.route(['/shop/voucher'], type='json', auth="public", methods=['POST'], website=True)
	def voucher_code(self, promo, **post):
		request.env.uid = 1
		current_sale_order = request.website.sale_get_order()

		for i in  current_sale_order.order_line:
			if i.discount_line == True:
				return "A Voucher is already applied. Please remove it from cart to apply new Voucher."
		dv = False
		by_name = request.env['web.gift.coupon'].search([('name', '=ilike', promo)])
		by_code = request.env['web.gift.coupon'].search([('c_barcode','=', promo)])
		if by_name:
			dv = by_name
		if by_code:
			dv = by_code
		if not dv:
			return "Invalid Voucher !"
		else:   
			dv = request.env['web.gift.coupon'].browse(dv).id
			dt_end = False
			discount_value = False
			order_line_obj = request.env['sale.order.line'].sudo().search([])

			if dv.coupon_count >= dv.coupon_apply_times :
				return "Can not use coupon because you reached the maximum limit of usage."

			if dv.amount_type == 'fix':
				discount_value = dv.amount
			elif dv.amount_type == 'per':
				total = 0
				for i in current_sale_order.order_line:
					if i.discount_line == False:
						total += i.price_subtotal
				# discount_value = current_sale_order.amount_total * (1 - (dv.amount or 0.0) / 100.0)
				discount_value = ((total * dv.amount)/100)

			if dv.exp_dat_show:
				dt_end = datetime.strptime(str(dv.expiry_date), '%Y-%m-%d %H:%M:%S').date()

			if not dv.max_amount >= discount_value:
				return "Discount amount is higher than maximum amount of this coupon."

			if not current_sale_order.amount_total >= discount_value:
				return "Can not apply discount more than order total."               

			if dv.partner_true == True:
				partner = dv.partner_id.id
				curr_user_partner = request.env['res.users'].browse(request._uid).partner_id
				selected_partner = request.env['res.partner'].browse(partner)
				
				flag = False
				if curr_user_partner.id == selected_partner.id:
					if dv.exp_dat_show:
						if dt_end < datetime.now().date():
							return "This code has been Expired !"
					# request.website.sale_get_order(code2=promo)
					res = order_line_obj.sudo().create({
							'product_id': dv.product_id.id,
							'name': dv.product_id.name,
							'price_unit': -discount_value,
							'order_id': current_sale_order.id,
							'product_uom':dv.product_id.uom_id.id,
							'discount_line':True,
					})
					current_sale_order.sale_coupon_id = dv
					current_sale_order.assign_voucher_code(promo)    
					return True   
				else:
					return "Invalid Customer !"                  
												
			if dv.exp_dat_show:
				if dt_end < datetime.now().date():
					return "This code has been Expired !"

			# request.website.sale_get_order(code2=promo)
			res = order_line_obj.sudo().create({
							'product_id': dv.product_id.id,
							'name': dv.product_id.name,
							'price_unit': -discount_value,
							'order_id': current_sale_order.id,
							'product_uom':dv.product_id.uom_id.id,
							'discount_line':True,
					})
			current_sale_order.sale_coupon_id = dv
			current_sale_order.assign_voucher_code(promo) 
			return True



class WebsiteSaleInherit(WebsiteSale):


	@http.route('/shop/payment/validate', type='http', auth="public", website=True)
	def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
		""" Method that should be called by the server when receiving an update
		for a transaction. State at this point :



		"""
		if sale_order_id is None:
			order = request.website.sale_get_order()
		else:
			order = request.env['sale.order'].sudo().browse(sale_order_id)
			assert order.id == request.session.get('sale_last_order_id')

		if transaction_id:
			tx = request.env['payment.transaction'].sudo().browse(transaction_id)
			assert tx in order.transaction_ids()
		elif order:
			tx = order.get_portal_last_transaction()
		else:
			tx = None

		if not order or (order.amount_total and not tx):
			return request.redirect('/shop')


		list_of_order_product = []
		voucher_id = False
		
		if order.voucher_code:
			voucher_obj_by_name = request.env['web.gift.coupon'].search([('name', '=ilike', order.voucher_code)])
			voucher_obj_by_code = request.env['web.gift.coupon'].search([('c_barcode', '=', order.voucher_code)])
			if voucher_obj_by_name:
				dic = {'code':voucher_obj_by_name,'order':order}
				self._apply_coupon(dic)

			if voucher_obj_by_code:
				dic = {'code':voucher_obj_by_code,'order':order}
				self._apply_coupon(dic)                    
					
		if (not order.amount_total and not tx) or tx.state in ['pending', 'done', 'authorized']:
			if (not order.amount_total and not tx):
				# Orders are confirmed by payment transactions, but there is none for free orders,
				# (e.g. free events), so confirm immediately
				order.with_context(send_email=True).action_confirm()
		elif tx and tx.state == 'cancel':
			# cancel the quotation
			order.action_cancel()

		# clean context and session, then redirect to the confirmation page
		request.website.sale_reset()
		if tx and tx.state == 'draft':
			return request.redirect('/shop')

		return request.redirect('/shop/confirmation')
		
	def _apply_coupon(self,arg):
		partner_record_id = request.env['res.users'].browse(request._uid).partner_id.id
		coupon = arg['code']
		order = arg['order']
		discount_value = 0
		if coupon.amount_type == 'fix':
				discount_value = coupon.amount
		elif coupon.amount_type == 'per':
			total = 0
			for i in order.order_line:
				if i.discount_line == False:
					total += i.price_subtotal
			discount_value = ((total * coupon.amount)/100)
		coupon.update({
			'coupon_count': (coupon.coupon_count + 1),
			'max_amount':coupon.max_amount - discount_value,
		})
		order.write({
			'sale_coupon_id': coupon.id
		})
		used_sale_coup_id = coupon.sudo().sale_order_ids.sudo().browse(order.id).sale_coupon_id.id
		curr_vouch_id = coupon.id

		if used_sale_coup_id == curr_vouch_id:
			coupon.sale_order_ids.sudo().update({
				'user_id': http.request.env.context.get('uid'),
			})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
