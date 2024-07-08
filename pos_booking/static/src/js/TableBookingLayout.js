odoo.define('pos_booking.TableBookingLayout',function (require) {
    "use strict";


    const { parse } = require('web.field_utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const { useErrorHandlers } = require('point_of_sale.custom_hooks');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');
//    const { onChangeOrder } = require('point_of_sale.custom_hooks');
    var models = require('point_of_sale.models');
//    var DB = require('point_of_sale.DB');
//    var OrderReceipt = require('point_of_sale.OrderReceipt');
    const ajax = require('web.ajax');

//    models.load_models(
//        {
//        model: 'pos.order',
//        fields: ['name'],
//        loaded: function(self,order_lines){
//            ajax.rpc("/recall/orders", {}).then(function (result) {
//                    self.env.pos.recall_orders = null;
//                    self.env.pos.recall_orders = result[0];
//                    self.env.pos.recall_orders_sale = result[1];
//            });
//        }
//    });

    class TableBookingLayout extends PosComponent {
        constructor() {
            super(...arguments);
//            useListener('close-screen', this.close);
//            useListener('search', this._onSearch);
//            useListener('load-data', this._load_data);
//            this.searchDetails = {};
//            this._initializeSearchFieldConstants();
//            this._initializeAjaxCall();
            this.table_info = this.props.table
            this.future_booking = this.props.future_booking;
            useListener('edit_future_booking', this._edit_future_booking);
        }

//        close() {
//            if(this.env.pos.user.kitchen_screen_user === 'cook'){
//                this.showScreen('kitchenScreenWidget');
//            }
//            else if(this.env.pos.user.kitchen_screen_user === 'manager'){
//                this.showScreen('kitchenScreenWidget');
//            }
//            else if(this.env.pos.user.kitchen_screen_user === 'admin'){
//                this.showScreen('ProductScreen');
//            }
//        }
        mounted() {
            var self = this;
            self.env.pos.iseditLayout = false;
        }
        async new_booking_rev () {
            var self = this;
            var tableId = $('#new_table_booking').attr('data-table');
            var table = this.env.pos.tables_by_id[tableId]
                 if (this.env.pos.config.module_pos_hr){
                                             var employee = this.env.pos.get_cashier();
                                             const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
                                                isPassword: true,
                                                title: this.env._t('Password ?'),
                                                startingValue: null,
                                            });

                                            if (!confirmed) return false;

                                            if (employee.pin === Sha1.hash(inputPin)) {
                                               const { confirmedd } =  await Gui.showPopup('TableNewBooking',{table: table})
                                            } else {
                                                await this.showPopup('ErrorPopup', {
                                                    title: this.env._t('Incorrect Password'),
                                                });
                                                return false;
                                            }
                                       }else{
                                            const { confirmedd } =  await Gui.showPopup('TableNewBooking',{table: table})
                                       }

        }
        async select_table_rev () {
            var self = this;
            if (self.env.pos.config.iface_floorplan) {
                    const table = self.env.pos.table;
                    this.showScreen('FloorScreen');
            }
        }
        async edit_table_rev () {
            var self = this;
//             console.log("slect table edit mode active",this.env.pos);
//              if (this.env.pos.config.iface_floorplan) {
//                    const table = this.env.pos.table;
//                    this.env.pos.iseditLayout = true;
////                    this.showScreen('FloorScreen', { floor: pos.table ? pos.table.floor : null });
//                    this.showScreen('FloorScreen', { editModeReq: true });
//            }
                const selectedTable = this.table_info;
                if (!selectedTable) return;
                const { confirmed, payload: newName } = await this.showPopup('EditTablePopup', {
                    startingValue: selectedTable.name,
                    seatValue: selectedTable.seats,
                    title: this.env._t('Edit Table Name and Seat ?'),
                });
                if (!confirmed) return;
                if (newName.seats !== selectedTable.seats) {
                    if (newName.seats % 1 === 0){
                        if (newName.seats > 0){
                            if (newName.seats !== selectedTable.seats) {
                                selectedTable.seats = newName.seats;
                                selectedTable.name = newName.table_name;
                                await this._save(selectedTable);
                            }
                        }else{
                             await this.showPopup('ErrorPopup', {
                                title: this.env._t('Incorrect Seat number'),
                            });
                        }
                    }else{
                         await this.showPopup('ErrorPopup', {
                            title: this.env._t('Incorrect Seat number'),
                        });
                    }
                }
//                console.log("fetched firmations",newName);
                if (newName.table_name !== selectedTable.name) {
                    selectedTable.name = newName.table_name;
                    await this._save(selectedTable);
                }
        }
        async _save(table) {
            const fields = this.env.pos.models.find((model) => model.model === 'restaurant.table')
                .fields;
            const serializeTable = {};
            for (let field of fields) {
                if (typeof table[field] !== 'undefined') {
                    serializeTable[field] = table[field];
                }
            }
            serializeTable.id = table.id;
            const tableId = await this.rpc({
                model: 'restaurant.table',
                method: 'create_from_ui',
                args: [serializeTable],
            });
            table.id = tableId;
            this.env.pos.tables_by_id[tableId] = table;
        }
        async _edit_future_booking () {
            var self = this;
            const table = event.detail;
            self.future_booking.forEach((booking) => {
                if (booking.id == table){
                    console.log("sgfdhjgfdghsdjdfhgdsf",booking);

                    this.showPopup('TableFutureBooking',{'booking': booking});

                }
            });

        }

    }

    TableBookingLayout.template = 'TableBookingLayout';

    Registries.Component.add(TableBookingLayout);

    return TableBookingLayout;


});
