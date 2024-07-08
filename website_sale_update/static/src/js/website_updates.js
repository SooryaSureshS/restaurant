odoo.define('website_sale_update.website_updates', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;

publicWidget.registry.website_updates = publicWidget.Widget.extend({
    selector: '#wrapwrap',
    events: {
//        'scroll': '_movescroll',
//        'mouseleave': '_onMouseLeave',
//        'click': '_onClick',
        'click #top_menu a[href="/shop"]': '_onshop_click',
    },
//
//    /**
//     * @constructor
//     */
    init: function () {
        var self = this;
        var shop_cookie = utils.get_cookie('shop_click')
        this._super.apply(this, arguments);
        if (shop_cookie){
            console.log("if",shop_cookie)
            if (window.location.pathname == '/shop'){
                 var scrollContainer = document.getElementById('wrapwrap');
                            scrollContainer.scrollTo({
                                top: ($(".shop-page-banner").offset().top)-50,
                                left: 0,
                                behavior: 'auto'
                            });
            }
//            oe_website_sale
        }else{
//              console.log("else",shop_cookie)
//        }
        var pre_position = utils.get_cookie('pre_position')
        var current_position = utils.get_cookie('current_position')
        if(pre_position){
            if (window.location.pathname == pre_position.split("@")[0]){
                 var scrollContainer = document.getElementById('wrapwrap');
                            scrollContainer.scrollTo({
                                top: pre_position.split("@")[1],
                                left: 0,
                                behavior: 'auto'
                            });
            }
        }
        if(current_position){
            if (window.location.pathname == current_position.split("@")[0]){
                 var scrollContainer = document.getElementById('wrapwrap');
                            scrollContainer.scrollTo({
                                top: current_position.split("@")[1],
                                left: 0,
                                behavior: 'auto'
                            });
            }
        }
        }
        $('#wrapwrap').scroll(function (event) {
            var scroll = $('#wrapwrap').scrollTop();
            $("#wrap").scrollLeft()
            if (scroll > 0 ){
                self.do_something_store(scroll);
            }
        });

    },
    do_something_store: function(scroll){
        var self = this;
        var lang = utils.get_cookie('frontend_lang')
        var position = [];
        var pre_position = utils.get_cookie('pre_position')
        var current_position = utils.get_cookie('current_position')
        var log = window.location.pathname+"@"+scroll
        if(current_position){
            if (window.location.pathname == current_position.split("@")[0]){
                utils.set_cookie('current_position', log)
            }else{
                utils.set_cookie('pre_position', current_position)
                utils.set_cookie('current_position', log)
            }

        }else{
            utils.set_cookie('current_position', log)

        }
        utils.set_cookie('menu_category_click', false)
        var pre_position = utils.get_cookie('pre_position')
        var current_position = utils.get_cookie('current_position')

    },
    _onshop_click: function(ev){
        var self = this;
        utils.set_cookie('shop_click', true,2)
    },
    });


    publicWidget.registry.website_menu_click = publicWidget.Widget.extend({
            selector: '#o_shop_collapse_category',
            events: {
                'click li a': '_menu_click_category',
            },
            init: function () {
                var self = this;
                this._super.apply(this, arguments);
            },
            _menu_click_category: function(ev){
                var self = this;
                utils.set_cookie('menu_category_click', true)
            },
    });

    publicWidget.registry.website_reload_space = publicWidget.Widget.extend({
            selector: '#wrapwrap',
            init: function () {
                var self = this;
                var menu_category_click = utils.get_cookie('menu_category_click');
                $(document).ready(function(){
                     if(!self.$el.find('#oe_product_cart_id .o_wsale_product_information_text #add_to_cart').is(":visible")){
                         if(menu_category_click){
                            if(menu_category_click == 'true'){
                            var scrollContainer = document.getElementById('wrapwrap');
                                if($(".o_wsale_product_grid_wrapper").offset()){
                                 scrollContainer.scrollTo({
                                    top: ($(".o_wsale_product_grid_wrapper").offset().top),
                                    left: 0,
                                    behavior: 'auto'
                                });
                                }

                            }

                         }

                    }
                });
                this._super.apply(this, arguments);
            },
    });
});