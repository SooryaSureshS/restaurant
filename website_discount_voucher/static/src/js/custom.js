
// console.log("odoo_website_giftwrap custom js caleedddddddddddddddddddddddddddddddddd")
odoo.define('odoo_website_giftwrap.odoo_website_giftwrap', function(require) {
	"use strict";

	var core = require('web.core');
	var _t = core._t;
	var ajax = require('web.ajax');
	// var rpc = require('web.rpc');

	$(document).ready(function() {
		$('#apply_voucher').on('click', function() {
			var code = $("#code").val();

			ajax.jsonRpc('/shop/voucher', 'call', {
				'promo': code,
			}).then(function (output) {
				if(output != true)
				{
					var err = '/shop/cart?gift_msg='+output
					window.location.href = err;
				}
				else{
					location.reload();
				}
				
				
			});
		});
	});
});;
