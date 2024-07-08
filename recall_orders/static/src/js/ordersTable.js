odoo.define('recall_orders.ordersTable',function (require) {
    "use strict";


    const { parse } = require('web.field_utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const { useErrorHandlers } = require('point_of_sale.custom_hooks');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
//    const { onChangeOrder } = require('point_of_sale.custom_hooks');
    var models = require('point_of_sale.models');
//    var DB = require('point_of_sale.DB');
//    var OrderReceipt = require('point_of_sale.OrderReceipt');
    const ajax = require('web.ajax');

    models.load_models(
        {
        model: 'pos.order',
        fields: ['name'],
        loaded: function(self,order_lines){
            ajax.rpc("/recall/orders", {}).then(function (result) {
                    self.env.pos.recall_orders = null;
                    self.env.pos.recall_orders = result[0];
                    self.env.pos.recall_orders_sale = result[1];
            });
        }
    });

    class OrderTable extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
            useListener('search', this._onSearch);
            useListener('load-data', this._load_data);
            this.searchDetails = {};
            this._initializeSearchFieldConstants();
            this._initializeAjaxCall();
        }

        close() {
            if(this.env.pos.user.kitchen_screen_user === 'cook'){
                this.showScreen('kitchenScreenWidget');
            }
            else if(this.env.pos.user.kitchen_screen_user === 'manager'){
                this.showScreen('kitchenScreenWidget');
            }
            else if(this.env.pos.user.kitchen_screen_user === 'admin'){
                $('#hide_div_collapse').show();
                this.showScreen('ProductScreen');
            }
        }
        mounted() {
            var self = this;
        }
        _initializeAjaxCall () {
            var self = this;
             ajax.rpc("/recall/orders", {}).then(function (result) {
                    self.env.pos.recall_orders = null;
                    self.env.pos.recall_orders = result[0];
                    self.env.pos.recall_orders_sale = null;
                    self.env.pos.recall_orders_sale = result[1];
                    self.render();
            });

        }

        _onSearch(event) {
            const searchDetails = event.detail;
            Object.assign(this.searchDetails, searchDetails);
            this.render();
        }
        _load_data (){
            var self = this;
            ajax.rpc("/recall/orders", {}).then(function (result) {
                    self.env.pos.recall_orders = null;
                    self.env.pos.recall_orders = result[0];
                    self.env.pos.recall_orders_sale = null;
                    self.env.pos.recall_orders_sale = result[1];
                    self.render();
            });
        }
        get filteredOrdersList() {
            var self = this;
            var order = self.env.pos.recall_orders;
            const { fieldValue, searchTerm } = this.searchDetails;
            const fieldValues = 'Receipt Number'
//            const fieldValues = 'customer name'
            const fieldAccessor = this._searchFields[fieldValues];
            const searchCheck = (order) => {
                if (!fieldAccessor) return true;
                const fieldValue = fieldAccessor(order);
                if (fieldValue === null) return true;
                if (!searchTerm) return true;
                return fieldValue && fieldValue.toString().toLowerCase().includes(searchTerm.toLowerCase());
            };

            const predicate = (order) => {
                return searchCheck(order);
            };
            return self.orderList.filter(predicate);
        }


        get filteredSaleOrdersList() {
            var self = this;
            var order = self.env.pos.recall_orders_sale;
            const { fieldValue, searchTerm } = this.searchDetails;
            const fieldValues = 'Receipt Number'
//            const fieldValues = 'customer name'
            const fieldAccessor = this._searchFields[fieldValues];
            const searchCheck = (order) => {
                if (!fieldAccessor) return true;
                const fieldValue = fieldAccessor(order);
                if (fieldValue === null) return true;
                if (!searchTerm) return true;
                return fieldValue && fieldValue.toString().toLowerCase().includes(searchTerm.toLowerCase());
            };

            const predicate = (order) => {
                return searchCheck(order);
            };
            return self.orderListSale.filter(predicate);
        }
        get orderList() {
            return this.env.pos.recall_orders.reverse();
        }
        get orderListSale() {
            return this.env.pos.recall_orders_sale.reverse();
        }

        get _searchFields() {
            var self = this;
            var order = self.env.pos.recall_orders;
            var fields = {
                'Receipt Number': (order) => order.pos_reference,
//                Date: (order) => moment(order.preparation_date).format('YYYY-MM-DD hh:mm A'),
                'Customer Name': (order) => order.customer_name,
            };

            return fields;
        }

        async PreviewClick(order) {
            var self = this;
            self.showPopup('RecallPopupsWidget',{'ref': order.pos_reference, 'client': order.customer_name,'result':order.lines});
        }
        async PrintReceipt(order) {
            var self = this;
            this.showScreen('ReceiptScreenRecall', {'order': order, 'widget': self});
        }

        _initializeSearchFieldConstants() {
            this.constants = {};
            Object.assign(this.constants, {
                searchFieldNames: Object.keys(this._searchFields),
                screenToStatusMap: this._screenToStatusMap,
            });
        }
    }

    OrderTable.template = 'RecallOrderListScreens';

    Registries.Component.add(OrderTable);

    return OrderTable;


});
