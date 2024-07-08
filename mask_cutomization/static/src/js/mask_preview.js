odoo.define('mask_cutomization.mask_preview', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');
publicWidget.registry.MaskCustomizationPreview = publicWidget.Widget.extend({
    selector: '#MaskCustomizationPreview',
    events: {
//        'input #player_kit': '_player_kit',
//        'input #player_kit': '_player_kit',
        'click .fold_button': '_fold_button',
        'click .3d_button': '_3d_button',
        'click .image_button': '_image_button',
        'click .product_packaging': '_product_packaging',
        'click #gui_back': '_gui_back',
    },

    /**
     * @constructor
     */
    init: function () {
     console.log("****************************8")
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        var product = $('#product').val();
        var line = $('#line').val();


        $('.all_btn').each(function (){
            $(this).removeClass('active_block')
            $(this).removeClass('active_none')
        });
        $('.fold_button').last().trigger('click');
        return this._super.apply(this, arguments);
    },
    _fold_button: function (ev){
        var self = this;
        console.log("datata",$(ev.currentTarget))
         $('.all_btn').each(function (){
            $(this).removeClass('active_block')
            $(this).removeClass('active_none')
        });
        var $parent = $(ev.currentTarget).parent();
        $(ev.currentTarget).addClass('active_none')
        $parent.find('.actived').removeClass('active_none')
        $parent.find('.actived').addClass('active_block')
        $('.group_preview_container').empty();
        var product = $('#product').val();
        var line = $('#line').val();
        if (product) {
            var url = window.location.origin+'/mask/load/'+product+'/'+line+'/fold'
            var a = '/mask/load/'+product+'/'+line+'/fold'
            console.log("urlbvbvbvbv",url,a,product)
            $('.group_preview_container').empty();
            $('.group_preview_container').append('<iframe id="inlineFrameExample" title="Inline Frame Example" width="100%" height="100%" src='+url+'></iframe>')
        }
    },
    _3d_button: function (ev){
        var self = this;
        $('.all_btn').each(function (){
            $(this).removeClass('active_block')
             $(this).removeClass('active_none')
        });
        var $parent = $(ev.currentTarget).parent();
        $(ev.currentTarget).addClass('active_none')
        $parent.find('.actived').removeClass('active_none')
        $parent.find('.actived').addClass('active_block')
        var product = $('#product').val();
        var line = $('#line').val();
        if (product) {
            var url = window.location.origin+'/mask/load/'+product+'/'+line+'/3d'
            console.log("url",url)
            $('.group_preview_container').empty();
            $('.group_preview_container').append('<iframe id="inlineFrameExample" title="Inline Frame Example" width="100%" height="100%" src='+url+'></iframe>')
        }
    },
    _image_button: function (ev){
        var self = this;
        $('.all_btn').each(function (){
            $(this).removeClass('active_block')
             $(this).removeClass('active_none')
        });
        var $parent = $(ev.currentTarget).parent();
        $(ev.currentTarget).addClass('active_none')
        $parent.find('.actived').removeClass('active_none')
        $parent.find('.actived').addClass('active_block')
        $('.group_preview_container').empty();
        var order = $('#order').val();
        var url = window.location.origin+'/web/image?model=sale.order&id='+order+'&field=upload_your_image'
        $('.group_preview_container').append('<img src='+url+' alt="" style="width:50%">');

    },
    _product_packaging: function (ev) {
        var self = this;
        console.log("informations")
        var product = $('#product').val();
        var line = $('#line').val();
//        var order = $('#order').val();
        window.location.href = '/mask/packaging/'+product+'/'+line+'/'
    },
     _gui_back: function (ev) {
        var self = this;
         window.history.back();
//        window.history.go(-1)

    },

});

});