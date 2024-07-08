odoo.define('pos_optional_products.ProductsPopupLarge', function(require) {
    'use strict';
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { useState } = owl.hooks;
    var models = require('point_of_sale.models');
    var core = require('web.core');

//    models.load_fields("pos.order.line", ['option_line_ids']);

    class OptionalProductsPopupLarge extends AbstractAwaitablePopup {
    constructor() {
    super(...arguments);
    }

    get ClickProduct() {
        var data = this.env.pos.optional_parent_product_large;
        var parent_product = {'id': data['id'], 'name': data['display_name'],'description_sale':data['description_sale'] ,'list_price':data['lst_price'],'image_url':'/web/image/product.product/'+data['id']+'/image_1920' }
        return parent_product;
    }
    get productsToDisplay() {

        var optional_products = [];
        var data = this.env.pos.optional_products_large;
        for (var i=0;i<data.length; i++){
        if (data[i]!== undefined){
            optional_products.push({'id':data[i]['id'],'name':data[i]['display_name'], 'group':data[i]['product_option_group'], 'list_price':data[i]['lst_price'] })
        }
        }
        return optional_products;
    }

    get get_group() {

        var optional_groups = [];
        var optional = [];

        var data = this.env.pos.optional_products_large;

        for (var i=0;i<data.length; i++){
            if (data[i]!== undefined){

            if (data[i]['product_option_group']){
            console.log(data[i]);
            if(optional.includes(data[i]['product_option_group'][0])==false){
            var group_elements= data[i]['product_option_group'];
            group_elements.push(data[i].option_sequence)
            optional_groups.push(group_elements)
            optional.push(data[i]['product_option_group'][0]);
            }}

        }
        }
        var sorted_array = optional_groups.sort((a,b) => {
        return a[2] - b[2];} )
        console.log("get_group get_group get_group get_group",sorted_array)

        return sorted_array;
    }
}

   OptionalProductsPopupLarge.template = 'OptionalProductsPopupLarge';
   OptionalProductsPopupLarge.defaultProps = {
       confirmText: 'Ok',
       cancelText: 'Cancel',
       title: 'Optional Products Large',
       body: '',
   };
   Registries.Component.add(OptionalProductsPopupLarge);
   return OptionalProductsPopupLarge;
});
