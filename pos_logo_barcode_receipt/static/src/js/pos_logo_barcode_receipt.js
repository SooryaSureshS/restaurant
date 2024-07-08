odoo.define('pos_logo_barcode_receipt.pos_logo_barcode_receipt', function (require) {
"use strict";

    var core = require('web.core');
    var chrome = require('point_of_sale.chrome');
    var models = require('point_of_sale.models');
    var Model = require('web.DataModel');
    var screens = require('point_of_sale.screens');
    var session = require('web.session');
    var devices = require('point_of_sale.devices');
    var QWeb = core.qweb;
    var _t = core._t;
    
    models.PosModel.prototype.models.push({
        label: 'pictures',
        loaded: function(self){
            self.company_logo = new Image();
            var  logo_loaded = new $.Deferred();
            self.company_logo.onload = function(){
                var img = self.company_logo;
                var ratio = 1;
                var targetwidth = 300;
                var maxheight = 150;
                if( img.width !== targetwidth ){
                    ratio = targetwidth / img.width;
                }
                if( img.height * ratio > maxheight ){
                    ratio = maxheight / img.height;
                }
                var width  = Math.floor(img.width * ratio);
                var height = Math.floor(img.height * ratio);
                var c = document.createElement('canvas');
                    c.width  = width;
                    c.height = height;
                var ctx = c.getContext('2d');
                    ctx.drawImage(self.company_logo,0,0, width, height);

                self.company_logo_base64 = c.toDataURL();
                logo_loaded.resolve();
            };
            self.company_logo.onerror = function(){
                logo_loaded.reject();
            };
            self.company_logo.crossOrigin = "anonymous";
            if(self.config.pos_receipt_logo){
                alert('logo is available')
                self.company_logo.src = '/web/image?model=pos.config&id='+self.config.id + '&field=pos_receipt_logo';
            }else{
                self.company_logo.src = '/web/binary/company_logo' +'?dbname=' + session.db + '&_'+Math.random();
            }
            return logo_loaded;
        }
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes,options) {
            var self = this;
            this.set({
                'pos_reference' : false
            });
            _super_order.initialize.apply(this,arguments);
        },
        export_for_printing: function(){
            var json = _super_order.export_for_printing.apply(this,arguments);
            var barcode_val = this.get_name();
            var barcode_src = false;
            if(this.get_pos_reference()){
                barcode_val = this.get_pos_reference();
            }
            if (barcode_val.indexOf(_t("Order ")) != -1) {
                barcode_val = barcode_val.split(_t("Order "))[1];
                var barcodeTemplate = QWeb.render('templatebarcode',{
                      widget: self,barcode : barcode_val
                });
                $(barcodeTemplate).find('#barcode_div').barcode(barcode_val.toString(), "code128");
                if(_.isElement($(barcodeTemplate).find('#barcode_div').barcode(barcode_val.toString(), "code128")[0])){
                    if($(barcodeTemplate).find('#barcode_div').barcode(barcode_val.toString(), "code128")[0].firstChild != undefined 
                            && $(barcodeTemplate).find('#barcode_div').barcode(barcode_val.toString(), "code128")[0].firstChild.data != undefined){
                        barcode_src = $(barcodeTemplate).find('#barcode_div').barcode(barcode_val.toString(), "code128")[0].firstChild.data;
                    }
                }
            }
            json.barcode_src = barcode_src;
            return json;
        },
        set_pos_reference: function(pos_reference) {
            this.set('pos_reference', pos_reference)
        },
        get_pos_reference: function() {
            return this.get('pos_reference')
        },
    });

//    screens.ReceiptScreenWidget.include({
//        show: function(){
//            this._super();
//            var order = this.pos.get_order()
//            /*Set barcode in pos ticket.*/
//            var barcode_val = order.get_name();
//            if(order.get_pos_reference()){
//                barcode_val = order.get_pos_reference();
//            }
//            if (barcode_val) {
//               $("#barcode_div").addClass(barcode_val.toString());
//               $("#barcode_div").barcode(barcode_val.toString(), "code128");
//            }
//        },
//    });

    chrome.Chrome.include({
        build_chrome: function() {
            var self = this;
            this._super();
            this.$('.edit').click(function(){
                $('#change_logo').click();
            });
            $("#change_logo").change(function () {
                if (this.files && this.files[0]) {
                    var reader = new FileReader();
                    reader.onload = function (re) {
                        var base64result = re.target.result.split(',')[1];
                        var $img = $('.pos-logo').attr('src', re.target.result)
                        new Model("pos.config").get_func("write")(self.pos.config.id,{'pos_logo':base64result});
                    }
                    reader.readAsDataURL(this.files[0]);
                }
            });
        },
    });

});