odoo.define('pos_size_category.productListInherit', function(require) {
    'use strict';


	const CashierName = require('point_of_sale.CashierName');
    const Registries = require('point_of_sale.Registries');
    const useSelectEmployee = require('pos_hr.useSelectEmployee');
    const { useBarcodeReader } = require('point_of_sale.custom_hooks');
    const ProductsWidget = require('point_of_sale.ProductsWidget');
    const ProductList = require('point_of_sale.ProductList');
    const { useListener } = require('web.custom_hooks');
    const { useState } = owl.hooks;

   const PosComponent = require('point_of_sale.PosComponent');
  var core = require('web.core');
  var QWeb = core.qweb;
    class ProductSizeCategory extends PosComponent {
     constructor() {
                super(...arguments);
//                const { selectEmployee, askPin } = useSelectEmployee();
//                this.askPin = askPin;
                this.data_item = "selectEmployee";
//                this.data_item = "selectEmployee";
                useListener('switch-size-category', this._switchSizeCategory);
                this.state = useState({ searchWord: '' });

//                useBarcodeReader({ cashier: this._onCashierScan });
            }
             mounted() {
//                this.env.pos.on('change:cashier', this.render, this);
            }
            willUnmount() {
//                this.env.pos.off('change:cashier', null, this);
            }

            _switchSizeCategory(event) {
                var self = this;
                var order = this.env.pos.get_order();

                $('.size_class_loop').each(function(){
                    $(this).removeClass('size_enabled');
                })
                $('#'+event.detail+'size_category').addClass('size_enabled');

                if(order.get_size() == event.detail){
                    $('#'+event.detail+'size_category').removeClass('size_enabled');
                    $('.product-list #product_info_list').each(function(){
                             var $product = $(this)
                             $product.show();
                    });
                    order.set_size(0);
                }else{
                    order.set_size(event.detail);
                    var pro = this.env.pos.db.get_product_by_size(event.detail);
                    if (pro.length>0){
                        $('.product-list #product_info_list').each(function(){
                             var $product = $(this)
                             $product.hide();
                            _.each(pro, function (size) {
                                if($product.attr('data-product-id') == size){
                                    $product.show();
                                }
                            });

                        });
                    }else{
                        $('.product-list #product_info_list').each(function(){
                             var $product = $(this)
                             $product.hide();
                    });
                    }
                }

            }
            get searchWord() {
                return this.state.searchWord.trim();
            }
            get product_size_category() {
                $('#hide_div_collapse').show();
                console.log("data found ssdssd",this.env.pos.product_size_category)
                return this.env.pos.product_size_category
            }
            get productsToDisplay() {
                console.log("datathis.searchWord",this.state)
                    if (this.searchWord !== '') {
                        return this.env.pos.db.search_product_in_category(
                            this.selectedCategoryId,
                            this.searchWord
                        );
                    } else {
                        return this.env.pos.db.get_product_by_category(this.selectedCategoryId);
                    }
                }
            _tryAddProduct(event) {
            const searchResults = this.productsToDisplay;
            console.log("datatttttttt",searchResults)
            // If the search result contains one item, add the product and clear the search.
            if (searchResults.length === 1) {
                const { searchWordInput } = event;
                this.trigger('click-product', searchResults[0]);
                // the value of the input element is not linked to the searchWord state,
                // so we clear both the state and the element's value.
                searchWordInput.el.value = '';
                this._clearSearch();
            }
        }


    }
    ProductSizeCategory.template = 'ProductSizeCategory';

    Registries.Component.add(ProductSizeCategory);

    return ProductSizeCategory;





//
//	const ProductSizeList = (ProductList) =>
//        class extends ProductList {
//            constructor() {
//                super(...arguments);
////                const { selectEmployee, askPin } = useSelectEmployee();
////                this.askPin = askPin;
////                this.data = "selectEmployee";
//                useListener('switch-size-category', this._switchSizeCategory);
////                useBarcodeReader({ cashier: this._onCashierScan });
//            }
//            mounted() {
////                this.env.pos.on('change:cashier', this.render, this);
//            }
//            willUnmount() {
////                this.env.pos.off('change:cashier', null, this);
//            }
//            _switchSizeCategory(event) {
//                console.log("size",event)
////                this.env.pos.set('selectedCategoryId', event.detail);
//            }
//
////        get product_size_category() {
////            console.log("data found",this.env.pos.product_size_category)
////            return this.env.pos.product_size_category
////        }
//        };
//
//    Registries.Component.extend(ProductList, ProductSizeList);
//
//    return ProductSizeList;

});

