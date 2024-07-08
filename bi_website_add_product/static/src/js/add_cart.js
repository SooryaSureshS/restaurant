odoo.define('bi_website_add_product.add_cart', function (require) {
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

publicWidget.registry.add_cart_details = publicWidget.Widget.extend({
    selector: '#product_detail',
    xmlDependencies: ['/bi_website_add_product/static/src/xml/products_popup_detail.xml'],
    events: {
//        'scroll': '_movescroll',
//        'mouseleave': '_onMouseLeave',_close_model_note
        'click .cart-button': '_onClick_add_cart',
        'click .onit_note_confirm_new': '_onit_note_confirm',
        'click .close_model_note': '_close_model_note',
        'click .checkout_cart': '_checkout_cart',
        'click .js_add_plus': '_js_add_plus',
        'click .js_add_minus': '_js_add_minus',

    },
//
//    /**
//     * @constructor
//     */
    init: function () {
        var self = this;
        this._super.apply(this, arguments);


    },
    _js_add_minus: function (events){
     var text = $('#js_quantity_no_varaible').val();
     var qty = parseInt(text);
     if (qty!==1){
     var change_qty = parseInt(text)-1;
     $('#js_quantity_no_varaible').val(change_qty);
     }

     },
    _js_add_plus: function (events){
     var text = $('#js_quantity_no_varaible').val();
     var qty = parseInt(text)+1;
     $('#js_quantity_no_varaible').val(qty);
     },
     _close_model_note: function (events){
     $('#modal_confimation_order_note_detail').hide();
     },
      _checkout_cart: function (events){
           var self = this;
           $('.lis-modal').hide();
           var product_id = $('#cart_popup_attribute').attr('data-product_id')
             var text_qty = $('#js_quantity_no_varaible').val();
            var qty = parseInt(text_qty);
          var text = $('#checkout_text_update').val();
          var params ={
                        product_id: product_id,
                        add_qty: qty,checkout_note: text}
          console.log("order onfo",text)
               this._rpc({
                    route: "/shop/cart/update_with_values",
                    params: params,
                }).then(function (data) {
                    wSaleUtils.updateCartNavBar(data);
                    var $navButton = $('header .o_wsale_my_cart').first();
                    if(data){
                        if(data>0){
                            $navButton.find('.my_cart_quantity').text(data)
                        }
                    }
                    window.location.href = '/shop/cart';

//                    setTimeout(function(){  window.location.href = '/shop/cart'; }, 3000);

                });
     },
    _onit_note_confirm: function (events){
          var self = this;
           $('.lis-modal').hide();
          var text = $('#checkout_text_update').val();
          var product_id = $('#cart_popup_attribute').attr('data-product_id')
            var text_qty = $('#js_quantity_no_varaible').val();
            var qty = parseInt(text_qty);
          console.log("order onfo",text)
               this._rpc({
                    route: "/shop/cart/update_with_values",
                    params: {
                        product_id: product_id,
                        add_qty: qty,
                        checkout_note: text
                    },
                }).then(function (data) {
                    wSaleUtils.updateCartNavBar(data);
                    var $navButton = $('header .o_wsale_my_cart').first();
                    if(data){
                        if(data>0){
                            $navButton.find('.my_cart_quantity').text(data)
                        }
                    }
                    $('#modal_confimation_order_note_detail').hide();
                });
        },

    _onClick_add_cart: function (ev){
        var self = this;
        self.target_animation = $(ev.currentTarget);
        var $card = $(ev.currentTarget).closest('.card');
        var product_id = $(ev.currentTarget).attr('data-product-product-id');
        console.log("KKKKKKKK",self,product_id)
                this._rpc({
                    route: "/get/novariable/popup/details",
                    params: {
                        product_id: product_id,
                    },
                }).then(function (data) {
                if(data){
                                     self.$el.prepend(qweb.render('bi_website_add_product.products_popup_detail', data));

                }
                });

    },

    _onClick_add_cart_mobile: function(){
        var self = this;
        console.log("colapse",self)
    },

});

publicWidget.registry.add_cart = publicWidget.Widget.extend({
    selector: '.o_wsale_products_main_row',
    xmlDependencies: ['/bi_website_add_product/static/src/xml/products_popup.xml'],
    events: {
//        'scroll': '_movescroll',
//        'mouseleave': '_onMouseLeave',
        'click .cart-button': '_onClick_add_cart',
        'click .onit_note_confirm_new': '_onit_note_confirm',
        'click .close_model_note': '_close_model_note',
        'click .checkout_cart': '_checkout_cart',
        'click .js_add_plus': '_js_add_plus',
        'click .js_add_minus': '_js_add_minus',

    },
//
//    /**
//     * @constructor
//     */
    init: function () {
        var self = this;
        this._super.apply(this, arguments);


    },
    _js_add_minus: function (events){
     var text = $('#js_quantity_no_varaible').val();
     var qty = parseInt(text);
     if (qty!==1){
     var change_qty = parseInt(text)-1;
     $('#js_quantity_no_varaible').val(change_qty);
     }

     },
    _js_add_plus: function (events){
     var text = $('#js_quantity_no_varaible').val();
     var qty = parseInt(text)+1;
     $('#js_quantity_no_varaible').val(qty);
     },
     _close_model_note: function (events){
     $('#modal_confimation_order_note').hide();
     },
      _checkout_cart: function (events){
           var self = this;
           $('.lis-modal').hide();
           var product_id = $('#cart_popup_attribute').attr('data-product_id')
             var text_qty = $('#js_quantity_no_varaible').val();
            var qty = parseInt(text_qty);
          var text = $('#checkout_text_update').val();
          var params ={
                        product_id: product_id,
                        add_qty: qty,checkout_note: text}
          console.log("order onfo",text)
               this._rpc({
                    route: "/shop/cart/update_with_values",
                    params: params,
                }).then(function (data) {
                    wSaleUtils.updateCartNavBar(data);
                    var $navButton = $('header .o_wsale_my_cart').first();
                    if(data){
                        if(data>0){
                            $navButton.find('.my_cart_quantity').text(data)
                        }
                    }
                    window.location.href = '/shop/cart';

//                    setTimeout(function(){  window.location.href = '/shop/cart'; }, 3000);

                });
     },
    _onit_note_confirm: function (events){
          var self = this;
           $('.lis-modal').hide();
          var text = $('#checkout_text_update').val();
          var product_id = $('#cart_popup_attribute').attr('data-product_id')
            var text_qty = $('#js_quantity_no_varaible').val();
            var qty = parseInt(text_qty);
          console.log("order onfo",text)
               this._rpc({
                    route: "/shop/cart/update_with_values",
                    params: {
                        product_id: product_id,
                        add_qty: qty,
                        checkout_note: text
                    },
                }).then(function (data) {
                    wSaleUtils.updateCartNavBar(data);
                    var $navButton = $('header .o_wsale_my_cart').first();
                    if(data){
                        if(data>0){
                            $navButton.find('.my_cart_quantity').text(data)
                        }
                    }
                    $('#modal_confimation_order_note').hide();
                });
        },

    _onClick_add_cart: function (ev){
        var self = this;
        self.target_animation = $(ev.currentTarget);
        var $card = $(ev.currentTarget).closest('.card');
        var product_id = $(ev.currentTarget).attr('data-product-product-id');
        console.log("KKKKKKKK",self)
                this._rpc({
                    route: "/get/novariable/popup/details",
                    params: {
                        product_id: product_id,
                    },
                }).then(function (data) {
                if(data){
                                     self.$el.prepend(qweb.render('bi_website_add_product.products_popup', data));

                }
                });


//               this._rpc({
//                    route: "/shop/cart/update_with_values",
//                    params: {
//                        product_id: $(ev.currentTarget).attr('data-product-product-id'),
//                        add_qty: 1
//                    },
//                }).then(function (data) {
//                    wSaleUtils.updateCartNavBar(data);
//                    var $navButton = $('header .o_wsale_my_cart').first();
//                    if(data){
//                        if(data>0){
//                            $navButton.find('.my_cart_quantity').text(data)
//                        }
//
//                    }
//
//                    var animation = wSaleUtils.animateClone($navButton, $(ev.currentTarget).parents('.o_carousel_product_card'), 25, 40);
//                    Promise.all([ animation]).then(function (values) {
//        //                self._render(values[0]);my_cart_quantity
//
//                    });
//                });
//        }

    },

    _onClick_add_cart_mobile: function(){
        var self = this;
        console.log("colapse",self)
    },


    });


    publicWidget.registry.bizople_header = publicWidget.Widget.extend({
            selector: '#bizople_header',
            events: {
                'click .collapse-btn button': '_onClick_add_cart_mobile',
            },
        //
        //    /**
        //     * @constructor
        //     */
            init: function () {
                var self = this;
                this._super.apply(this, arguments);
            },
            _onClick_add_cart_mobile: function (ev){
                var self = this;
                this._rpc({
                    route: "/shop/cart/update_qty_data",
                    params: {
                    },
                }).then(function (data) {
                    wSaleUtils.updateCartNavBar(data);
                    var $navButton_mobile = $('#top_menu .cart').first();
                    if(data){
                        if(data>0){
                            $navButton_mobile.find('.my_cart_quantity').text(data)
                        }
                    }

                    var animation = wSaleUtils.animateClone($navButton_mobile, $(ev.currentTarget).parents('.o_carousel_product_card'), 25, 40);
                    Promise.all([ animation]).then(function (values) {
//        //                self._render(values[0]);my_cart_quantity
//
                    });
                });
            },
    });


publicWidget.registry.o_wsale_products_grid_table_wrapper = publicWidget.Widget.extend({
    selector: '.o_wsale_products_grid_table_wrapper',

    init: function () {
        var self = this;

        $('.o_wsale_products_grid_table_wrapper').load(window.location.href + " .o_wsale_products_grid_table_wrapper" ,function() {
             if(self.$el.find('#oe_product_cart_id .o_wsale_product_information_text #add_to_cart').is(":visible")){
                self.$el.find('#oe_product_cart_id .product_price_otional .add_to_cart_large_scree_hide').removeClass('add_to_cart_unhide');
                console.log("pc")
            }else{
                console.log("mobile")
                self.$el.find('#oe_product_cart_id .product_price_otional .add_to_cart_large_scree_hide').addClass('add_to_cart_unhide');
            }
        });

//         $(document).ready(function(){
//            if(self.$el.find('#oe_product_cart_id .o_wsale_product_information_text #add_to_cart').is(":visible")){
////                self.$el.find('#oe_product_cart_id .o_wsale_product_information_text #add_to_cart').show();
////                self.$el.find('#oe_product_cart_id .product_price_otional .add_to_cart_large_scree_hide').hide();
//                self.$el.find('#oe_product_cart_id .product_price_otional .add_to_cart_large_scree_hide').removeClass('add_to_cart_unhide');
//                console.log("pc")
//            }else{
//                console.log("mobile")
//                self.$el.find('#oe_product_cart_id .product_price_otional .add_to_cart_large_scree_hide').addClass('add_to_cart_unhide');
////                self.$el.find('#oe_product_cart_id .o_wsale_product_information_text #add_to_cart').hide();
//            }
//        });
        this._super.apply(this, arguments);
    },
    });

});