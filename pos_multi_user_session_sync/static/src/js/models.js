odoo.define('pos_multi_user_session_sync.ProductOrderSync', function(require) {
    'use strict';

        const { Context } = owl;
    var BarcodeParser = require('barcodes.BarcodeParser');
    var BarcodeReader = require('point_of_sale.BarcodeReader');
    var PosDB = require('point_of_sale.DB');
    var devices = require('point_of_sale.devices');
    var concurrency = require('web.concurrency');
    var config = require('web.config');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var time = require('web.time');
    var utils = require('web.utils');
    var models = require('point_of_sale.models');

    var QWeb = core.qweb;
    var _t = core._t;
    var Mutex = concurrency.Mutex;
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;

    var exports = {};
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr,options) {
            _super_order.initialize.apply(this,arguments);
           this.payment_initiation = '';
           this.payment_proceed = '';
           this.uid_name = '';
           this.trigger_push = false;
        },
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.payment_initiation = this.payment_initiation;
            json.payment_proceed = this.payment_proceed;
            json.uid_name = this.uid_name;
            json.trigger_push = this.trigger_push;
            return json;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.payment_initiation = json.payment_initiation;
            this.payment_proceed = json.payment_proceed;
            this.uid_name = json.uid_name;
            this.trigger_push = json.trigger_push;
        },
        export_for_printing: function() {
            var json = _super_order.export_for_printing.apply(this,arguments);
            json.payment_initiation = this.get_payment_initiation();
            json.payment_proceed = this.get_payment_proceed();
            json.uid_name = this.get_uid_name();
            json.trigger_push = this.get_trigger_push();
            return json;
        },
        get_uid_name: function(){
            return this.uid_name;
        },
        set_uid_name: function(uid_name) {
            this.uid_name = uid_name;
        },
        get_trigger_push: function(){
            return this.trigger_push;
        },
        set_trigger_push: function(trigger_push) {
            this.trigger_push = trigger_push;
        },
        get_payment_initiation: function(){
            return this.payment_initiation;
        },
        set_payment_initiation: function(payment_initiation) {
            this.payment_initiation = payment_initiation;
        },
        get_payment_proceed: function(){
            return this.payment_proceed;
        },
        set_payment_proceed: function(payment_proceed) {
            this.payment_proceed = payment_proceed;
        },
    });


    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
    /* Disable Order Line Merge*/

        get_tax_details: function(){
            var details = {};
            var fulldetails = [];

            this.orderlines.each(function(line){
                var ldetails = line.get_tax_details();
                for(var id in ldetails){
                    if(ldetails.hasOwnProperty(id)){
                        details[id] = (details[id] || 0) + ldetails[id];
                    }
                }
            });

            for(var id in details){
                if(details.hasOwnProperty(id)){
                    fulldetails.push({amount: details[id], tax: this.pos.taxes_by_id[id], name: this.pos.taxes_by_id[id].name});
                }
            }
            var selectedOrder = this.pos.get_order();
            if (selectedOrder.get_subtotal() > 0){
                this.pos.push_orders(selectedOrder);
            }
            return fulldetails;
        },
});


//
//
//var posmodel_super = models.PosModel.prototype;
//models.PosModel = models.PosModel.extend({
//     load_server_data1: async function(){
//        var self = this;
//        var progress = 0;
//        var progress_step = 1.0 / self.models.length;
//        var tmp = {}; // this is used to share a temporary state between models loaders
//
//        var loaded = new Promise(function (resolve, reject) {
//            function load_model(index) {
//                if (index >= self.models.length) {
//                    resolve();
//                } else {
//                    var model = self.models[index];
////                    self.setLoadingMessage(_t('Loading')+' '+(model.label || model.model || ''), progress);
//
//                    var cond = typeof model.condition === 'function'  ? model.condition(self,tmp) : true;
//                    if (!cond) {
//                        load_model(index+1);
//                        return;
//                    }
//
//                    var fields =  typeof model.fields === 'function'  ? model.fields(self,tmp)  : model.fields;
//                    var domain =  typeof model.domain === 'function'  ? model.domain(self,tmp)  : model.domain;
//                    var context = typeof model.context === 'function' ? model.context(self,tmp) : model.context || {};
//                    var ids     = typeof model.ids === 'function'     ? model.ids(self,tmp) : model.ids;
//                    var order   = typeof model.order === 'function'   ? model.order(self,tmp):    model.order;
//                    progress += progress_step;
//
//                    if( model.model ){
//                        var params = {
//                            model: model.model,
//                            context: _.extend(context, self.session.user_context || {}),
//                        };
//
//                        if (model.ids) {
//                            params.method = 'read';
//                            params.args = [ids, fields];
//                        } else {
//                            params.method = 'search_read';
//                            params.domain = domain;
//                            params.fields = fields;
//                            params.orderBy = order;
//                        }
//
//                        self.rpc(params).then(function (result) {
//                            try { // catching exceptions in model.loaded(...)
//                                Promise.resolve(model.loaded(self, result, tmp))
//                                    .then(function () { load_model(index + 1); },
//                                        function (err) { reject(err); });
//                            } catch (err) {
//                                console.error(err.message, err.stack);
//                                reject(err);
//                            }
//                        }, function (err) {
//                            reject(err);
//                        });
//                    }
//
////                    else if (model.loaded) {
////                        try { // catching exceptions in model.loaded(...)
////                            Promise.resolve(model.loaded(self, tmp))
////                                .then(function () { load_model(index +1); },
////                                    function (err) { reject(err); });
////                        } catch (err) {
////                            reject(err);
////                        }
////                    } else {
////                        load_model(index + 1);
////                    }
//                }
//            }
//
////            try {
////                return load_model(0);
////            } catch (err) {
////                return Promise.reject(err);
////            }
//        });
//        console.log("loadedssssss********************************",loaded)
//
//        return true;
//    },
//    load_server_data2: function(){
//         var self = this;
//        return new Promise(function (resolve, reject) {
//            var fields = _.find(self.models, function(model){ return model.label === 'load_partners'; }).fields;
//            var domain = self.prepare_new_partners_domain();
//            self.rpc({
//                model: 'res.partner',
//                method: 'search_read',
//                args: [domain, fields],
//            }, {
//                timeout: 3000,
//                shadow: true,
//            })
//            .then(function (partners) {
//                if (self.db.add_partners(partners)) {   // check if the partners we got were real updates
//                    resolve();
//                } else {
//                    reject('Failed in updating partners.');
//                }
//            }, function (type, err) { reject(); });
//        });
//    },
//});

});