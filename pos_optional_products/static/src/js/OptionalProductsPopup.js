odoo.define('pos_optional_products.OptionalProductsPopup', function(require) {
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

    models.load_fields("pos.order.line", ['option_line_ids']);

    class OptionalProductsPopup extends AbstractAwaitablePopup {
    constructor() {
    super(...arguments);
    }

    get ClickProduct() {
        var data = this.env.pos.optional_parent_product
        var parent_product = {'id': data['id'], 'name': data['display_name'], 'list_price':data['lst_price'] }
        return parent_product;
    }
    get productsToDisplay() {
        var optional_products = [];
        var data = this.env.pos.optional_products_data
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
        var data = this.env.pos.optional_products_data

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

        return sorted_array;
    }

    async confirm_products() {
            var self = this;
            var parent_product = $('#parent_product').val();
            var parent_quantity = $('#parent_qty').val();
            var parent = self.env.pos.db.get_product_by_id(parent_product)
            var currentOrder = this.env.pos.get_order()
            currentOrder.add_product(parent, {
                quantity: parent_quantity,
            });

            var selected_child = document.querySelectorAll('input[type="checkbox"]:checked');
            for(var i=0; i<selected_child.length; i++){
                var child_pro = selected_child[i]['id'];
                var child = self.env.pos.db.get_product_by_id(child_pro)
                currentOrder.add_product(child, {
                    quantity: parent_quantity,
                });
            }
            return this.confirm();
    }
}

   OptionalProductsPopup.template = 'OptionalProductsPopup';
   OptionalProductsPopup.defaultProps = {
       confirmText: 'Ok',
       cancelText: 'Cancel',
       title: 'Optional Products',
       body: '',
   };
   Registries.Component.add(OptionalProductsPopup);
   return OptionalProductsPopup;
});
