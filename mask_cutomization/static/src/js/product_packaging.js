odoo.define('mask_cutomization.product_packaging', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');
publicWidget.registry.product_packaging = publicWidget.Widget.extend({
    selector: '#product_packaging',
    events: {
        'input #upload_file_change': '_upload_file_change',
        'click #fetch_upload': '_fetch_upload',
        'click #preview-btn': '_preview_button',
        'click #design_btn': '_design_unload_btn',
        'click #gui_back': '_gui_back',
        'click #left_crumb': '_left_crumb',
        'click #center_crumb': '_center_crumb',
        'click #right_crumb': '_right_crumb',
    },

    /**
     * @constructor
     */
    init: function () {
     console.log("*****************product_packaging")
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        var package_image = $('#package_image').val();
        self._rpc({
                    route: "/search/fields",
                    params: {
                        id: $('#lines_id').val(),
                        model: "product.line",
                    },
                }).then(function (data) {
                    if (data['packaging_image']){
                        var img = "data:image/jpeg;base64,"+data['packaging_image']
                        $('#print').attr("style",'background-image:url('+img+')');
                        $('#print').removeClass('border_none');
                        $('#print').removeClass('border_block');
                        $('#print').addClass('border_none');
                    }
        });
//        if (package_image) {
//            var product_line = $('#sale_order_line').val();
//                    if (product_line) {
//                        var package_image = $('#package_image').val();
//                        if (package_image) {
//                            var url_image = window.location.origin+'/web/image?model=sale.order.line&id='+product_line+'&field=packaging_image'
//                            $('#print').attr("style",'background-image:url('+url_image+')');
//                        }
//
//            }
//        }else{
//            $('#print').attr("style",'background-image:url()');
//        }
        return this._super.apply(this, arguments);
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
    _save_file_backend: function (image, name) {
        var self = this;
        var sale_order_line = $('#sale_order_line').val()
        if (image.includes("data:image/png;base6")){
            var base64Img = image.replace("data:image/png;base64,", "");
        }
        if (image.includes("data:image/jpg;base6")){
            var base64Img = image.replace("data:image/jpg;base64,", "");
        }
        if (image.includes("data:image/jpeg;base6")){
            var base64Img = image.replace("data:image/jpeg;base64,", "");
        }

        self._rpc({
                    route: "/package/logo/write",
                    params: {
                        image: base64Img,
                        name: name,
                        line: sale_order_line
                    },
                }).then(function (data) {
                console.log("product_varient_id",data)
                if (data){
                    $("#file_uploaded_image").load(location.href + " #file_uploaded_image>*", "");
                    $("#image_size_check").load(location.href + " #image_size_check>*", "");
                    var product_line = $('#sale_order_line').val();
                    if (product_line) {
                        var package_image = $('#package_image').val();
//                        console.log("sadsdadsadsadsa",product_line,package_image)
//                        if (package_image) {
//                            var url_image = window.location.origin+'/web/image?model=sale.order.line&id='+product_line+'&field=packaging_image'
                            var url_image = "data:image/jpeg;base64,"+base64Img
                            $('#print').attr("style",'background-image:url('+url_image+')');
                            $('#print').removeClass('border_none');
                            $('#print').removeClass('border_block');
                            $('#print').addClass('border_none');
//                        }

                    }
                    self._un_block_ui();
                }
        });
    },
    _upload_file_change: function (ev) {
        var self = this;
        self._block_ui();
        if(document.querySelector("#upload_file_change").value == '') {
            console.log('No file selected');
            return;
        }
        var file = document.querySelector("#upload_file_change").files[0];
        var imageType = /image.*/;

        if (file.type.match(imageType)) {
            var reader = new FileReader();
            reader.onload = function(e) {
                var original_data = reader.result;
                var current_image = new Image();
                current_image.src = reader.result;
                self._save_file_backend(reader.result, file.name)
            };
            reader.onerror = function(e) {
                // error occurred
                console.log('Error : ' + e.type);
                self._un_block_ui();
            };
            reader.readAsDataURL(file);
        }else{
             self._un_block_ui();
             swal({
                      title: "Sorry image is not uploaded!",
                      icon: "error",
                      button: "Close",
                });
        }
    },
    _design_unload_btn: function (ev){
        var self = this;
        var line = $('#sale_order_line').val();
        $('#upload_file_change').val('')
        self._block_ui();
        if (line) {
            self._rpc({
                    route: "/package/image/delete",
                    params: {
                        line: line,
                    },
                }).then(function (data) {
                if (data){

                    $("#image_size_check").load(location.href + " #image_size_check>*", "");
                    $("#file_uploaded_image").load(location.href + " #file_uploaded_image>*", "");
                    $('#print').attr("style",'background-image:url()');
                    $('#print').removeClass('border_none');
                     $('#print').removeClass('border_block');
                    self._un_block_ui();
                }
                });
        }
        setTimeout(function () {
            $('body').unblock();
        }, 6000);
    },
    _fetch_upload: function (ev){
        var self = this;
        $('#upload_file_change').trigger('click');
    },
    _preview_button: function (ev){
        var self = this;
        $('.preview_div').each(function(){
            $(this).hide('swing');
        })
        $('.preview_none_div').show('swing');
        var product_line = $('#sale_order_line').val();
        if (product_line) {
            var package_image = $('#package_image').val();
            if (package_image) {
                var url_image = window.location.origin+'/web/image?model=sale.order.line&id='+product_line+'&field=packaging_image'
                $('#print').attr("style",'background-image:url('+url_image+')');
            }

        }
    },
    _gui_back: function (ev) {
        var self = this;
        window.history.go(-1)
    },
    _left_crumb: function (ev) {
        var self = this;
        var line = $('#lines_id').val();
        self._rpc({
                    route: "/package/history",
                    params: {
                        line: line,
                    },
                }).then(function (data) {
                    if (data) {
                        window.location.href= data
                    }
                });
    },
    _center_crumb: function (ev) {
        var line = $('#lines_id').val()
        var product = $('#product_info').val()
        window.location.href='/mask/packaging/'+product+'/'+line
    },
    _right_crumb: function (ev) {
        var line = $('#lines_id').val()
        var product = $('#product_info').val()
        window.location.href='/carton/packaging/'+product+'/'+line
    },
    });
});