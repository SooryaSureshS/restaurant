odoo.define('bi_website_add_product.bundle_product_modal', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;
    var session = require('web.session');
    var utils = require('web.utils');
    var timeout;
    var wSaleUtils = require('website_sale.utils');
    var core = require('web.core');
    var qweb = core.qweb;

    publicWidget.registry.bundle_modal = publicWidget.Widget.extend({
        selector: '#product_detail',
        events: {
            'click .js_add_plus_bundle': '_js_add_plus',
            'click .js_add_minus_bundle': '_js_add_minus',
            'click .checkout_cart_bundle': '_checkout_cart',
            'click .checkout_shop_bundle': '_checkout_shop',
            'click .close_model_note': '_close_model_note',
            'click .open_choice': '_open_choice',
            'click .close_choice': '_close_choice',
            'click .radio_choice': '_radio_choice',
            'click .product_choice .custom_custom': '_product_choice_custom_custom',
            'click .product_choice .done_custom': '_product_choice_done_custom',
        },

        init: function () {
            var self = this;
            this._super.apply(this, arguments);


        },
        _product_choice_custom_custom: function (ev){
            var self = this;
            var $target = $(ev.currentTarget);
            $target.parent().find('.done_custom').show();
            $target.parent().parent().parent().find('.optional_product').show();
            $target.hide();
        },
        _product_choice_done_custom: function (ev){
            var self = this;
            var $target = $(ev.currentTarget);
            $target.parent().find('.custom_custom').show();
            $target.parent().parent().parent().find('.optional_product').hide();
            $target.hide();
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
            $('#modal_confimation_bundle').hide();
         },
        _open_choice(ev){
            var products_class = ev.currentTarget.value;
            var product_custom = $('#'+products_class+'open').hide();
            var product_done = $('#'+products_class+'close').show();
            var product_data = $('#'+products_class+'data').show();
        },
        _close_choice(ev){
            var products_class = ev.currentTarget.value;
            var product_custom = $('#'+products_class+'open').show();
            var product_done = $('#'+products_class+'close').hide();
            var product_data = $('#'+products_class+'data').hide();
            var next_id = parseInt(products_class)+1;
            var next_data = $('#'+next_id+'data').show();
            var product_done = $('#'+next_id+'open').hide();
            var product_show = $('#'+next_id+'close').show();

            var radio_options = $('.radio_options');
            $(radio_options).each(function(){
                $($(this).find('.radio_choice')).each(function(){
                    console.log("lkjh", $(this));
                    if ($(this)[0].checked == true){
                        console.log("nbv", $(this).parent().parent().parent().parent().find('#popup_req'))
                        $(this).parent().parent().parent().parent().find('#popup_req').hide();
                        $(this).parent().parent().parent().parent().find('#popup_sel').show();
                    }
                })
            })


        },


        _radio_choice(ev){
            var products_class = ev.currentTarget.value;
            var product_choice = $('.product_choice');
            var choice_checked = 0;

            $(product_choice).each(function(){
                var choice_product = '';
                var radio_choice = $(this).find('.radio_choice');
                var bundle_id = radio_choice[0].id;
                $(radio_choice).each(function(){
                    if ($(this)[0].checked == false){
                        choice_checked = choice_checked + 1
                        var choice_product = $(this).attr('variant_id');
                        var choice_count = $(this).attr('choice-count');
                        var choice_custom_val = $(this).attr('custom_val');
                        var check_val = $(this).attr('check_val');
                        var optional_product = product_choice.find('.variant_checkbox');
                        var optional_product_data = []
                        $(optional_product).each(function(){
                            if ($(this).is(":checked")){
                                var variant_id = $(this).attr('variant_id');
                                var choice_data = $(this).attr('variant_value');
                                var variant_check_val = $(this).attr('check_val');
//                                if (variant_check_val == check_val){
//                                $(this).prop('checked', false);
//                                }
                            }
                        });
                    }
                    if ($(this)[0].checked == true){
                        $(this).parent().parent().parent().parent().find('#popup_req').hide();
                        $(this).parent().parent().parent().parent().find('#popup_sel').show();
                    }

                })
            });
        },
        _checkout_cart: function (events){
            var self = this;
            $('.lis-modal').hide();
            var product_id = $('#bundle_product_id').val();
            var text_qty = $('#js_quantity_no_varaible').val();
            var qty = parseInt(text_qty);
            var text = $('#checkout_text_update').val();
            var choice_product_data = [];

            var product_choice = $('.product_choice');
            var choice_checked = 0;

            $(product_choice).each(function(){
                var choice_product = '';
                var radio_choice = $(this).find('.radio_choice');
                var bundle_id = radio_choice[0].id;
                $(radio_choice).each(function(){
                    if ($(this)[0].checked == true){
                        choice_checked = choice_checked + 1
                        var choice_product = $(this).attr('variant_id');
                        var choice_count = $(this).attr('choice-count');
                        var choice_custom_val = $(this).attr('custom_val');
                        var check_val = $(this).attr('check_val');
                        var optional_product = product_choice.find('.variant_checkbox');
                        var optional_product_data = []
                        $(optional_product).each(function(){
                            if ($(this).is(":checked")){
                                var variant_id = $(this).attr('variant_id');
                                var choice_data = $(this).attr('variant_value');
                                var variant_check_val = $(this).attr('check_val');
                                if (variant_check_val == check_val){
                                    optional_product_data.push(variant_id)
                                }
                            }
                        });
                        choice_product_data.push({'choice_product':choice_product, 'variants': optional_product_data})
                    }
                })
            });
            var params ={
                            product_id: product_id,
                            add_qty: qty,
                            checkout_note: text,
                            choice_product_data: choice_product_data,
                        }
                var total_count = document.getElementById("total_product_count").value;
                if (choice_checked < total_count){
                    alert("Select Product from each category")
                }
                else{
                    this._rpc({
                        route: "/shop/cart/update_option/bundle",
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
                    });
                }
        },
        _checkout_shop: function (events){
            var self = this;
            $('.lis-modal').hide();
            var text = $('#checkout_text_update').val();
            var product_id = $('#bundle_product_id').val();
            var text_qty = $('#js_quantity_no_varaible').val();
            var qty = parseInt(text_qty);
            var text = $('#checkout_text_update').val();
            var choice_product_data = [];
            var product_choice = $('.product_choice');
            var choice_checked = 0;

            $(product_choice).each(function(){
                var choice_product = '';
                var radio_choice = $(this).find('.radio_choice');
                var bundle_id = radio_choice[0].id;
                $(radio_choice).each(function(){
                    if ($(this)[0].checked == true){
                        choice_checked = choice_checked + 1
                        var choice_product = $(this).attr('variant_id');
                        var choice_count = $(this).attr('choice-count');
                        var choice_custom_val = $(this).attr('custom_val');
                        var check_val = $(this).attr('check_val');
                        var optional_product = product_choice.find('.variant_checkbox');
                        var optional_product_data = []
                        $(optional_product).each(function(){
                            if ($(this).is(":checked")){
                                var variant_id = $(this).attr('variant_id');
                                var choice_data = $(this).attr('variant_value');
                                var variant_check_val = $(this).attr('check_val');
                                if (variant_check_val == check_val){
                                    optional_product_data.push(variant_id)
                                }
                            }
                        });
                        choice_product_data.push({'choice_product':choice_product, 'variants': optional_product_data})
                    }
                })
            });
            var params ={   product_id: product_id,
                            add_qty: qty,
                            checkout_note: text,
                            choice_product_data: choice_product_data,
                        }
                var total_count = document.getElementById("total_product_count").value;
                if (choice_checked < total_count){
                    alert("Select Product from each category")
                }
                else{
                    this._rpc({
                        route: "/shop/cart/update_option/bundle",
                        params: params,
                    }).then(function (data) {
                        wSaleUtils.updateCartNavBar(data);
                        var $navButton = $('header .o_wsale_my_cart').first();
                        if(data){
                            if(data>0){
                                $navButton.find('.my_cart_quantity').text(data)
                            }
                        }
                        $('#modal_confimation_bundle').hide();
                    });
            }
        },

    });
    publicWidget.registry.bundle_modal_details = publicWidget.Widget.extend({
        selector: '.o_wsale_products_main_row',
        events: {
            'click .js_add_plus_bundle': '_js_add_plus',
            'click .js_add_minus_bundle': '_js_add_minus',
            'click .checkout_cart_bundle': '_checkout_cart',
            'click .checkout_shop_bundle': '_checkout_shop',
            'click .close_model_note': '_close_model_note',
            'click .open_choice': '_open_choice',
            'click .close_choice': '_close_choice',
            'click .radio_choice': '_radio_choice',
            'click .product_choice .custom_custom': '_product_choice_custom_custom',
            'click .product_choice .done_custom': '_product_choice_done_custom',

        },

        init: function () {
            var self = this;
            this._super.apply(this, arguments);


        },
        _product_choice_custom_custom: function (ev){
            var self = this;
            var $target = $(ev.currentTarget);
            $target.parent().find('.done_custom').show();
            $target.parent().parent().parent().find('.optional_product').show();
            $target.hide();

        },
         _product_choice_done_custom: function (ev){
            var self = this;
            var $target = $(ev.currentTarget);
            $target.parent().find('.custom_custom').show();
            $target.parent().parent().parent().find('.optional_product').hide();
            $target.hide();

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
            $('#modal_confimation_bundle').hide();
         },
        _radio_choice(ev){
            var products_class = ev.currentTarget.value;
            var product_choice = $('.product_choice');
            var choice_checked = 0;

            $(product_choice).each(function(){
                var choice_product = '';
                var radio_choice = $(this).find('.radio_choice');
                var bundle_id = radio_choice[0].id;
                $(radio_choice).each(function(){
                    if ($(this)[0].checked == false){
                        choice_checked = choice_checked + 1
                        var choice_product = $(this).attr('variant_id');
                        var choice_count = $(this).attr('choice-count');
                        var choice_custom_val = $(this).attr('custom_val');
                        var check_val = $(this).attr('check_val');
                        var optional_product = product_choice.find('.variant_checkbox');
                        var optional_product_data = []
                        $(optional_product).each(function(){
                            if ($(this).is(":checked")){
                                var variant_id = $(this).attr('variant_id');
                                var choice_data = $(this).attr('variant_value');
                                var variant_check_val = $(this).attr('check_val');
//                                if (variant_check_val == check_val){
//                                    $(this).prop('checked', false);
//                                }
                            }
                        });
                    }
                    if ($(this)[0].checked == true){
                        $(this).parent().parent().parent().parent().find('#popup_req').hide();
                        $(this).parent().parent().parent().parent().find('#popup_sel').show();
                    }

                })
            });
        },
        _open_choice(ev){
            var products_class = ev.currentTarget.value;
            var product_custom = $('#'+products_class+'open').hide();
            var product_done = $('#'+products_class+'close').show();
            var product_data = $('#'+products_class+'data').show();
        },
        _close_choice(ev){
            var products_class = ev.currentTarget.value;
            var product_custom = $('#'+products_class+'open').show();
            var product_done = $('#'+products_class+'close').hide();
            var product_data = $('#'+products_class+'data').hide();
            var next_id = parseInt(products_class)+1;
            var next_data = $('#'+next_id+'data').show();
            var product_done = $('#'+next_id+'open').hide();
            var product_show = $('#'+next_id+'close').show();
            var radio_options = $('.radio_options');
            $(radio_options).each(function(){
                $($(this).find('.radio_choice')).each(function(){
                    if ($(this)[0].checked == true){
                        $(this).parent().parent().parent().parent().find('#popup_req').hide();
                        $(this).parent().parent().parent().parent().find('#popup_sel').show();
                    }
                })
            })

        },

        _checkout_cart: function (events){
            var self = this;
            $('.lis-modal').hide();
            var product_id = $('#bundle_product_id').val();
            var text_qty = $('#js_quantity_no_varaible').val();
            var qty = parseInt(text_qty);
            var text = $('#checkout_text_update').val();
            var choice_product_data = [];

            var product_choice = $('.product_choice');
            var choice_checked = 0;

            $(product_choice).each(function(){
                var choice_product = '';
                var radio_choice = $(this).find('.radio_choice');
                var bundle_id = radio_choice[0].id;
                $(radio_choice).each(function(){
                    if ($(this)[0].checked == true){
                        choice_checked = choice_checked + 1
                        var choice_product = $(this).attr('variant_id');
                        var choice_count = $(this).attr('choice-count');
                        var choice_custom_val = $(this).attr('custom_val');
                        var check_val = $(this).attr('check_val');
                        var optional_product = product_choice.find('.variant_checkbox');
                        var optional_product_data = []
                        $(optional_product).each(function(){
                            if ($(this).is(":checked")){
                                var variant_id = $(this).attr('variant_id');
                                var choice_data = $(this).attr('variant_value');
                                var variant_check_val = $(this).attr('check_val');
                                if (variant_check_val == check_val){
                                    optional_product_data.push(variant_id)
                                }
                            }
                        });
                        choice_product_data.push({'choice_product':choice_product, 'variants': optional_product_data})
                    }
                })
            });
            var params ={
                            product_id: product_id,
                            add_qty: qty,
                            checkout_note: text,
                            choice_product_data: choice_product_data,
                        }
                var total_count = document.getElementById("total_product_count").value;
                if (choice_checked < total_count){
                    alert("Select Product from each category")
                }
                else{
                    this._rpc({
                        route: "/shop/cart/update_option/bundle",
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
                    });
                }
        },
        _checkout_shop: function (events){
            var self = this;
            $('.lis-modal').hide();
            var text = $('#checkout_text_update').val();
            var product_id = $('#bundle_product_id').val();
            var text_qty = $('#js_quantity_no_varaible').val();
            var qty = parseInt(text_qty);
            var text = $('#checkout_text_update').val();
            var choice_product_data = [];
            var product_choice = $('.product_choice');
            var choice_checked = 0;

            $(product_choice).each(function(){
                var choice_product = '';
                var radio_choice = $(this).find('.radio_choice');
                var bundle_id = radio_choice[0].id;
                $(radio_choice).each(function(){
                    if ($(this)[0].checked == true){
                        choice_checked = choice_checked + 1
                        var choice_product = $(this).attr('variant_id');
                        var choice_count = $(this).attr('choice-count');
                        var choice_custom_val = $(this).attr('custom_val');
                        var check_val = $(this).attr('check_val');
                        var optional_product = product_choice.find('.variant_checkbox');
                        var optional_product_data = []
                        $(optional_product).each(function(){
                            if ($(this).is(":checked")){
                                var variant_id = $(this).attr('variant_id');
                                var choice_data = $(this).attr('variant_value');
                                var variant_check_val = $(this).attr('check_val');
                                if (variant_check_val == check_val){
                                    optional_product_data.push(variant_id)
                                }
                            }
                        });
                        choice_product_data.push({'choice_product':choice_product, 'variants': optional_product_data})
                    }
                })
            });
            var params ={   product_id: product_id,
                            add_qty: qty,
                            checkout_note: text,
                            choice_product_data: choice_product_data,
                        }
                var total_count = document.getElementById("total_product_count").value;
                if (choice_checked < total_count){
                    alert("Select Product from each category")
                }
                else{
                    this._rpc({
                        route: "/shop/cart/update_option/bundle",
                        params: params,
                    }).then(function (data) {
                        wSaleUtils.updateCartNavBar(data);
                        var $navButton = $('header .o_wsale_my_cart').first();
                        if(data){
                            if(data>0){
                                $navButton.find('.my_cart_quantity').text(data)
                            }
                        }
                        $('#modal_confimation_bundle').hide();
                    });
            }
        },

    });
});
