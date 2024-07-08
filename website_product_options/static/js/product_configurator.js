odoo.define('website_product_options.product_configurator', function (require) {
    "use strict";

var ajax = require('web.ajax');
var Dialog = require('web.Dialog');
const OwlDialog = require('web.OwlDialog');
var ServicesMixin = require('web.ServicesMixin');
var VariantMixin = require('sale.VariantMixin');
var sale_product_configurator = require('sale_product_configurator.OptionalProductsModal');


var OptionalProductsModal= sale_product_configurator.include({
    events:  _.extend({}, Dialog.prototype.events, VariantMixin.events, {
        'click a.js_add, a.js_remove': '_onAddOrRemoveOption',
        'click button.js_add_cart_json': 'onClickAddCartJSON',
        'change .in_cart input.js_quantity': '_onChangeQuantity',
        'change .js_raw_price': '_computePriceTotal',
        'click .check_product': '_productclick',
        'change .check_product': '_check_product'
    }),

    init: function () {
        var self = this;
        self.product_list = {}
        this._super.apply(this, arguments);
    },

//    _productclick: function (ev) {
//     var self = this;
//     var product='';
//     $(".check_product").change(function(){
//        product = $(this).attr("id");
//        var child_id = $(this).closest("tr").attr("id");
//        ajax.jsonRpc('/get/options/group', 'call', {"ready": 1,"child_id":child_id}).then(function(res) {
//            if (res){
//            var maximum_count = res.max;
////                if (maximum_count>0){
//                $('.'+child_id).each(function() {
//                var length = $("."+child_id+" input[type=checkbox]:checked").length;
//                if(length>maximum_count)
////                {
//                     $('#'+product).prop('checked',false);
//                    alert("Hi,You can select maximum "+maximum_count.toString()+" Options For This Category!!!");
//                }
////                })
//                }
//            }
//
//        });
//    });
//
//    },
     _productclick: function (ev) {
     var self = this;
     var product='';
     $(".check_product").change(function(){
        product = $(this).attr("id");
        var child_id = $(this).closest("tr").attr("id");
        ajax.jsonRpc('/get/options/group', 'call', {"ready": 1,"child_id":child_id}).then(function(res) {
            if (res){
            var maximum_count = res.max;
                if (maximum_count>0){
                $('.'+child_id).each(function() {
                var length = $("."+child_id+" input[type=checkbox]:checked").length;
                if(length>maximum_count)
                {
                     $('#'+product).prop('checked',false);
                    alert("Hi,You can select maximum "+maximum_count.toString()+" Options For This Category!!!");
                }
                })
                }
            }

        });
    });

    },
    getSelectedProducts: function () {
        var self = this;
        self.rootProduct.toppings = self.product_merge;
        var products = [this.rootProduct];
        var products_alternative = [];
        this.$modal.find('.js_product:not(.main_product)').each(function () {
            var $item = $(this);
            var id = '#'+$item.find('input.product_id').val();
            var alternative_product = $item.find('input.alternative_product').val();
            console.log("Ggggggggggggggggggg",alternative_product)
            if ($(id).prop('checked') == true && alternative_product==false){
            var quantity = parseInt($item.find('input[name="add_qty"]').val(), 10);
            var parentUniqueId = this.dataset.parentUniqueId;
            var uniqueId = this.dataset.uniqueId;
            var productCustomVariantValues = self.getCustomVariantValues($(this));
            var noVariantAttributeValues = self.getNoVariantAttributeValues($(this));
            products.push({
                'product_id': parseInt($item.find('input.product_id').val(), 10),
                'product_template_id': parseInt($item.find('input.product_template_id').val(), 10),
                'quantity': quantity,
                'parent_unique_id': parentUniqueId,
                'unique_id': uniqueId,
                'product_custom_attribute_values': productCustomVariantValues,
                'no_variant_attribute_values': noVariantAttributeValues
            });
            }
            if ($(id).prop('checked') == true && alternative_product=='True'){
            var quantity = parseInt($item.find('input[name="add_qty"]').val(), 10);
            var parentUniqueId = this.dataset.parentUniqueId;
            var uniqueId = this.dataset.uniqueId;
            var productCustomVariantValues = self.getCustomVariantValues($(this));
            var noVariantAttributeValues = self.getNoVariantAttributeValues($(this));
            products_alternative.push({
                'product_id': parseInt($item.find('input.product_id').val(), 10),
                'product_template_id': parseInt($item.find('input.product_template_id').val(), 10),
                'quantity': quantity,
                'parent_unique_id': parentUniqueId,
                'unique_id': uniqueId,
                'product_custom_attribute_values': productCustomVariantValues,
                'no_variant_attribute_values': noVariantAttributeValues
            });
            }

        });
        return [products,products_alternative];
    },

    _onConfirmButtonClick: function () {
        var self = this;
          var ids= {};
          this.$modal.find('.product_options_group:not(.main_product)').each(function () {
          var val=$("."+$(this).attr("id")+" input[type=checkbox]:checked").length;
          ids[$(this).attr("id")]=val;
        });
        ajax.jsonRpc('/get/options/all/group', 'call', {"ready": 1,"ids":[ids]}).then(function(res) {
        if (res){
        var check = false;
         var text = '';
        for(var i = 0; i < res.length; i++){
            var value= res[i];
            if (value.count>0){
            if (value.selected<value.count){
            check = true
            if (text==''){
            text= value.name+'('+value.count.toString()+')'
            }
            else{
            text= text+','+value.name+'('+value.count.toString()+')'

            }

            }
            }
        }
        if (text.length>1){
        alert("Hi,At least you should choose the options for "+ text);
        }
        if (check==false){

        self.trigger('confirm');
        self.close();
        }
        }
        else{
        self.trigger('confirm');
        self.close();
        }



        });

    },

    /**
     * @private
     */
   _onCancelButtonClick: function () {

        var self = this;
          var ids= {};
          this.$modal.find('.product_options_group:not(.main_product)').each(function () {
          var val=$("."+$(this).attr("id")+" input[type=checkbox]:checked").length;
          ids[$(this).attr("id")]=val;
        });
        ajax.jsonRpc('/get/options/all/group', 'call', {"ready": 1,"ids":[ids]}).then(function(res) {
        if (res){
        var check = false;
        var text = '';
        for(var i = 0; i < res.length; i++){
            var value= res[i];
            if (value.count>0){
            if (value.selected<value.count){
            check = true
            if (text==''){
            text= value.name+'('+value.count.toString()+')'
            }
            else{
            text= text+','+value.name+'('+value.count.toString()+')'

            }

            }
            }
        }
        if (text.length>1){
        alert("Hi,At least you should choose the options for "+ text);
        }
        if (check==false){

        self.trigger('back');
        self.close();
        }
        }
        else{
         self.trigger('back');
        self.close();
        }

        });
    },


    start: function () {
        var def = this._super.apply(this, arguments);
        var self = this;
        self.product_merge = {}

        $(".check_product").change(function(){
        console.log("wwwwwwwwwwwqqqqqqqqqqqqqqqqqqqq")
            product = $(this).attr("id");
               this.$modal.find('.js_product:not(.main_product)').each(function () {
                    var $item = $(this);
                    var id = '#'+$item.find('input.product_id').val();
                    if ($(id).prop('checked') == true){
                    var quantity = parseInt($item.find('input[name="add_qty"]').val(), 10);
                    console.log("wwwwwwwwwww",id)

                    }
                });
//            self.product_merge[self.rootProduct.quantity] =
        });
        console.log("startsss",self.rootProduct.product_id)
    },
    _check_product: function (ev) {
        var self = this;
        self.update_toppings();
    },
    update_toppings: function(){
        var self = this;
        var toppings_list = []
//      var toppings = $(ev.currentTarget).attr('id');
        this.$modal.find('.js_product:not(.main_product)').each(function () {
                    var $item = $(this);
                    var id = '#'+$item.find('input.product_id').val();
                    if ($(id).prop('checked') == true){
                    var quantity = parseInt($item.find('input[name="add_qty"]').val(), 10);
                        toppings_list.push($item.find('input.product_id').val());
                    }
        });
        self.product_merge[self.rootProduct.quantity] = toppings_list

    },


    onClickAddCartJSON: function (ev) {
        ev.preventDefault();
        var self = this;
        var varients_selected = false;
        this.$modal.find('.js_product:not(.main_product)').each(function () {
            var $item = $(this);
            var id = '#'+$item.find('input.product_id').val();
            if ($(id).prop('checked') == true){
                var quantity = parseInt($item.find('input[name="add_qty"]').val(), 10);
                varients_selected = true;
                $(id).prop('checked', false);
            }
        });
        var $link = $(ev.currentTarget);
        var $input = $link.closest('.input-group').find("input");
        var min = parseFloat($input.data("min") || 0);
        var max = parseFloat($input.data("max") || Infinity);
        var previousQty = parseFloat($input.val() || 0, 10);
        var quantity = ($link.has(".fa-minus").length ? -1 : 1) + previousQty;
        var newQty = quantity > min ? (quantity < max ? quantity : max) : min;

        if (newQty !== previousQty) {
            $input.val(newQty).trigger('change');
        }

        var $button_fa = $link.find('.fa')
        if ($button_fa.hasClass('fa-plus')){
            if (varients_selected) {
                $('.popup_td_span').topAlertjs({
                        type: 'confirm',
                        message: 'Would You Like To Add Previous Options?',
                        callback: function ( confirm ) { if( confirm ) {

                            if(previousQty){
                                if(self.product_merge[previousQty]){
                                    _.each(self.product_merge[previousQty], function (product) {
                                        $('#'+product).prop('checked', true);
                                        self.update_toppings();
                                    });
                                }
                            }
                            }
                        }
                });
            }
        }
        if ($button_fa.hasClass('fa-minus')){
            if(self.product_merge[$input.val()]){
                _.each(self.product_merge[$input.val()], function (product) {
                    $('#'+product).prop('checked', true);
                });
            }

             for(var object = 0; object < Object.keys(self.product_merge).length; object++) {
//                   console.log("s",Object.keys(self.product_merge).length,$input.val());
                  if ($input.val() <= object){
                     delete self.product_merge[object+1]
                   }

             }
        }

        return false;
    },

});
return OptionalProductsModal;


});