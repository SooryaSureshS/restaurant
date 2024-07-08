# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	'name': 'Website Coupons & Vouchers in Odoo Shop',
	'summary': 'Apps website discount Coupons shore Gift Vouchers Discount website Discount Coupons website gift Discount pos discount website discount website promo Discount website offer discount store Vouchers webshop gifts website discount Vouchers website offers',
	'description': """

				A promotional tool called “vouchers” are essentially provided by the sellers to increase sales, to become competitive, to re-activate old customers. Those customers that have been lured away by your competitors will start buying from you again when you give them a good reason to do so.

They feel special and privileged to get voucher codes for discounts to be applied on the cart. Voucher allows you to generate codes, which can be used to provide flat or percentage based discount on a customers order. It will be applicable on the store front checkout. Additional filtering can be applied so that customer uses voucher for single time use spends certain amount for a specific time period to access the voucher code.


Module to send an email offering discount voucher to customer one week before Birthday and Father's Day. Modules provides a feature to send a discount voucher when New user is created.
Website discount vouchers ,Website gift discount ,Website promotion , website promo coupon, website promo code ,website promo coupon 
website promotional discount ,website Gift Coupons Discount in website Gift Coupons Discount website vouchers discount website gift vouchers discount
website discount coupon, website gift discount, website discount vouhcer, website coupon discount, website voucher coupon 
website coupons discount,Website Discount, website Gift Vouchers,website discount Coupons
website coupon code,website promo-code,website promocode,Discount on website,Gift Deducation on website,Website deducation
Gift Voucher on website
   
webshop discount vouchers ,webshop gift discount ,webshop promotion , webshop promo coupon, webshop promo code ,webshop promo coupon 
webshop promotional discount ,webshop Gift Coupons Discount in webshop Gift Coupons Discount webshop vouchers discount webshop gift vouchers discount
webshop discount coupon, webshop gift discount, webshop discount vouhcer, webshop coupon discount, webshop voucher coupon 
webshop coupons discount,webshop Discount, webshop Gift Vouchers,webshop discount Coupons
webshop coupon code,webshop promo-code,webshop promocode,Discount on webshop,Gift Deducation on webshop,webshop deducation
Gift Voucher on webshop

eCommerce discount vouchers ,eCommerce gift discount ,eCommerce promotion , eCommerce promo coupon, eCommerce promo code ,eCommerce promo coupon 
eCommerce promotional discount ,eCommerce Gift Coupons Discount in eCommerce Gift Coupons Discount eCommerce vouchers discount eCommerce gift vouchers discount
eCommerce discount coupon, eCommerce gift discount, eCommerce discount vouhcer, eCommerce coupon discount, eCommerce voucher coupon 
eCommerce coupons discount,eCommerce Discount, eCommerce Gift Vouchers,eCommerce discount Coupons
eCommerce coupon code,eCommerce promo-code,eCommerce promocode,Discount on eCommerce,Gift Deducation on eCommerce,eCommerce deducation
Gift Voucher on eCommerce

	""",
	"category": 'Website',
	'author': 'BrowseInfo',
	'version' : '14.0.0.0',
	'price': 55,
	'currency': "EUR",
	'website': 'https://www.browseinfo.in',
	'depends': ['base','sale_management','website','website_sale','barcodes'],
	'data': [
		'views/web_gift_coupon.xml',
		'views/report_web_gift_coupon.xml',
		'views/template.xml',
		'views/views.xml',
		'security/ir.model.access.csv',
	],
	'installable': True,
	"live_test_url": "https://youtu.be/xPKzfhf-_lo",
	"images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
