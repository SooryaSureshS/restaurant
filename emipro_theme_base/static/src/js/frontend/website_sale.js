odoo.define('emipro_theme_base.website_sale', function(require) {
    'use strict';

    const publicWidget = require('web.public.widget');
    var WebsiteSale = require('website_sale.website_sale');
    var VariantMixin = require('sale.VariantMixin');
    var timer;
    var core = require('web.core');
    var _t = core._t;
    const { OptionalProductsModal } = require('@sale_product_configurator/js/product_configurator_modal');


    publicWidget.registry.WebsiteSale.include({

        _onChangeCombination: function(ev, $parent, combination) {

            this._super.apply(this, arguments);
            $('.td-product_name .product-name');
            $(".js_sku_div").html('N/A');
            if (combination.sku_details) {
                $(".js_sku_div").html(combination.sku_details);
            }
            $(".js_product .te_discount, .js_product .te_discount_before").addClass('d-none');
            $(".js_product .te_discount, .js_product .te_percentage").hide()
            if (combination.has_discounted_price) {
                $(".js_product .te_discount, .js_product .te_discount_before").removeClass('d-none');
                var difference = combination.list_price - combination.price;
                var discount = difference * 100 / combination.list_price;
                if (discount > 0) {
                    $(".js_product .te_discount_before .oe_currency_value").html(difference.toFixed(2));
                    $(".js_product .te_discount .te_percentage .percent_val").html(discount.toFixed(2));
                    $(".js_product .te_discount, .js_product .te_percentage").show()
                }
            }
            if($('#id_lazyload').length) {
                $('img.lazyload').lazyload();
            }
        },
        _onChangeAttribute: function(ev) {
            $('.cus_theme_loader_layout').removeClass('d-none');
            this._super.apply(this, arguments);
        },
    });
    OptionalProductsModal.include({
        _onChangeCombination: function (ev, $parent, combination) {
            this._super.apply(this, arguments);

            $parent.find('.td-price .te_discount').addClass('d-none')
            $parent.find('.td-price .te_discount_option').addClass('d-none')

            if (combination.has_discounted_price) {

                var difference = combination.list_price - combination.price;
                var discount = difference * 100 / combination.list_price;
                if (discount > 0) {
                    $parent.find('.td-price .te_discount').removeClass('d-none')
                    $parent.find('.td-price .te_discount_option').removeClass('d-none')

                    $parent.find('.te_discount .percent_val').html(discount.toFixed(2));
                    $parent.find('.te_discount_option .percent_val_option').html(discount.toFixed(2));
                }
            }
        },
    });
});
