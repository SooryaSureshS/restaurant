odoo.define('pos_open_orders.openOrderScreen',function (require) {
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

    var rpc = require('web.rpc');
//    models.load_models({
//        model:  'pos.order',
//        fields: ['name', 'partner_id','date_order','amount_total', 'amount_tax',
//            'pos_reference','lines','state','session_id','company_id','return_ref','return_status'],
//        loaded: function(self, orders){
//            self.orders = orders;
//            }
//    });

//    models.load_models({
//        model:  'pos.config',
//        fields: [],
//        loaded: function(self, orders){
////            self.sale_orders_refund = orders;
////            self.fetch_new_data()
//            console.log("data",self.config.sale_order_days)
//            rpc.query({
//                    model: 'pos.order',
//                    method: 'get_pos_order',
//                    args: [self.config.pos_order_days],
//                }, {
//                    shadow: true,
//                }).then(function (result) {
//                    self.orders = result;
//            });
//        }
//    });


    class OpenOrderScreen extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
            useListener('close-screen-product', this.close_product);
            useListener('search', this._onSearch);
//            useListener('sale_return-screen', this.sale_order);
//            useListener('fetch_new-screen', this.fetch_new_data);
            this.searchDetails = {};
            this._initializeSearchFieldConstants();
        }
        close() {
            this.showScreen('FloorScreen', { floor: this.floor });
        }
        close_product() {
            $('#hide_div_collapse').show();
            this.showScreen('ProductScreen');
        }

//        sale_order() {
//            console.log("sale ordersd")
//            this.showScreen('SaleListReturn');
//        }
//        fetch_new_data(){
//            var self = this;
//            var params = {
//                model: 'pos.order',
//                method: 'get_pos_order',
//                args: [self.env.pos.config.pos_order_days],
//            }
//            self.rpc(params, {async: false}).then(function(result){
//                  self.env.pos.orders = [];
//                  self.env.pos.orders = result;
//                  self.render();
//
//            }).catch(function () {
//                const { confirmed: confirmedPopup } = this.showPopup('ConfirmPopup', {
//                    title: 'Network Error',
//                    body: 'No Order Found Please Check Network',
//                });
//                if (!confirmedPopup) return;
//            });
//        }
        _onSearch(event) {
            const searchDetails = event.detail;
            Object.assign(this.searchDetails, searchDetails);
            this.render();
        }
        get filteredOrdersList() {
            var self = this;
            const { fieldValue, searchTerm } = this.searchDetails;
            const fieldValues = 'Receipt Number'
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
            return this.orderList.filter(predicate);
//            return self.env.pos.orders;
        }
        get orderList() {
            console.log("order listsss",this.env.pos.orders_open);
            return this.env.pos.orders_open;
        }

        get _searchFields() {
            var fields = {
                'Receipt Number': (order) => order.pos_reference,
                Date: (order) => moment(order.creation_date).format('YYYY-MM-DD hh:mm A'),
                Customer: (order) => order.get_client_name(),
            };
            return fields;
        }
        selectPosOrder(id){
            console.log("order idssssss",id);
            var self = this;
            var params = {
                model: 'pos.order',
                method: 'get_pos_open_order_by_id',
                args: [id,self.env.pos.env.session.user_context],
            }
            self.rpc(params, {async: false}).then(function(result){
                  console.log("newssssssssss",result);
                  if (result){
//                        new update
                        const currentOrder = self.env.pos.get_order();
//                        var orders = self.env.pos.set_table(null);

                        self.env.pos.open_order_up();

                        console.log("cxxxxxxxxxxxxu",self.env.pos.get_order());





//                        const table_obj = self.env.pos.tables_by_id[result['table']];
//                        var orders = self.env.pos.set_table(table_obj);
//                        var orders = self.env.pos.set_table(table_obj);

//                         this.env.pos.set_table(order.table, order);
//                        var currentOrder = self.env.pos.get_order();
//                        self.env.pos.get_order().finalize();
//                        self.env.pos.set_table(table_obj);
//                        self.env.pos.db.remove_order(currentOrder);
//                        self.env.pos.add_new_order();
//                        var currentOrder =  self.env.pos.get_order();
//                        var orderlines = currentOrder.get_orderlines();
//                        for(var i = 0, len = orderlines.length; i < len; i++){
//                            currentOrder.remove_orderline(orderlines);
//                        }

//                        console.log("cxxxxxxxxxxxxu",currentOrder);
//                        if (currentOrder.get_orderline()){
//                             currentOrder.get_orderline().forEach(function (orderline) {
//                                     console.log("cu",currentOrder);
//                                     currentOrder.remove_orderline(orderline);
//                             });
//                        }
                         _.each(result['lines'], function (line){
                            var tip_product = self.env.pos.db.get_product_by_id(line.product_id);
                            self.env.pos.get_order().add_product(tip_product,{
                                quantity: line.qty,
                                discount: line.discount,
                                merge: false,
                                });
                         });

                         if (result['partner_id']){
                             var partner_id = self.env.pos.db.get_partner_by_id(result['partner_id']);
                             if (partner_id) {
                                self.env.pos.get_order().set_client(partner_id);
                             }
                         }
                         if (result['id']){
                            self.env.pos.get_order().set_open_order_ref(result['name']);
                            self.env.pos.get_order().set_open_order_id(result['id']);
                            self.env.pos.get_order().set_open_order_table(result['table']);
                            console.log("current_orderssss",self.env.pos.get_order());
                         }
                         if (result['delivery_type']){
                            self.env.pos.get_order().set_delivery_type(result['delivery_type']);
                             console.log("current_orderssss",self.env.pos.get_order());
                         }
                         self.showScreen('PaymentScreen');
                  }

            })
        }
//
//        async ReturnClick(order_id) {
//            var self = this;
//            var order = this.get_order_by_id(order_id);
//            var client = ''
//            if (order.partner_id){
//                 client = order.partner_id[0];
//            }
//            if (order && order.return_status ==='fully_return'){
//                const { confirmed: confirmedPopup } = await this.showPopup('ConfirmPopup', {
//                    title: 'Error',
//                    body: 'This is a fully returned order',
//                });
//                if (!confirmedPopup) return;
//            }
//            else if (order && order.return_ref) {
//                const { confirmed: confirmedPopup } = await this.showPopup('ConfirmPopup', {
//                    title: 'Error',
//                    body: 'This is a returned order',
//                });
//                if (!confirmedPopup) return;
//            }
//            else{
//              var params = {
//                        model: 'pos.order',
//                        method: 'get_lines',
//                        args: [order.pos_reference],
//                    }
//                    this.rpc(params, {async: false}).then(function(result){
//                        if (result[0]){
//                            const { confirmed } = self.showPopup('ReturnPopupsWidget',{'ref': order.pos_reference, 'client': client,'result':result[0]});
//                        }
//
//                    }).catch(function () {
//                        alert("NO DATA")
//                    });;
//
//
//            }
//        }
//        get_order_by_id(id) {
//            var orders = this.env.pos.orders;
//            for (var i in orders){
//                if (orders[i].id === id){
//                    return orders[i];
//                }
//            }
//
//        }
//        async CreateGiftCard() {
//            const order = this.env.pos.get_order();
//            if (!order.get_client()) {
//                const { confirmed: confirmedPopup } = await this.showPopup('ConfirmPopup', {
//                    title: 'Need customer to gift card',
//                    body: 'Do you want to open the customer list to select customer?',
//                });
//                if (!confirmedPopup) return;
//                $('.gift_card_header_buttons').hide();
//                $('.client-details-contents .client-details').css('background-color','snow');
//                const { confirmed: confirmedTempScreen, payload: newClient } = await this.showTempScreen(
//                    'ClientListScreen'
//                );
//                if (!confirmedTempScreen) {
//                     $('.gift_card_header_buttons').show();
//                }
//                if (!confirmedTempScreen) return;
//                $('.gift_card_header_buttons').show();
//                const { confirmed } = await this.showPopup('CreateCardPopupWidget',{'partner_id': newClient});
//            }else{
//                const { confirmed } = await this.showPopup('CreateCardPopupWidget',{'partner_id': order.get_client()});
//            }
//        }
        _initializeSearchFieldConstants() {
            this.constants = {};
            Object.assign(this.constants, {
                searchFieldNames: Object.keys(this._searchFields),
                screenToStatusMap: this._screenToStatusMap,
            });
        }
    }

    OpenOrderScreen.template = 'OpenOrderScreen';

    Registries.Component.add(OpenOrderScreen);

    return OpenOrderScreen;


});