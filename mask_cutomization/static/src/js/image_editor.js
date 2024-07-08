odoo.define('mask_cutomization.image_editor', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');
var rpc = require('web.rpc');
publicWidget.registry.image_editor_mask = publicWidget.Widget.extend({
    selector: '#image_editor_mask',
    events: {
//        'click .save_button': '_save_button',
        'click .cancel_button': '_cancel_button',
        'change #upload_file_change': '_upload_file_change',
        'click .plus': '_plus',
        'click .minus': '_minus',
    },

    /**
     * @constructor
     */
    init: function () {
        console.log("image editor")
        var self = this;
        var product_id = $('#product_id').val();
        var area = $('#area').val();
        console.log("loading editor @@@@@@@");
        self._block_ui();
        var url = window.location.origin+'/web/image?model=product.product&id='+product_id+'&field=kit_personalisation_image'
        console.log("$$$$$$$$$$$$$$$$$$$$$$ IMAGE",product_id,area)
        ajax.jsonRpc('/get/crop/image/details', 'call', {'product_id': product_id})
                .then(function (data) {
                console.log("wwwwwwwwwwwwwwwwwwwwwwww",data,area)
                 if (area == 'logo') {
                $('#scream').attr("src", window.location.origin+'/web/image?model=product.template&id='+product_id+'&field=preview_logo_area');
                $('#scream').attr("style", "width:"+data['logo_crop_width']+"px;height:"+data['logo_crop_height']+"px;left: 10px;top: 7px;");
                $('#image_width').text(Math.round(parseFloat(data['logo_crop_width']) * 0.0264583333 * 100)/100 );
                $('#image_height').text(Math.round(parseFloat(data['logo_crop_height']) * 0.0264583333 * 100)/100 );
            }
            if (area == 'full') {
                $('#scream').attr("src", window.location.origin+'/web/image?model=product.template&id='+product_id+'&field=preview_full_area');
                $('#scream').attr("style", "width:"+data['full_crop_width']+"px;height:"+data['full_crop_height']+"px;");
                $('#image_width').text(Math.round(parseFloat(data['full_crop_width']) * 0.0264583333 * 100)/100);
                $('#image_height').text(Math.round(parseFloat(data['full_crop_height']) * 0.0264583333 * 100)/100);
            }
            self._change_image_browse();
                });
//        self._rpc({
//                            route: "/get/crop/image/details",
//                            params: {
//                                product_id: product_id,
//
//                            },
//                        }).then(function (data) {
//                        console.log("wwwwwwwwwwwwwwwwwwwwwwww",data,area)
//                        });

//        rpc.query({
//            model: 'product.template',
//            method: 'get_editor_image',
//            args: [product_id],
//        }, {
//            shadow: true,
//        }).then(function (data) {
//        console.log("********************************* image",data)
//            if (area == 'logo') {
//                $('#scream').attr("src", window.location.origin+'/web/image?model=product.template&id='+product_id+'&field=preview_logo_area');
//                $('#scream').attr("style", "width:"+data['logo_crop_width']+"px;height:"+data['logo_crop_height']+"px;left: 10px;top: 7px;");
//                $('#image_width').text(Math.round(parseFloat(data['logo_crop_width']) * 0.0264583333 * 100)/100 );
//                $('#image_height').text(Math.round(parseFloat(data['logo_crop_height']) * 0.0264583333 * 100)/100 );
//            }
//            if (area == 'full') {
//                $('#scream').attr("src", window.location.origin+'/web/image?model=product.template&id='+product_id+'&field=preview_full_area');
//                $('#scream').attr("style", "width:"+data['full_crop_width']+"px;height:"+data['full_crop_height']+"px;");
//                $('#image_width').text(Math.round(parseFloat(data['full_crop_width']) * 0.0264583333 * 100)/100);
//                $('#image_height').text(Math.round(parseFloat(data['full_crop_height']) * 0.0264583333 * 100)/100);
//            }
//            self._change_image_browse();
//        });
        console.log("loading editor ##########################");
        console.log("loading editor ##########################", window.location.origin+'/web/image?model=product.template&id='+product_id+'&field=preview_logo_area');
        this._super.apply(this, arguments);
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
    _upload_file_change: function (ev) {
        var self = this;

    },
    _plus: function (ev) {
           var self = this;
           var scaleRange = $('#scaleRange').val();
           $('#scaleRange').val(parseFloat(scaleRange) + parseFloat(.1) );
           var scaleRange = $('#scaleRange').val();
           self.$canvasTable.changeScale(scaleRange);

    },
    _minus: function (ev) {
           var self = this;
           var scaleRange = $('#scaleRange').val();
           $('#scaleRange').val(parseFloat(scaleRange) - parseFloat(.1) );
           var scaleRange = $('#scaleRange').val();
           self.$canvasTable.changeScale(scaleRange);

    },
    _change_image_browse: function () {
        var self = this;
        var c = document.getElementById("canvas");
        var ctx = c.getContext("2d");
        var img = document.getElementById("scream");
        ctx.drawImage(img,20,10);
        var sale_order_id = $('#sale_order_id').val();
        var session_product_id = $('#session_product_id').val();
        var url = window.location.origin+'/web/image?model=product.line&id='+session_product_id+'&field=buffer_image'
        var url = window.location.origin+'/web/image?model=product.line&id='+session_product_id+'&field=buffer_image'
        console.log("urldd",url)
        self.$canvasTable = $("#canvas").canvasTable({
                width: 390,
                height: 290,
                gap: 10,
                strokeDash: 5,
                strokeWidth: 2,
                showAlignmentLines: true,
                // css grid template areas
                templateAreas: ["photo1"],
                //templateAreas: ["photo1 photo1 photo2 photo2", "photo3 photo3 photo4 photo5", "photo6 photo6 photo6 photo6"],
                images: [
                  {
                    area: "photo1",
                    source:
                      url
                  },
                ],
                onSelected(selectedArea) {
                  $("#scaleRange").attr("disabled", false);
                  $("#rotateRange").attr("disabled", false);
                  $("#scaleRange").val(selectedArea.image.scale);
                  $("#rotateRange").val(selectedArea.image.rotate);
                }
          });
          $("#scaleRange").on("input", (event) => {
            self.$canvasTable.changeScale(event.target.value);
            console.log("plus values",event.target.value)
          });

          $("#rotateRange").on("input", (event) => {
            self.$canvasTable.changeRotate(event.target.value);
          });

          $(".save_button").click(() => {
            self.$canvasTable.setDefault();
            const canvasSource = self.$canvasTable.createPhoto();
            const canvasImage = new Image();
            canvasImage.src = canvasSource;
//            console.log("image ",canvasSource)
            var $window = window.parent.$(".sweet-modal-buttons").find('.greenB')

            var base64Img = canvasSource. replace("data:image/png;base64,", "");
                    self._rpc({
                            route: "/image/save/editor",
                            params: {
                                image: base64Img,
                                name: "uploaded",
                            },
                        }).then(function (data) {
                            if (data){
                                $window.click();
                            }else{
                                 $.sweetModal({
                                        title: 'Sorry Error',
                                        content: 'sorry sale order not found'
                                    });
                            }

                    });
          });
          $('#image_editor_mask').show();
          self._un_block_ui();
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },

    _save_button: function (ev){
        var self = this;
        var img = $(".cropme img").attr('src');
        var name = $(".cropme img").attr('name');
        var $window = window.parent.$(".sweet-modal-buttons").find('.greenB')
        try {
            var base64Img = img. replace("data:image/png;base64,", "");
            self._rpc({
                    route: "/image/save/editor",
                    params: {
                        image: base64Img,
                        name: name,
                    },
                }).then(function (data) {
                    if (data){
                        console.log("data saved",$window)
//                        $('#amount_total').text(data)
//                        $('#amount_total').val(data)
                        $window.click();
                    }else{
                         $.sweetModal({
                                title: 'Sorry Error',
                                content: 'sorry sale order not found'
                            });
                    }

            });

        }catch(e){
				$.miniNoty('Sorry image is not updated!','error')
		}

//
//            var imageType = /image.*/;


//            if (file.type.match(imageType)) {
//        $('body').block({
//                message: '<lottie-player src="https://assets6.lottiefiles.com/packages/lf20_zyq1qkhh.json"  background="transparent"  speed="1"  style="width: 300px; height: 300px;"  loop autoplay></lottie-player>',
//                overlayCSS: {backgroundColor: "#000", opacity: 0.3, zIndex: 1050, color: "#FFFFFF"},
//        });
    },

      _cancel_button: function (ev){
        var self = this;
            var $window = window.parent.$(".sweet-modal-buttons").find('.redB')
            $window.click();
        },
     _gui_back: function (ev) {
        var self = this;
        window.history.go(-1)
    },
    });
});