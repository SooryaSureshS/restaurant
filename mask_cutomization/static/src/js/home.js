odoo.define('mask_cutomization.home', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');
publicWidget.registry.home_page_container = publicWidget.Widget.extend({
    selector: '#home_container',
    events: {
//        'input #upload_file_change': '_upload_file_change',
//        'click .pellete_color': '_change_pellete_color',
//        'click .quantity_minus': '_quantity_minus',
//        'click .quantity_plus': '_quantity_plus',
//        'click .nose_pad_yes_button': '_nose_pad_yes_button',
        'click .order_button': '_order_button',
        'click #overlay': '_image_flex',
        'mouseenter .image_flex': '_onMouseOver',
        'mouseleave .image_flex': '_onMouseOut',
        'click .mobile_click': '_mobile_click',
        'touchstart .mobile_click': '_touchstart',
        'touchend .mobile_click': '_touchend',
    },

    /**
     * @constructor
     */
    init: function () {
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    _onMouseOver: function (ev) {
        var $parent = $(ev.currentTarget).parent();
        var $data = $parent.find('.overlay')
        $data.css('display','block');
        console.log("datata",$data)

    },
    _onMouseOut: function (ev) {
        var $parent = $(ev.currentTarget).parent();
        var $data = $parent.find('.overlay')
        $data.css('display','none');
//        console.log("datataasa",$parent)

    },
    _image_flex: function (ev) {
        var $parent = $(ev.currentTarget).parent();
        var $data = $parent.find('.overlay')
//        $data.css('display','none');

//        console.log("datataasa",$(ev.target).attr('data-value'))
        var product = $(ev.currentTarget).attr('data-value')
        if(product){
            var url = '/product/shop/'+product
            console.log("url",url)
            window.location.href=url
        }
    },
    _mobile_click: function (ev) {
        var self = this;
        var product = $(ev.currentTarget).attr('data-value');
        var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
		if (isMobile && product) {
  			 var url = '/product/shop/'+product
            window.location.href=url
		}
    },
     _touchstart: function (ev) {
        var self = this;
        var $parent = $(ev.currentTarget).parent();
        var $data = $parent.find('.overlay')
        $data.css('display','block');
    },
    _touchend: function (ev) {
        var self = this;
         var $parent = $(ev.currentTarget).parent();
        var $data = $parent.find('.overlay')
        $data.css('display','none');

    },
    _order_button: function (ev) {
        var self = this;
        console
        var product = $(ev.currentTarget).val();
//        var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
		if(product){
            var url = '/product/shop/'+product
            console.log("url",url)
            window.location.href=url
        }
    },

});
publicWidget.registry.footer_scroll = publicWidget.Widget.extend({
    selector: '.conatiner_sky',
    events: {
//        'input #upload_file_change': '_upload_file_change',
//        'click .pellete_color': '_change_pellete_color',
//        'click .quantity_minus': '_quantity_minus',
//        'click .quantity_plus': '_quantity_plus',
//        'click .nose_pad_yes_button': '_nose_pad_yes_button',
        'click .move_to_top': '_move_to_top',
//        'mouseenter .image_flex': '_onMouseOver',
//        'mouseleave .image_flex': '_onMouseOut',
    },

    /**
     * @constructor
     */
    init: function () {
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    _move_to_top: function (ev) {
        $('body').animate({
            scrollTop: 0
        }, 2000);

    }

});
publicWidget.registry.product_details_page = publicWidget.Widget.extend({
    selector: '#product_details_page',
    events: {
        'click #customize_mask': '_customize_mask',
    },
    _customize_mask: function (ev) {
        var self = this;
        console.log("logeddd",self);
        var product = $(ev.target).attr('data-value');
        if (product) {
            var url = '/customize/mask/'+product;
            window.location.href=url
        }

    },
    });
publicWidget.registry.select_your_mask = publicWidget.Widget.extend({
    selector: '#select_your_mask',
    events: {
        'click .adult_button': '_adult_button',
        'click .child_button': '_child_button',
        'click .bread_crumb_skypro': '_bread_crumb_skypro',
    },
    _adult_button: function (ev) {
        var self = this;
        console.log("logeddd",self);
        var product = $(ev.target).attr('data-value');
        if (product) {
            var url = '/print/area/mask/adult/'+product;
            window.location.href=url;
        }
    },
    _child_button: function (ev) {
        var self = this;
        console.log("logeddd",self);
        var product = $(ev.target).attr('data-value');
        if (product) {
            var url = '/print/area/mask/child/'+product;
            window.location.href=url;
        }
     },
     _bread_crumb_skypro: function (ev){
        var self = this;
//        window.location.back();
        window.history.go(-1)
     },
    });


publicWidget.registry.print_area_mask = publicWidget.Widget.extend({
    selector: '#print_area_mask',
    events: {
        'click #logo': '_logo',
        'click #full': '_full',
        'click #blank': '_blank',
        'click .bread_crumb_skypro': '_bread_crumb_skypro',
//        'click .child_button': '_child_button',
//        'click .bread_crumb_skypro': '_bread_crumb_skypro',
    },
    _logo: function (ev) {
        var self = this;
        console.log("logeddd",self);
        var size = $(ev.target).attr('data-size');
        var product = $(ev.target).attr('data-product');
        if (product && size) {
            console.log("sdgfsgdfsfs",product,size)
            var url = '/mask/designing/logo/'+size+'/'+product;
            window.location.href=url;
        }
     },
     _full: function (ev) {
        var self = this;
        console.log("logeddd",self);
        var size = $(ev.target).attr('data-size');
        var product = $(ev.target).attr('data-product');
        if (product && size) {
            console.log("sdgfsgdfsfs",product,size)
            var url = '/mask/designing/full/'+size+'/'+product;
            window.location.href=url;
        }
     },
     _blank: function (ev) {
        var self = this;
        console.log("logeddd",self);
        var size = $(ev.target).attr('data-size');
        var product = $(ev.target).attr('data-product');
        if (product && size) {
            console.log("sdgfsgdfsfs",product,size)
            var url = '/mask/designing/blank/'+size+'/'+product;
            window.location.href=url;
        }
     },
      _bread_crumb_skypro: function (ev){
        var self = this;
//        window.location.back();
        window.history.go(-1)
     },

    });

});