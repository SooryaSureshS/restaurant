odoo.define('pos_table_waiting_list.WaitList',function (require) {
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
    const { Gui } = require('point_of_sale.Gui');
    var core = require('web.core');
    var _t = core._t;
    var rpc = require('web.rpc');

    models.load_models({
        model:  'pos.config',
        fields: [],
        loaded: function(self, orders){
            rpc.query({
                    model: 'table.waiting.line',
                    method: 'get_waiting_list',
                    args: [],
                }, {
                    shadow: true,
                }).then(function (result) {
                    self.env.pos.WaitList = result['waiting_list'];
                    self.env.pos.WaitListAvailableTables = result['available_tables'];
            });
        }
    });

    class WaitList extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
            useListener('fetch_new-screen', this.fetch_new_data);
            useListener('waiting-list-add', this.add_to_waiting_list);
        }
        close() {
            this.showScreen('FloorScreen');
        }
        add_to_waiting_list() {
            this.showPopup("AddToWaitListPopup", {
                title : _t("Add To Wait List"),
                confirmText: _t("Exit")
            });
        }
        mounted() {
            var self = this;
            self.fetch_new_data();
        }

        fetch_new_data(){
            var self = this;
            var params = {
                model: 'table.waiting.line',
                method: 'get_waiting_list',
                args: [],
            }
            self.rpc(params, {async: false}).then(function(result){
                self.env.pos.WaitList = [];
                self.env.pos.WaitList = result['waiting_list'];
                self.env.pos.WaitListAvailableTables = result['available_tables'];

                  self.render();
            }).catch(function () {
                const { confirmed: confirmedPopup } = this.showPopup('ConfirmPopup', {
                    title: 'Network Error',
                    body: 'No Waiting List Found Please Check Network',
                });
                if (!confirmedPopup) return;
            });
        }

        get filteredWaitList() {
            var self = this;
            return this.env.pos.WaitList;
        }
        get filterWaitListAvailableTables() {
            var self = this;
            return this.env.pos.WaitListAvailableTables;
        }
        editWaiting(waiting){
            var self = this;
            rpc.query({
                model: 'table.waiting.line',
                method: 'edit_waiting_list',
                args: [waiting],
            }).then(function (result) {
                if(result === false){
                    self.showPopup('ErrorPopup', {
                        title: _t('Failed'),
                        body: _t(
                        'Some Error Occurred. Please try again later'
                        ),
                    });
                }
                else{
                    self.env.pos.EditWaitList = result;
                    console.log("kllklklkkl",  result);
                    self.showPopup("EditWaitListPopup", {
                        title : _t("Add To Wait List"),
                        confirmText: _t("Exit")
                    });
                }
            });
        }
        confirmWaiting(waiting){
            var self = this;
            rpc.query({
                model: 'table.waiting.line',
                method: 'confirm_waiting_list',
                args: [waiting],
            }).then(function (result) {
                if(result === false){
                    self.showPopup('ErrorPopup', {
                        title: _t('Failed'),
                        body: _t(
                        'Some Error Occurred. Please try again later'
                        ),
                    });
                }
                else{
//                    self.env.pos.EditWaitList = result;
//                    console.log("kllklklkkl",  result);
//                    self.showPopup("EditWaitListPopup", {
//                        title : _t("Add To Wait List"),
//                        confirmText: _t("Exit")
//                    });
                    self.env.pos.WaitList = [];
                    self.env.pos.WaitList = result['waiting_list'];
                    self.env.pos.WaitListAvailableTables = result['available_tables'];
                    self.showScreen('FloorScreen');

                }
            });
        }
    }
    WaitList.template = 'WaitList';
    Registries.Component.add(WaitList);
    return WaitList;
});