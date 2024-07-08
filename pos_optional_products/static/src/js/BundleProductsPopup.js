odoo.define('pos_optional_products.BundleProductsPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
     const { useExternalListener } = owl.hooks;

    class BundlePopup extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        constructor() {
            super(...arguments);

        }

        mounted() {
//            this.inputRef.el.focus();
        }


    get ClickProduct() {
        var data = this.env.pos.bundle_parent_product
        var parent_product = {'id': data['id'], 'name': data['display_name'], 'list_price':data['lst_price'] }
        return parent_product;
    }
    async prepend_bundle_qty(){

        var qty = parseInt($('#parent_qty').val());
        console.log("Prepend", qty, typeof qty)
        if(typeof qty==='number' && (qty%1)===0) {
            qty = qty - 1;
            if (qty > 0){
                $('#parent_qty').val(qty);
            }
        }
    }
    async append_bundle_qty(){

        var qty = parseInt($('#parent_qty').val());
        console.log("Append", qty, typeof qty)
        if(typeof qty==='number' && (qty%1)===0) {
            qty = qty + 1;
            if (qty > 0){
                $('#parent_qty').val(qty);
            }
        }
    }

    async customise_pos(id,custom_value, choice_count, btn_count) {
        $('#tr_choice'+choice_count+custom_value+id).show();
        $('.customize'+custom_value+id+btn_count).hide();
        $('.close'+custom_value+id+btn_count).show();
        $('.radio_options').each(function(){
            $($(this).find('.radio_choice')).each(function(){
                if ($(this)[0].checked == true){
                        $(this).parent().parent().parent().parent().parent().find('td .categ_label').css('color','#18710e');
                }
            })
        })
    }
    async close_pos(id,custom_value, choice_count, btn_count) {
        $('#tr_choice'+choice_count+custom_value+id).hide();
        $('.customize'+custom_value+id+btn_count).show();
        $('.close'+custom_value+id+btn_count).hide();
        $('.radio_options').each(function(){
            $($(this).find('.radio_choice')).each(function(){

                if ($(this)[0].checked == true){

                    $(this).parent().parent().parent().parent().parent().find('td .categ_label').css('color','#18710e');
                }
            })
        })
    }
    async customise_variant(id,custom_value, choice_count, var_count) {
        $('.open'+custom_value+id+var_count).hide();
        $('.done'+custom_value+id+var_count).show();
        var data = '.'+custom_value+"optional"+var_count+"optional"+id;
            $('.open'+custom_value+id+var_count).parent().parent().parent().find('.optional_product').show();
    }
    async close_variant(id,custom_value, choice_count, var_count) {
        $('.open'+custom_value+id+var_count).show();
        $('.done'+custom_value+id+var_count).hide();
        $('.open'+custom_value+id+var_count).parent().parent().parent().find('.optional_product').hide();
    }

    get productsToDisplay() {
        var bundle_products = [];
        var data = this.env.pos.bundle_products_data['variant_values']
        for (var i=0;i<data.length; i++){
            if (data[i]!== undefined){
                var qty_list = []
                var qty = data[i]['bundle_product_qty']
                for (var k=0;k<parseInt(qty); k++){
                    qty_list.push('a')
                }

                bundle_products.push({
                'bundle_product_id':data[i]['bundle_product_id'],
                'bundle_product_name':data[i]['bundle_product_name'],
                'bundle_product_qty':qty_list,
                'choice_products':data[i]['choice_products'],})
            }
        }
        return bundle_products;
    }

    async confirm_addqty() {
        var self = this;
        var total_count =  self.env.pos.bundle_total_count;
        var count = 0;
        $('.radio_choice').each(function(){
            if ($(this)[0].checked == true){
                count = count + 1;
            }
        })
        if (count < total_count){
            $('#add_button_validation').css('display','block');
        }
        else{
            $('#add_button_validation').css('display','none');
            let order = this.env.pos.get_order();
            var parent_product = $('#parent_product').val();
            var parent_quantity = $('#parent_qty').val();
            var parent = self.env.pos.db.get_product_by_id(parent_product)
            if (parseInt(parent_quantity)>0){
//                for (var k=0;k<parseInt(parent_quantity); k++){
                    order.add_product(parent, {quantity:parseInt(parent_quantity)})
                    $('.radio_options').each(function(){
                        $($(this).find('.radio_choice')).each(function(){
                            if ($(this)[0].checked == true){
                                var choice_pro_id = $(this).attr('value')
                                var choice_pro_price = $(this).attr('choice_price')
                                var choice_pro_name = $(this).attr('choice_name')
                                var choice = self.env.pos.db.get_product_by_id(choice_pro_id)
                                if (choice != undefined){
                                    order.add_product(choice, {price:choice_pro_price, quantity:parseInt(parent_quantity)})
                                }
                                $('.optional_product').each(function(){
                                    $($(this).find('.variant_checkbox')).each(function(){
                                        if ($(this).is(":checked")){
                                            var variant_pro_id = $(this).attr('id')
                                            var variant_pro_price = $(this).attr('price')
                                            var variant_pro_name = $(this).attr('name')
                                            var variant = self.env.pos.db.get_product_by_id(variant_pro_id)
                                            if (variant != undefined){
                                                if (choice_pro_name ==variant_pro_name){
                                                    order.add_product(variant, {price:variant_pro_price, quantity:parseInt(parent_quantity)})
                                                }
                                            }
                                        }
                                    })
                                })
                            }
                        })
                    });
//                }
            }
                self.confirm();
        }
    }
    }
    BundlePopup.template = 'BundleProductsModal';
    BundlePopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',

    };
    Registries.Component.add(BundlePopup);
    return BundlePopup;
});