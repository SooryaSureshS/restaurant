odoo.define('bi_website_add_product.bundle_product', function (require) {
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
var ajax = require('web.ajax');

publicWidget.registry.bundle_product = publicWidget.Widget.extend({
        selector: '.o_wsale_products_main_row',
        xmlDependencies: ['/bi_website_add_product/static/src/xml/PopUp_bundle_products.xml'],
        events: {
        'click #add_to_cart_bundle': '_onClick_add_cart_bundle',
        },
        init: function () {
            var self = this;
            this._super.apply(this, arguments);
        },
        _onClick_add_cart_bundle: function (ev){

            var self = this;
            var product_id = $(ev.currentTarget).attr('data-product-product-id');
            self.target_animation = $(ev.currentTarget);
            ajax.jsonRpc('/shop/get_bundle_data/', 'call', {'product_id': product_id})
            .then(function(response) {
                if(response){

                    self.$el.prepend(qweb.render('bi_website_add_product.PopUp_bundle_products', {'data': response}));
                }

            });
        },

    });

publicWidget.registry.bundle_product_detail = publicWidget.Widget.extend({
        selector: '#product_detail',
        xmlDependencies: ['/bi_website_add_product/static/src/xml/PopUp_bundle_products.xml'],
        events: {
        'click #add_to_cart_bundle_detail': '_onClick_add_cart_bundle',
        },
        init: function () {

            var self = this;
            this._super.apply(this, arguments);
        },
        _onClick_add_cart_bundle: function (ev){

            var self = this;
            var product_id = $(ev.currentTarget).attr('data-product-product-id');
            self.target_animation = $(ev.currentTarget);
            ajax.jsonRpc('/shop/get_bundle_data/', 'call', {'product_id': product_id})
            .then(function(response) {
                if(response){
                    self.$el.prepend(qweb.render('bi_website_add_product.PopUp_bundle_products_details', {'data': response}));
                }

            });
        },

    });

});