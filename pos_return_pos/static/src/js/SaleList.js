odoo.define('pos_return_pos.SaleList',function (require) {
    "use strict";


    const { parse } = require('web.field_utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const { useErrorHandlers } = require('point_of_sale.custom_hooks');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { onChangeOrder } = require('point_of_sale.custom_hooks');
    var models = require('point_of_sale.models');
    var DB = require('point_of_sale.DB');
    var OrderReceipt = require('point_of_sale.OrderReceipt');

    var now = new Date()
    var rpc = require('web.rpc');

    models.load_models({
        model:  'pos.config',
        fields: [],
        loaded: function(self, orders){
//            self.sale_orders_refund = orders;
//            self.fetch_new_data()
            console.log("data",self.config.sale_order_days)
            rpc.query({
                    model: 'sale.order',
                    method: 'get_sale_order',
                    args: [self.config.sale_order_days],
                }, {
                    shadow: true,
                }).then(function (result) {
                    self.sale_orders_refund = result;
            });
        }
    });


    class SaleListReturn extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
            useListener('pos_return-screen', this.pos_screen);
            useListener('search', this._onSearch);
            useListener('fetch_new-screen', this.fetch_new_data);
            this.searchDetails = {};
//            this._initializeSearchFieldConstants();
        }
        close() {
            $('#hide_div_collapse').show();
            this.showScreen('ProductScreen');
        }
        pos_screen() {
            this.showScreen('OrderListReturn');
        }
        _onSearch(event) {
            const searchDetails = event.detail;
            Object.assign(this.searchDetails, searchDetails);
            this.render();
        }
        fetch_new_data(){
            var self = this;
            console.log("fetchedssss")
            var params = {
                model: 'sale.order',
                method: 'get_sale_order',
                args: [self.env.pos.config.sale_order_days],
            }
            self.rpc(params, {async: false}).then(function(result){
                  self.env.pos.sale_orders_refund = [];
                  self.env.pos.sale_orders_refund = result;
                  self.render();

            }).catch(function () {
                const { confirmed: confirmedPopup } = this.showPopup('ConfirmPopup', {
                    title: 'Network Error',
                    body: 'No Order Found Please Check Network',
                });
                if (!confirmedPopup) return;
            });
        }
        get filteredSaleOrdersList() {
            var self = this;
            const { fieldValue, searchTerm } = this.searchDetails;
            const fieldValues = 'Name'
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

            return this.saleList.filter(predicate);
        }
        get saleList() {
            return this.env.pos.sale_orders_refund;
        }

        get _searchFields() {
            var fields = {
                'Name': (order) => order.name,
                Date: (order) => moment(order.creation_date).format('YYYY-MM-DD hh:mm A'),
                Customer: (order) => order.get_client_name(),
            };
            return fields;
        }

        async ReturnClick(order_id) {
            var self = this;
            var order = this.get_order_by_id(order_id);
            var client = ''
            if (order.partner_id){
                 client = order.partner_id[0];
            }
            if (order && order.return_status ==='fully_return'){
                const { confirmed: confirmedPopup } = await this.showPopup('ConfirmPopup', {
                    title: 'Error',
                    body: 'This is a fully returned order',
                });
                if (!confirmedPopup) return;
            }
            else if (order && order.return_ref) {
                const { confirmed: confirmedPopup } = await this.showPopup('ConfirmPopup', {
                    title: 'Error',
                    body: 'This is a returned order',
                });
                if (!confirmedPopup) return;
            }
            else{
//              var params = {
//                        model: 'sale.order',
//                        method: 'get_lines',
//                        args: [order.id],
//                    }
//                    this.rpc(params, {async: false}).then(function(result){
//                          console.log("datata",result)
//                        if (result[0]){
                            const {  confirmed: confirmedLInes ,payload: data_return} = await self.showPopup('ReturnSaleListPopupsWidget',{'ref': order.name, 'client': client,'result':order.lines});
                            if(confirmedLInes){
                                   const { confirmed: confirmedPopup } = self.showPopup('ConfirmPopup', {
                                    title: 'Refund',
                                    body: data_return,
                                });
                                self.fetch_new_data();

                            }
//                        }

//                    }).catch(function () {
//                        const { confirmed: confirmedPopup } = this.showPopup('ConfirmPopup', {
//                            title: 'Error',
//                            body: 'No Data Found',
//                        });
//                        if (!confirmedPopup) return;
//                    });
            }
        }

        async AmountReturn(order_id) {
            var self = this;
            var order = this.get_order_by_id(order_id);
            var client = ''
            if (order.partner_id){
                 client = order.partner_id[0];
            }
            if (order && order.return_status ==='fully_return'){
                const { confirmed: confirmedPopup } = await this.showPopup('ConfirmPopup', {
                    title: 'Error',
                    body: 'This is a fully returned order',
                });
                if (!confirmedPopup) return;
            }
            else if (order && order.return_ref) {
                const { confirmed: confirmedPopup } = await this.showPopup('ConfirmPopup', {
                    title: 'Error',
                    body: 'This is a returned order',
                });
                if (!confirmedPopup) return;
            }
            else{
                const {  confirmed: confirmedLInes ,payload: data_return} = await self.showPopup('ReturnSaleListAmountWidget',{'ref': order.name, 'client': client,'order':order,'result':order.lines});
                console.log("LLLLLLLLLLLLLL",order.lines);
                if(confirmedLInes){
                       const { confirmed: confirmedPopup } = self.showPopup('ConfirmPopup', {
                        title: 'Refund',
                        body: data_return,
                    });
                    self.fetch_new_data();

                }
            }
        }




        get_order_by_id(id) {
            var orders = this.env.pos.sale_orders_refund;
            for (var i in orders){
                if (orders[i].id === id){
                    return orders[i];
                }
            }

        }

        _initializeSearchFieldConstants() {
            this.constants = {};
            Object.assign(this.constants, {
                searchFieldNames: Object.keys(this._searchFields),
                screenToStatusMap: this._screenToStatusMap,
            });
        }
    }

    SaleListReturn.template = 'ReturnSaleListScreens';

    Registries.Component.add(SaleListReturn);

    return SaleListReturn;


});