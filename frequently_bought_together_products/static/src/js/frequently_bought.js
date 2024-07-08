
 /* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('frequently_bought_together_products.frequently_bought_together_products', function (require) {
"use strict";

$(document).ready(function()
{
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;
    var utils = require('web.utils');
    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;

         function price_to_str(price) {
            var l10n = _t.database.parameters;
            var precision = 2;
            if ($(".decimal_precision").length) {
                precision = parseInt($(".decimal_precision").last().data('precision'));
            }
            var formatted = _.str.sprintf('%.' + precision + 'f', price).split('.');
            formatted[0] = utils.insert_thousand_seps(formatted[0]);
            return formatted.join(l10n.decimal_point);
        }

        function change_fbp_total_price($supParent) {
            var total_web_price = 0
            var total_def_price = 0
            $supParent.find('input.fbp_product:checked').each(function () {
               var  $p1 = $(this).closest('.fbp-item').find('.fbp_variant_id').find(":selected").attr('website_price');
               var $p2 = $(this).closest('.fbp-item').find('.fbp_variant_id').find(":selected").attr('default_price');
               total_web_price += parseFloat($p1)
               total_def_price += parseFloat($p2)
            });
            $supParent.find('.fbp_total_price .total-default-price .oe_currency_value').text(price_to_str(parseFloat(total_def_price)));
            $supParent.find('.fbp_total_price .fbp-total-price .oe_currency_value').text(price_to_str(parseFloat(total_web_price)));
            if (parseFloat(total_def_price) > parseFloat(total_web_price))
            {
                $supParent.find('.fbp_total_price .total-default-price').show();
            }
            else{
                $supParent.find('.fbp_total_price .total-default-price').hide();
            }

         }

        $('.fbp-item ').on('change', '.fbp_variant_id',  function (ev) {
            var $selected_option = $(this).find(":selected");
            var $price = $selected_option.attr('website_price');
            var $default_price = $selected_option.attr('default_price');
            var $parent = $(this).closest('.fbp-item')
            $parent.find('.price').find(".wk_default_price .oe_currency_value").text(price_to_str(parseFloat($default_price)));
            $parent.find('.price').find('.wk_price .oe_currency_value').text(price_to_str(parseFloat($price)));
            var  $supParent= $(this).closest('.fbp-container');
            change_fbp_total_price($supParent);
        });

        $('.fbp-item ').on('click', 'input.fbp_product',  function (ev) {
            var  $supParent= $(this).closest('.fbp-container');
            change_fbp_total_price($supParent);
            if ($(this).is(":checked"))
            {
                $(this).closest('.fbp-item').css({'opacity':'1','background-color': '#EEEEEE'});
            }
            else{
                $(this).closest('.fbp-item').css({'opacity':'0.5','background-color': '#F5F5F5'});
            }
        });

        $('.fbp-container').on('click', '.fbp-add_to_cart', function (ev) {
            var values = [];
            $('.fbp-container').find('input.fbp_product:checked').each(function () {
               var  $id = $(this).closest('.fbp-item').find('.fbp_variant_id').find(":selected").val();
               values.push($id);
            });
            ajax.jsonRpc("/frequently/bought/add_to_cart", 'call', {'product_ids': values}).then(function(data)
            {
                location.pathname="/shop/cart";
            });


        });
    });
});
});
