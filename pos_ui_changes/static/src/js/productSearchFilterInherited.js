odoo.define('pos_ui_changes.productSearchFilterInherited', function(require) {
    'use strict';

    const { useState, useRef, onPatched } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const { onChangeOrder } = require('point_of_sale.custom_hooks');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductsWidgetControlPanel = require('point_of_sale.ProductsWidgetControlPanel');

       const ProductsWidgetControlPanelNew = (ProductsWidgetControlPanel) =>
        class extends ProductsWidgetControlPanel {
             clearSearch() {
                    console.log("data found");
                    this.searchWordInput.el.value = '';
                    this.trigger('clear-search');
                    $('#product_filters_informations').val("Filter");
                    $('.product-list-container .product-list #product_info_list').each(function(){
                             $(this).show();
                    });
                }
                updateSearch(event) {
                    this.trigger('update-search', event.target.value);
                    if (event.key === 'Enter') {
                        // We are passing the searchWordInput ref so that when necessary,
                        // it can be modified by the parent.
                        this.trigger('try-add-product', { searchWordInput: this.searchWordInput });
                    }
                    $('#product_filters_informations').val("Filter");
                    $('.product-list-container .product-list #product_info_list').each(function(){
                             $(this).show();
                    });
                }
                get clearOptionalProduct() {
                    if(this.env.pos.get('selectedCategoryId') == 0){
                        _.each(this.env.pos.db.product_by_id, function (product_by_id) {
                            if(product_by_id.is_optional_product){
                                $('.product-list-container #product_info_list').each(function(){
                                    var pro = $(this).attr('data-product-id');
                                    if (product_by_id.id == pro){
                                        $(this).hide();
                                    }
                                });
                            }
                        });

                    }else{
                        $('.product-list-container #product_info_list').each(function(){
                           $(this).show();

                        });
                    }
                }

        };

    Registries.Component.extend(ProductsWidgetControlPanel, ProductsWidgetControlPanelNew);

    return ProductsWidgetControlPanel;

});