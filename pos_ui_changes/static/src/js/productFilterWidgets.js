odoo.define('pos_ui_changes.productFilterWidgets', function(require) {
    'use strict';

    const { useRef } = owl.hooks;
    const { debounce } = owl.utils;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class FilterSearchByProduct extends PosComponent {
        constructor() {
            super(...arguments);
            this.searchWordInput = useRef('search-word-input');
            this.updateSearch = debounce(this.updateSearch, 100);
        }
//        get FiltersInformation() {
//            var self = this
//            const order = self.env.pos
//            const filter_info = []
//        }

        clearSearch1(event) {
            var self = this;
            var filter_list = []
            if (event.target.value != 'Filter'){
                $('.product-list-container .product-list #product_info_list').each(function(){
                    var pro_product = self.env.pos.db.get_product_by_id($(this).attr('data-product-id'));
                    if (event.target.value === 'gf'){
                         if (pro_product.gf){
                             $(this).show();
                         }else{
                            $(this).hide();
                         }
                    }
                    if (event.target.value === 'v'){
                         if (pro_product.v){
                             $(this).show();
                         }else{
                            $(this).hide();
                         }
                    }
                    if (event.target.value === 'veg'){
                         if (pro_product.veg){
                             $(this).show();
                         }else{
                            $(this).hide();
                         }
                    }
                });
            }else{
                $('.product-list-container .product-list #product_info_list').each(function(){
                    $(this).show();
                });
            }

        }
        availableOptions(event) {
            var self = this;
            var filter_list = []
            if (event.target.value == 'available_option'){
                $('#hide_div_collapse').show();
                this.showScreen('ProductScreen');
            }
             if (event.target.value == 'kvs'){
                $('#hide_div_collapse').hide();
                this.showScreen('kitchenScreenWidget');
            }
              if (event.target.value == 'refund'){
                $('#hide_div_collapse').hide();
                this.showScreen('OrderListReturn');
            }
            if (event.target.value == 'recall'){
                $('#hide_div_collapse').hide();
                this.showScreen('OrderTable');
            }
            if (event.target.value == 'open_orders'){
                $('#hide_div_collapse').hide();
                this.fetch_new_data();
            }


        }
        fetch_new_data(){
            var self = this;


//            var fetchedOrders = this._fetchOrders([999,999]);
//            fetchedOrders.forEach((order) => {
//                console.log("aaaaa",fetchedOrders.json());
//            });
//            console.log("aaaaa",this._fetchOrders([999]));
            var params = {
                model: 'pos.order',
                method: 'get_pos_open_order',
                args: [self.env.pos.pos_session.id],
            }
            self.rpc(params, {async: false}).then(function(result){
                  self.env.pos.orders_open = [];
                  self.env.pos.orders_open = result;
//                  self.render();
                  self.showScreen('OpenOrderScreen');

            }).catch(function () {
                const { confirmed: confirmedPopup } = this.showPopup('ConfirmPopup', {
                    title: 'Network Error',
                    body: 'No Order Found Please Check Network',
                });
                if (!confirmedPopup) return;
            });
        }
        get FiltersAvailable() {
            $('#availableOptions').val('available_option')
        }

    }
    FilterSearchByProduct.template = 'FilterSearchByProduct';

    Registries.Component.add(FilterSearchByProduct);

    return FilterSearchByProduct;
});
