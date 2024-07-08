odoo.define('store_sales_dashboard.DashboardRewrite', function (require) {
"use strict";

const ActionMenus = require('web.ActionMenus');
const ComparisonMenu = require('web.ComparisonMenu');
const ActionModel = require('web/static/src/js/views/action_model.js');
const FavoriteMenu = require('web.FavoriteMenu');
const FilterMenu = require('web.FilterMenu');
const GroupByMenu = require('web.GroupByMenu');
const patchMixin = require('web.patchMixin');
const Pager = require('web.Pager');
const SearchBar = require('web.SearchBar');
const { useModel } = require('web/static/src/js/model.js');

const { Component, hooks } = owl;

var concurrency = require('web.concurrency');
var config = require('web.config');
var field_utils = require('web.field_utils');
var time = require('web.time');
var utils = require('web.utils');
var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var Dialog = require('web.Dialog');
var field_utils = require('web.field_utils');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');
var abstractView = require('web.AbstractView');
var _t = core._t;
var QWeb = core.qweb;

const { useRef, useSubEnv } = hooks;

var HrDashboard = AbstractAction.extend({

    template: 'HrDashboardMain',
    cssLibs: [
        '/store_sales_dashboard/static/src/css/lib/nv.d3.css'
    ],
    jsLibs: [
        '/store_sales_dashboard/static/src/js/lib/d3.min.js'
    ],

     events: {
             'change .date_change_dashboard':'date_change_dashboard',
             'change #itemSearch':'date_change_dashboard',
             'change .date_change_start_order_type':'date_change_dashboard_order_type',
             'change .date_change_end_order_type':'date_change_dashboard_order_type',
             'change .date_change_start_top_selling':'date_change_top_selling',
             'change .date_change_end_top_selling':'date_change_top_selling',
             'change .date_change_start_top_paired':'date_change_top_paired',
             'change .date_change_end_top_paired':'date_change_top_paired',
             'change .date_change_start_optional':'get_optional_product_change_date',
             'change .date_change_end_top_optional':'get_optional_product_change_date',
             'change .date_change_start_top_selling_channel':'date_change_top_selling_channel',
             'change .date_change_end_top_selling_channel':'date_change_top_selling_channel',
             'change .date_change_start_service_speed':'date_change_service_speed',
             'change .date_change_end_service_speed':'date_change_service_speed',
             'change .time_interval_change_service_speed':'date_change_service_speed',
             'change .get_company_ids':'get_company_ids_change',
        },

    init: function(parent, context) {

        this._super(parent, context);
        this.date_range = 'week';  // possible values : 'week', 'month', year'
        this.date_from = moment().subtract(1, 'week');
        this.date_to = moment();
        this.dashboards_templates = ['StoreSalesData'];
        this.employee_birthday = [];
        this.upcoming_events = [];
        this.announcements = [];
        this.login_employee = [];

    },

    get_company_ids_change: function(){
        var self = this;
        var date_val = $('.date_change_dashboard').val();
        var company_ids = $('#itemSearch').val();
        if (company_ids){
            console.log('s')
        }
        else{
             var date_change =  this._rpc({
                model: 'sale.order',
                method: 'get_company_ids',
                }).then(function(result) {
                if (result){
                self.login_employee =  result;
                    $.when(self.render_template(result)).then(function() {
                        var li = []
                        _.each(result['company_ids'],function(items){
                            var d = {
                                'id': items['id'],
                                'text': items['name']
                            }
                            li.push(d);
                        });
                        $('#itemSearch').select2({
                            tags : true,
                            width: '100%',
                            allowClear: true,
                            multiple: true,
                            data: li,
                            });
                    });
                }
            });
        }
    },
    willStart: function(){
            var self = this;
            this.login_employee = {};
            return this._super()
            .then(function() {
                var def0 =  self._rpc({
                        model: 'sale.order',
                        method: 'get_user_employee_details'
                }).then(function(result) {
                    self.login_employee =  result;
                });

            var def2 =  self._rpc({
            model: 'sale.order',
            method: 'get_order_report_values'
            }).then(function(result) {
                self.order_type =  result;
            });

            var def3 =  self._rpc({
            model: 'sale.order',
            method: 'get_top_selling_values'
            }).then(function(result) {
                self.top_selling =  result;
            });
            var def4 =  self._rpc({
            model: 'sale.order',
            method: 'get_top_paired_today'
            }).then(function(result) {
                self.PairedProducts =  result;
            });
            var def5 =  self._rpc({
            model: 'sale.order',
            method: 'get_optional_product'
            }).then(function(result) {
                self.optional_product =  result;
            });
            var def6 =  self._rpc({
            model: 'sale.order',
            method: 'get_top_selling_channel_mix'
            }).then(function(result) {
            self.top_selling_channel =  result;
             });

             var def7 =  self._rpc({
             model: 'sale.order',
             method: 'get_service_speed'
             }).then(function(result) {
             self.service_speed =  result;
             });

        return $.when(def0,def2,def3,def4,def5,def6,def7);


        });
    },


    start: function() {
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.update_cp();
                self.render_dashboards();
                self.render_graphs();
                self.$el.parent().addClass('oe_background_grey');
            });
        },

    fetch_data: function() {
        var self = this;
        var def1 =  this._rpc({
                model: 'hr.employee',
                method: 'get_user_employee_details'
        }).then(function(result) {
            self.login_employee =  result;
        });

        return $.when(def1);
    },


    render_dashboards: function() {
        var self = this;
        if (this.login_employee){
            var restaurant_data = this.login_employee
            var order_type = this.order_type;
            var templates = []
            var date_change =  this._rpc({
                model: 'sale.order',
                method: 'get_company_ids',
            }).then(function(result) {
//                self.init_render(restaurant_data,result);
                $.when(self.init_render(restaurant_data,result)).then(function() {
                        var li = []
                        _.each(result['company_ids'],function(items){
                            var d = {
                                'id': items['id'],
                                'text': items['name']
                            }
                            li.push(d);
                        });
                        $('#itemSearch').select2({
                            tags : true,
                            width: '100%',
                            allowClear: true,
                            multiple: true,
                            data: li,
                        });
                })
            });

//            var template = 'StoreSalesData';
//            self.$('.o_hr_dashboard').append(QWeb.render(template, {widget: restaurant_data}));
        }
//         init_render: function(restaurant_data,result) {
//             var self = this;
//             var template = 'StoreSalesData';
//             self.$('.o_hr_dashboard').append(QWeb.render(template, {widget: restaurant_data}));
//             return true
//         },
         if (this.dashboards_templates){
            var restaurant_data = this.login_employee

            var login_employee = this.login_employee
            self.$('.o_hr_dashboard').append(QWeb.render('StoreSalesData', {widget: login_employee}));
         }
        if (this.order_type){
            var restaurant_data = this.login_employee
            var order_type = this.order_type;
            self.$('.o_hr_dashboard').append(QWeb.render('OrderTypeReport', {widget: order_type}));
        }
        if (this.top_selling){
            var restaurant_data = this.top_selling
            var top_selling = this.top_selling;
            self.$('.o_hr_dashboard').append(QWeb.render('TopSoldProduct', {widget: top_selling}));
        }
        if (this.top_selling_channel){
             var restaurant_data = this.top_selling_channel
             var top_selling_channel = this.top_selling_channel;
             self.$('.o_hr_dashboard').append(QWeb.render('TopSoldProductChannel', {widget: top_selling_channel}));
        }


        if (this.service_speed){
            var restaurant_data = this.service_speed
            var service_speed = this.service_speed;
            self.$('.o_hr_dashboard').append(QWeb.render('ServiceSpeed', {widget: service_speed}));
                }


        if(this.PairedProducts){
                self.$('.o_hr_dashboard').append(QWeb.render('PairedProducts', {widget: this.PairedProducts}));
        }
        if(this.optional_product){
            self.$('.o_hr_dashboard').append(QWeb.render('OptionalProducts', {widget: this.optional_product}));
        }
     },





    render_graphs: function(){
        var self = this;
        if (this.login_employee){
        }
    },
    init_render: function(restaurant_data,result) {
        var self = this;
        var template = 'StoreSalesData';

        return true
    },
    get_company_ids: function(){
        console.log("mani")
        var date_change =  this._rpc({
                model: 'sale.order',
                method: 'get_company_ids',
        }).then(function(result) {
            if (result){
            self.login_employee =  result;
                $.when(self.render_template(result)).then(function() {
                    var li = []
                    _.each(result['company_ids'],function(items){
                        var d = {
                            'id': items['id'],
                            'text': items['name']
                        }
                        li.push(d);
                    });
                    $('#itemSearch').select2({
                        tags : true,
                        width: '100%',
                        allowClear: true,
                        multiple: true,
                        data: li,
                        });
                });
            }
        });

    },

    date_change_dashboard: function(){
        var self = this;
        var date_val = $('.date_change_dashboard').val();
        var company_ids = $('#itemSearch').val();
        if (date_val && company_ids)  {
            var date_change =  this._rpc({
                    model: 'sale.order',
                    method: 'change_date_dashboard',
                    args: [date_val,company_ids]
            }).then(function(result) {
                if (result){
                self.login_employee =  result;
                    $.when(self.render_template(result)).then(function() {
                        var li = []
                        _.each(result['company_ids'],function(items){
                                var d = {
                                'id': items['id'],
                                'text': items['name']
                            }
                            li.push(d);
                        });

                        $('#itemSearch').select2({
                            tags : true,
                            width: '100%',
                            allowClear: true,
                            multiple: true,
                            data: li,
                            });
//                            $("#itemSearch").val(company_ids).trigger("change");
                    });
                    $('#itemSearch').val(company_ids);
                }
            });

        }

    },
    render_template: function (result){
        var self = this;
        var templates = []
        var template = 'StoreSalesData';
                self.$('.store-sales').empty();
                self.$('.store-sales').append(QWeb.render(template, {widget: result}));
                console.log("info")
                return true
    },

    date_change_dashboard_order_type: function(){
        var self = this;
        var date_val_start = $('.date_change_start_order_type').val();
        var date_val_end = $('.date_change_end_order_type').val();
        if (date_val_start && date_val_end){
           var date_change =  this._rpc({
                model: 'sale.order',
                method: 'get_order_report_change_date',
                args: [date_val_start,date_val_end]
                }).then(function(result) {
                    self.order_type =  result;
                    var templates = []
                    var template = 'OrderTypeReport';
                        self.$('.order-type').empty();
                        self.$('.order-type').append(QWeb.render(template, {widget: result}));
                });
        }
    },

    date_change_top_selling: function(){
        var self = this;
        var date_val_start = $('.date_change_start_top_selling').val();
        var date_val_end = $('.date_change_end_top_selling').val();
        if (date_val_start && date_val_end){
           var date_change =  this._rpc({
                model: 'sale.order',
                method: 'get_top_selling_values_date_change',
                args: [date_val_start,date_val_end]
                }).then(function(result) {
                    self.order_type =  result;
                    var templates = []
                    var template = 'TopSoldProduct';
                        self.$('.top-sold').empty();
                        self.$('.top-sold').append(QWeb.render(template, {widget: result}));
                });
        }

    },
    date_change_top_selling_channel: function(){
                var self = this;
                var date_val_start = $('.date_change_start_top_selling_channel').val();
                var date_val_end = $('.date_change_end_top_selling_channel').val();
                if (date_val_start && date_val_end){
                   var date_change =  this._rpc({
                        model: 'sale.order',
                        method: 'get_top_selling_values_date_change_channel',
                        args: [date_val_start,date_val_end]
                        }).then(function(result) {
                            self.order_type =  result;
                            var templates = []
                            var template = 'TopSoldProductChannel';
                                self.$('.top-channel').empty();
                                self.$('.top-channel').append(QWeb.render(template, {widget: result}));
                        });
                }

            },

    date_change_service_speed: function(){
                var self = this;
                var date_val_start = $('.date_change_start_service_speed').val();
                var date_val_end = $('.date_change_end_service_speed').val();
                var time_interval = $('.time_interval_change_service_speed').val();
                if (date_val_start && date_val_end && time_interval){
                   var date_change =  this._rpc({
                        model: 'sale.order',
                        method: 'get_service_speed_date_change',
                        args: [date_val_start,date_val_end,time_interval]
                        }).then(function(result) {
                            self.order_type =  result;
                            var templates = []
                            var template = 'ServiceSpeed';
                                self.$('.service_speed').empty();
                                self.$('.service_speed').append(QWeb.render(template, {widget: result}));
                        });
                }

            },





    date_change_top_paired: function(){
        var self = this;
        var date_val_start = $('.date_change_start_top_paired').val();
        var date_val_end = $('.date_change_end_top_paired').val();
        if (date_val_start && date_val_end){
           var date_change =  this._rpc({
                model: 'sale.order',
                method: 'get_top_paired',
                args: [date_val_start,date_val_end]
                }).then(function(result) {
                    self.paired_product =  result;
                    var templates = []
                    var template = 'PairedProducts';
                        self.$('.top-paired').empty();
                        self.$('.top-paired').append(QWeb.render(template, {widget: result}));
                });
        }

    },
     get_optional_product_change_date: function(){
        var self = this;
        var date_val_start = $('.date_change_start_optional').val();
        var date_val_end = $('.date_change_end_top_optional').val();
        if (date_val_start && date_val_end){
           var date_change =  this._rpc({
                model: 'sale.order',
                method: 'get_optional_product_change_date',
                args: [date_val_start,date_val_end]
                }).then(function(result) {
                    self.optional_product =  result;
                    var templates = []
                    var template = 'OptionalProducts';
                        self.$('.optional-products').empty();
                        self.$('.optional-products').append(QWeb.render(template, {widget: result}));
                });
        }

    },

    on_reverse_breadcrumb: function() {
        var self = this;
        web_client.do_push_state({});
        this.update_cp();
        this.fetch_data().then(function() {
            self.$('.o_hr_dashboard').empty();
            self.render_dashboards();
            self.render_graphs();
        });
    },

    update_cp: function() {
        var self = this;
    },

   });

    core.action_registry.add('hr_dashboard', HrDashboard);

return HrDashboard;

});