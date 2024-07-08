odoo.define('mask_cutomization.mask_designing', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');
var rpc = require('web.rpc');

var QWeb = core.qweb;
publicWidget.registry.mask_designing_container = publicWidget.Widget.extend({
    selector: '#mask_designing_container',
    events: {
//        'change #upload_file_change': '_upload_file_change',
        'click .pellete_color': '_change_pellete_color',
        'click .pellete_color_mask': '_change_pellete_color_mask',
        'click .quantity_minus': '_quantity_minus',
        'click .quantity_plus': '_quantity_plus',
        'click .nose_pad_yes_button': '_nose_pad_yes_button',
        'click .nose_pad_no_button': '_nose_pad_no_button',
        'click #fetch_upload': '_fetch_upload',
        'click #gui_back': '_gui_back',
        'click #submit_form': '_submit_form',
        'click #new_upload': '_new_upload',
        'click .fold_button': '_fold_button',
        'click .3d_button': '_3d_button',
        'click .image_button': '_image_button',
        'click .nose_pad_button': '_nose_pad_button',
        'click .fragrance_button': '_fragrance_button',
                'click #left_crumb': '_left_crumb',
        'click #center_crumb': '_center_crumb',
        'click #right_crumb': '_right_crumb',
    },

    /**
     * @constructor
     */
    init: function () {
        console.log("*****************mask_designing_container ggfg")
        var self = this;
        self.selected_view = false
        this._super.apply(this, arguments);
        $('#upload_file_change').change(function(){
            const file = this.files[0];
            console.log("infofofo",file);
            if (file) {
                var imageType = /image.*/;

            if (file.type.match(imageType)) {
                if (file){
                  let reader = new FileReader();
                  reader.onload = function(event){
                    console.log(event.target.result);
                         var base64Img = event.target.result. replace("data:image/png;base64,", "");
                         var base64Img = base64Img. replace("data:image/jpeg;base64,", "");
                    self._rpc({
                            route: "/image/save/editor",
                            params: {
                                image: base64Img,
                                name: file.name,
                            },
                        }).then(function (data) {
                            if (data){
                                console.log("datatatat",data);
                                var product = $('#product_ids').val();
                                if (product) {
                                    var url = window.location.origin+'/image/editor/'+product
//                                        return $.when(this._loadTemplates()).then(function () {
                                             $('.cropme').simpleCropper()
                                             $.sweetModal.confirm('Image Editor',
                                                '<iframe id="inlineFrameExample" title="Inline Frame Example" width="100%" height = 500px;" src='+url+' style="border:none;"></iframe>', function() {
                                                location.reload(true)
                                                }, function() {
//                                                    $.sweetModal('You declined. That\'s okay!');
                                                    console.log("canceled")
                                                });
//                                        });
                                }
                            }
                    });



                  }
                  reader.readAsDataURL(file);
                }
            }else{
                 swal({
                      title: "Sorry Unsupported file",
                      icon: "error",
                      button: "Close",
                });
            }
            }else{
                swal({
                      title: "Sorry Unsupported file",
                      icon: "error",
                      button: "Close",
                });
            }


        });
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        self._block_ui();
        var buffer_product = $('#buffer_product').val();
        if (buffer_product) {
            self._render_session_values();
        }else{
            self._render_default_attribute();
        }
        $('.3d_button').first().trigger('click');
        return this._super.apply(this, arguments);
    },
    _render_session_values: function (ev) {
        var self = this;
        var buffer_product = $('#buffer_product').val();
        self._rpc({
                route: "/product/ptav/get",
                params: {
                    pid: buffer_product,
                },
            }).then(function (data) {
                if (data){
                    if (data['status'] == 1){
                            if (data['attributes']) {
                                $('#default_mask').val(data['attributes']['Cloth color']).trigger('change');
                                $('#default_color').val(data['attributes']['Earloop color']).trigger('change');
                                $('#default_nose').val(data['attributes']['Nose sponge']).trigger('change');
                                $('#default_fragrance').val(data['attributes']['Fragrance bead']).trigger('change');
                                self._render_default_attribute();
                            }
                    }else{
                        self._render_default_attribute();
                    }
                }
            });
    },
    _render_default_attribute: function (ev) {
        var self = this;
        var mask = $('#default_mask').val();
        var color = $('#default_color').val();
        var nose = $('#default_nose').val();
        var fragrance = $('#default_fragrance').val();
        if (mask) {
           var $pellete_color_mask = $('#color_mask').find('.pellete_color_mask')
           $pellete_color_mask.each(function (){
//               console.log("default cloth color",$(this).attr('data-value_id'));
               if ($(this).attr('data-value_id') == mask){
                    $(this).trigger("click");
               }
           });
        }
        if (color) {
            var $pellete_color_rope = $('#rope_color').find('.pellete_color')
           $pellete_color_rope.each(function (){
//               console.log("default rop color",$(this).attr('data-value_id'));
               if ($(this).attr('data-value_id') == color){
                    $(this).trigger("click");
               }
           });
        }

        if (nose) {
            var $nose_attribute = $('#nose_attribute').find('.nose_pad_button')
             $nose_attribute.each(function (){
//               console.log("default nose ",$(this).attr('data-value_id'));
               if ($(this).attr('data-value_id') == nose){
                    $(this).trigger("click");
               }
           });
        }
        if (fragrance) {
            var $nose_attribute = $('#fragrance_attribute').find('.fragrance_button')
             $nose_attribute.each(function (){
//               console.log("default fragrance ",$(this).attr('data-value_id'));
               if ($(this).attr('data-value_id') == fragrance){
                    $(this).trigger("click");
               }
           });
        }
    },
    _block_ui: function(){
         $('body').block({
                message: '<lottie-player src="https://assets9.lottiefiles.com/packages/lf20_p8bfn5to.json"  background="transparent"  speed="1"  style="height: 300px;"  loop autoplay></lottie-player>',
                overlayCSS: {backgroundColor: "#000", opacity: 0.3, zIndex: 1050, color: "#FFFFFF"},
        });
    },
    _un_block_ui: function (){
        setTimeout(function () {
            $('body').unblock();
        }, 1000);
    },
    _fold_button: function (ev){
        var self = this;
        var pass = true;
        if ($('#area').val() == 'full'){
            if ($('#upload_image_view').attr('date_image')){
                 pass = true;
            }else{
                pass = false;
                swal({
                      title: "Sorry image is not uploaded!",
                      icon: "error",
                      button: "Close",
                });
            }
        }
        if ($('#area').val() == 'logo'){
            if ($('#upload_image_view').attr('date_image')){
                 pass = true;
            }else{
                pass = false;
                swal({
                      title: "Sorry image is not uploaded!",
                      icon: "error",
                      button: "Close",
                });
            }
        }
        if ($('#area').val() == 'blank'){
            pass = true;
        }
        if (pass) {
            $('.3d_button').each(function(){
                if ($(this).hasClass('actived')){
                    $(this).removeClass('active_block');
                    $(this).removeClass('active_none');
                    $(this).addClass('active_none');
                }
                if ($(this).hasClass('blocked')){
                    $(this).removeClass('active_none');
                    $(this).removeClass('active_block');
                    $(this).addClass('active_block');
                }
            });
            var $parent = $(ev.currentTarget).parent();
            if ($parent.find('.actived').hasClass('active_block')){
                $parent.find('.blocked').removeClass('active_block');
                $parent.find('.blocked').removeClass('active_none');
                $parent.find('.actived').removeClass('active_block');
                $parent.find('.actived').removeClass('active_none');
                $parent.find('.actived').addClass('active_none');
                $parent.find('.blocked').addClass('active_block');
                self.selected_view = '';
            }else{
                $parent.find('.blocked').removeClass('active_block');
                $parent.find('.blocked').removeClass('active_none');
                $parent.find('.actived').removeClass('active_none');
                $parent.find('.actived').removeClass('active_none');

                $parent.find('.actived').addClass('active_block');
                $parent.find('.blocked').addClass('active_none');
                self.selected_view = 'fold';
            }
            if (self.selected_view == 'fold'){
                $('.3d_preview').show();
                $('.image_preview').hide();
                $('.group_preview_container').empty();
                var product = $('#product_varients').val();
                var sale_order = $('#sale_order').val();
                console.log("product info",product)
                if (product) {
                    var url = window.location.origin+'/mask/design/load/'+product+'/'+sale_order+'/fold'
                    var a = '/mask/design/load/'+product+'/'+sale_order+'/fold'
                    console.log("urlbvbvbvbv",url,a,product)
                    $('.group_preview_container').empty();
                    $('.group_preview_container').append('<iframe id="inlineFrameExample" title="Inline Frame Example" width="100%" height="100%" src='+url+'></iframe>')
                }
            }else{
                 $('.3d_preview').hide();
                $('.image_preview').show();

            }
        }

        console.log("self@@@@@@@@@@@@@@22222222",self)
    },
    _3d_button: function (ev){
        var self = this;
        var pass = true;
        if ($('#area').val() == 'full'){
            if ($('#upload_image_view').attr('date_image')){
                 pass = true;
            }else{
                pass = false;
                swal({
                      title: "Sorry image is not uploaded!",
                      icon: "error",
                      button: "Close",
                });
            }
        }
        if ($('#area').val() == 'logo'){
            if ($('#upload_image_view').attr('date_image')){
                 pass = true;
            }else{
                pass = false;
                swal({
                      title: "Sorry image is not uploaded!",
                      icon: "error",
                      button: "Close",
                });
            }
        }
        if ($('#area').val() == 'blank'){
            pass = true;
        }
        if (pass) {
            var $parent = $(ev.currentTarget).parent();
            $('.fold_button').each(function(){
                    if ($(this).hasClass('actived')){
                        $(this).removeClass('active_block');
                        $(this).removeClass('active_none');
                        $(this).addClass('active_none');
                    }
                    if ($(this).hasClass('blocked')){
                        $(this).removeClass('active_none');
                        $(this).removeClass('active_block');
                        $(this).addClass('active_block');
                    }
            });
            if ($parent.find('.actived').hasClass('active_block')){
                $parent.find('.blocked').removeClass('active_block');
                $parent.find('.blocked').removeClass('active_none');
                $parent.find('.actived').removeClass('active_block');
                $parent.find('.actived').removeClass('active_none');
                $parent.find('.actived').addClass('active_none');
                $parent.find('.blocked').addClass('active_block');
                self.selected_view = '';
            }else{
                $parent.find('.blocked').removeClass('active_block');
                $parent.find('.blocked').removeClass('active_none');
                $parent.find('.actived').removeClass('active_none');
                $parent.find('.actived').removeClass('active_none');

                $parent.find('.actived').addClass('active_block');
                $parent.find('.blocked').addClass('active_none');
                self.selected_view = '3d';
            }
            if (self.selected_view == '3d'){
                $('.3d_preview').show();
                $('.image_preview').hide();
                 $('.group_preview_container').empty();
                var product = $('#product_varients').val();
                var sale_order = $('#sale_order').val();
                console.log("product info",product)
                if (product) {
                    var url = window.location.origin+'/mask/design/load/'+product+'/'+sale_order+'/3d'
                    var a = '/mask/design/load/'+product+'/'+sale_order+'/fold'
                    console.log("urlbvbvbvbv",url,a,product)
                    $('.group_preview_container').empty();
                    $('.group_preview_container').append('<iframe id="inlineFrameExample" title="Inline Frame Example" width="100%" height="100%" src='+url+'></iframe>')
                }
            }else{
                 $('.3d_preview').hide();
                $('.image_preview').show();
            }
        }
    },
    _upload_file_change: function (ev) {
        var self = this;
    },
    _nose_pad_button: function (ev) {
        var self = this;
        var $nose_pad_button = $(ev.currentTarget)
        $('.nose_pad_button').each(function(){
            $(this).removeClass('nose_pad_button_active')
        });
        $(ev.currentTarget).addClass('nose_pad_button_active');
        $('.is_nosepad').val('False')
        if($('.nose_pad_button_active').attr('data-value') == 'Y'){
            $('.is_nosepad').val('True')
            var price_extra = $('.nose_pad_price_extra').val()
            $('.nose_pad_price').val(price_extra)
        }
        else{
            $('.is_nosepad').val('False')
            $('.nose_pad_price').val(0.0)
        }
        $('#selected_nose').val($(ev.currentTarget).attr('data-value_id'));
        self._product_search();
    },
    _fragrance_button: function (ev) {
        var self = this;
        var $nose_pad_button = $(ev.currentTarget)
        $('.fragrance_button').each(function(){
            $(this).removeClass('fragrance_button_active')
        });
        $(ev.currentTarget).addClass('fragrance_button_active')
        $('#selected_fragrance').val($(ev.currentTarget).attr('data-value_id'));
        self._product_search();
    },

    _change_pellete_color: function (ev){
        var self = this;
        var $color_pellete = $(ev.currentTarget)
        $('.pellete_color').each(function(){
            $(this).removeClass('pellete_active')
        });
        $(ev.currentTarget).addClass('pellete_active');
        $('#selected_rope_color').val($(ev.currentTarget).attr('data-value_id'));
        self._product_search();
    },
    _change_pellete_color_mask: function (ev){
        var self = this;
        var $color_pellete = $(ev.currentTarget)
        $('.pellete_color_mask').each(function(){
            $(this).removeClass('pellete_active')
        });
        $(ev.currentTarget).addClass('pellete_active');
        $('#selected_cloth_color').val($(ev.currentTarget).attr('data-value_id'));
        self._product_search();
    },
    _product_search: function (ev){
        var self = this;
        var selected_size = $('#selected_size').val();
        var selected_print_type = $('#selected_print_type').val();
        var selected_cloth_color = $('#selected_cloth_color').val();
        var selected_rope_color = $('#selected_rope_color').val();
        var selected_nose = $('#selected_nose').val();
        var selected_fragrance = $('#selected_fragrance').val();
        var product_template = $('#product_ids').val();
        console.log("changed", selected_size,selected_print_type,selected_cloth_color,selected_rope_color,selected_nose,selected_fragrance)
        self._rpc({
                    route: "/product/variant/search",
                    params: {
                        "product_tmpl_id": product_template,
                        "attributes": {
                            print_type: selected_print_type,
                            nose_sponge: selected_nose,
                            cloth_color: selected_cloth_color,
                            cloth_color: selected_cloth_color,
                            earloop_color: selected_rope_color,
                            mask_size: selected_size,
//                            fragrance: selected_fragrance,
                        }
                    },
                }).then(function (data) {
                if (data){
                    console.log("result",data['product'])
//                    $('#product_varients').text(data['product']).trigger('change');
                    $('#product_varients').val(data['product']).trigger('change');
                    self._trigger_change_amount();
                }
                });
//        }
    },
    _quantity_minus: function (ev){
        var self = this;
        var qty = $('#qty_order').val();
        var minQty = $('#prod_min_qty').val();
        var minQtyStep = $('#prod_qty_step').val();
        if (qty > minQty){
            var a = parseFloat(qty) - parseFloat(minQtyStep);
            $('#qty_order').val(a)
            $('#product_qty').text(a).trigger('change');
            $('#product_qty').val(a).trigger('change');
            self._trigger_change_amount();

        }
        console.log("minus",qty)
    },
    _quantity_plus: function (ev){
        var self = this;
        var qty = $('#qty_order').val();
        var minQty = $('#prod_min_qty').val();
        var minQtyStep = $('#prod_qty_step').val();
        var a = parseFloat(qty) + parseFloat(minQtyStep);
        $('#qty_order').val(a)
        $('#product_qty').text(a).trigger('change');
        $('#product_qty').val(a).trigger('change');
        self._trigger_change_amount();
    },
    _nose_pad_yes_button: function (ev){
        var self = this;
        var $color_pellete = $(ev.currentTarget)
        $('.nose_pad_yes_button').removeClass('nose_pad_active')
        $('.nose_pad_no_button').removeClass('nose_pad_active')
        $(ev.currentTarget).addClass('nose_pad_active')
        var service = $('#website_service_product_price').val();
        $('#product_charges').text(service).trigger('change');
        $('#product_charges').val(service).trigger('change');
        self._trigger_change_amount();
    },
    _nose_pad_no_button: function (ev){
        var self = this;
        var $color_pellete = $(ev.currentTarget)
        $('.nose_pad_yes_button').removeClass('nose_pad_active')
        $('.nose_pad_no_button').removeClass('nose_pad_active')
        $(ev.currentTarget).addClass('nose_pad_active')
        var service = false
        $('#product_charges').text(service).trigger('change');
        $('#product_charges').val(service).trigger('change');
        self._trigger_change_amount();
    },
    _trigger_view: function (ev) {
        var self = this;
        if (self.selected_view == 'fold')  {
              $('.group_preview_container').empty();
            var product = $('#product_varients').val();
            var sale_order = $('#sale_order').val();
            console.log("product info",product)
            if (product) {
                var url = window.location.origin+'/mask/design/load/'+product+'/'+sale_order+'/fold'
                var a = '/mask/design/load/'+product+'/'+sale_order+'/fold'
                $('.group_preview_container').empty();
                $('.group_preview_container').append('<iframe id="inlineFrameExample" title="Inline Frame Example" width="100%" height="100%" src='+url+'></iframe>')
            }
        }
        if (self.selected_view == '3d'){
            $('.group_preview_container').empty();
            var product = $('#product_varients').val();
            var sale_order = $('#sale_order').val();
            if (product) {
                var url = window.location.origin+'/mask/design/load/'+product+'/'+sale_order+'/3d'
                var a = '/mask/design/load/'+product+'/'+sale_order+'/fold'
                $('.group_preview_container').empty();
                $('.group_preview_container').append('<iframe id="inlineFrameExample" title="Inline Frame Example" width="100%" height="100%" src='+url+'></iframe>')
            }
        }
        self._un_block_ui();
    },
    _trigger_change_amount: function (ev) {
        var self = this;
        self._block_ui();
        self._trigger_view();
        self._rpc({
                    route: "/amount/fetch",
                    params: {
                        product_variants: $('#product_varients').val(),
                        nose_pad: $('#product_charges').val(),
                        qty: $('#qty_order').val(),
                    },
                }).then(function (data) {
                    console.log("amount",data)
                    self._un_block_ui();
                    if (data){
                        $('#amount_total').text(data)
                        $('#amount_total').val(data)
                    }

                });
        var qty = $('#qty_order').val();
        $('#product_qty').val(qty).trigger('change');
    },
    _loadTemplates: function(){
        return ajax.loadXML('/mask_cutomization/static/src/xml/template.xml', QWeb);
    },
    _fetch_upload: function (ev){
        var self = this;
        $('#upload_file_change').trigger('click');
    },
         _gui_back: function (ev) {
        var self = this;
        window.history.go(-1)
    },
    _submit_form: function (ev) {
        var self = this;
        $(ev.currentTarget).closest('form')
        var image = $('#session_product_id').val();
        console.log("form",image)
        var area = $('#area').val();
        if (area == 'blank'){
            $(ev.currentTarget).closest('form').submit();
        }else{
            if (image) {
                $(ev.currentTarget).closest('form').submit();
            }else{
                $.sweetModal({
                                    title: 'Sorry Error',
                                    content: 'sorry image not found'
                                });
            }
        }

    },
    _new_upload: function (ev) {
        var product = $('#product_ids').val();
        if (product) {
            var url = window.location.origin+'/image/editor/'+product
                return $.when(this._loadTemplates()).then(function () {
                     $('.cropme').simpleCropper()
                     $.sweetModal.confirm('Please click the camera icon',
                        '<iframe id="inlineFrameExample" title="Inline Frame Example" width="100%" height = 500px;" src='+url+' style="border:none;"></iframe>', function() {
                        location.reload(true)
                        }, function() {
                            $.sweetModal('You declined. That\'s okay!');
                        });
                });
        }
    },
    _left_crumb: function (ev) {
        var self = this;
        window.location.reload();
//        var line = $('#lines_id').val();
//        self._rpc({
//                    route: "/package/history",
//                    params: {
//                        line: line,
//                    },
//                }).then(function (data) {
//                    if (data) {
//                        window.location.href= data
//                    }
//                });
    },
    _center_crumb: function (ev) {
       console.log("session id",$('#session_product_id').val())
        var self = this;
        $(ev.currentTarget).closest('form')
        var image = $('#session_product_id').val();
        console.log("form",image)
        var area = $('#area').val();
        if (area == 'blank'){
            $('#form_action_product_details').submit();
        }else{
            if (image) {
                $('#form_action_product_details').submit();
            }else{
                $.sweetModal({
                                    title: 'Sorry Error',
                                    content: 'sorry image not found'
                                });
            }
        }
//        var line = $('#lines_id').val()
//        var product = $('#product_info').val()
//        window.location.href='/mask/packaging/'+product+'/'+line
    },
    _right_crumb: function (ev) {
        var line = $('#session_product_id').val()
        var product = $('#product_varients').val()
        window.location.href='/carton/packaging/'+product+'/'+line
    },

});
$(document).ready(function() {
    console.log("loading *****************************************88888888888")
});


});