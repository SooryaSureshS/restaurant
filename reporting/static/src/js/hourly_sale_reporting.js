odoo.define('reporting.HSRDashboard', function (require) {
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

var HSRDashboard = AbstractAction.extend({

    template: 'HSRDashboard',
    cssLibs: [
        '/store_sales_dashboard/static/src/css/lib/nv.d3.css'
    ],
    jsLibs: [
        '/store_sales_dashboard/static/src/js/lib/d3.min.js'
    ],

     events: {
            'change .date_change_dashboard':'date_change_dashboard',
//             'change .get_company_ids':'get_company_ids_change',
        },

    init: function(parent, context) {

        this._super(parent, context);
        this.dashboards_templates = ['HourlySalesReport'];
        this.login_employee = [];

    },

    willStart: function(){
            var self = this;
            this.login_employee = {};
            return this._super().then(function() {
                var def0 =  self._rpc({
                        model: 'sale.order',
                        method: 'get_user_employee_details'
                }).then(function(result) {
                    self.login_employee =  result;
                });

        return $.when(def0);


        });
    },

    start: function() {
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.render_dashboards();
                self.$el.parent().addClass('oe_background_grey');
            });
        },

    render_dashboards: function() {
        var self = this;
        if (this.login_employee){
            var restaurant_data = this.login_employee
            var order_type = this.order_type;
            var templates = []
        if (this.dashboards_templates){
            var restaurant_data = this.login_employee
            var start_date_val = $('#select_start_date').val();
            var end_date_val = $('#select_end_date').val();
            var login_employee = this.login_employee
            this._rpc({
                model: 'sale.order',
                method: 'get_hourly_sales_data',
                args: [0,start_date_val,end_date_val]
            }).then(function(result) {
                self.$('.o_hr_dashboard').append(QWeb.render('HourlySalesReport', {widget: result}));
            });
        }
        }
    },

    init_render: function(restaurant_data,result) {
        var self = this;
        var template = 'StoreSalesData';
        return true
    },
    date_change_dashboard: function(){
        var self = this;
        var start_date_val = $('#select_start_date').val();
        var end_date_val = $('#select_end_date').val();
        var date_change =  this._rpc({
                model: 'sale.order',
                method: 'get_hourly_sales_data',
                args: [0,start_date_val,end_date_val]
            }).then(function(result) {
                self.render_template(result);
            });
    },

    render_template: function (result){
        var self = this;
        var templates = []
        var template = 'HourlySalesReport';
                self.$('.store-sales').empty();
                self.$('.store-sales').append(QWeb.render(template, {widget: result}));
                return true
    },
});

core.action_registry.add('hourly_sales_reporting', HSRDashboard);

return HSRDashboard;

});