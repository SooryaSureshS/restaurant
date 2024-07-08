odoo.define('bi_website_add_product.cart_lines', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;
var wSaleUtils = require('website_sale.utils');
var core = require('web.core');
var qweb = core.qweb;


publicWidget.registry.cart_products_hide = publicWidget.Widget.extend({
    selector: '.oe_cart #cart_products',
    events: {
    },
//
//    /**
//     * @constructor
//     */
    init: function () {
        var self = this;
        this._super.apply(this, arguments);
        $('#cart_products tr').each(function (){
            var $tr = $(this);
            if ($(this).find('.td-product_name').text().includes('Holiday surcharge')){
                $tr.hide();
            }
        });

    },

});

});