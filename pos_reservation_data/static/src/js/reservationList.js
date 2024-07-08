odoo.define('pos_reservation_data.reservationList',function (require) {
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

    models.load_models({
        model:  'pos.config',
        fields: [],
        loaded: function(self, orders){
            console.log("data",self.config.sale_order_days)
            rpc.query({
                    model: 'pos.order',
                    method: 'get_reservation_date',
                    args: [],
                }, {
                    shadow: true,
                }).then(function (result) {
                    self.env.pos.reservations = result;
            });
        }
    });


    class TableReservationList extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
            useListener('fetch_new-screen', this.fetch_new_data);
        }
        close() {
            this.showScreen('ProductScreen');
        }

        fetch_new_data(){
            var self = this;
            var params = {
                model: 'pos.order',
                method: 'get_reservation_date',
                args: [],
            }
            self.rpc(params, {async: false}).then(function(result){
                  self.env.pos.reservations = [];
                  self.env.pos.reservations = result;
                  self.render();
            }).catch(function () {
                const { confirmed: confirmedPopup } = this.showPopup('ConfirmPopup', {
                    title: 'Network Error',
                    body: 'No Reservations Found Please Check Network',
                });
                if (!confirmedPopup) return;
            });
        }

        get filteredReservationList() {
            var self = this;
            return this.env.pos.reservations;
        }

    }
    TableReservationList.template = 'TableReservationList';
    Registries.Component.add(TableReservationList);
    return TableReservationList;
});