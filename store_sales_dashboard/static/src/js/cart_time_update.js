odoo.define('store_sales_dashboard.cart_time_update', function(require) {
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

var models = require('point_of_sale.models');
var PosDB = require("point_of_sale.DB");


	var posorders_super = models.Order.prototype;
	models.Order = models.Order.extend({

		initialize: function(attr,options) {
			var self = this;
			this.order_set_time = false;
			posorders_super.initialize.call(this,attr,options);
		},

		export_as_JSON: function(){
			var loaded = posorders_super.export_as_JSON.apply(this, arguments);
			loaded.order_set_time = this.order_set_time
			return loaded;
		},

		init_from_JSON: function(json){
			posorders_super.init_from_JSON.apply(this,arguments);
			this.order_set_time = json.order_set_time
		},

		add_product: function(product, options){
		    posorders_super.add_product.apply(this, arguments);
            if(this.order_set_time == false) {
               this.order_set_time = new Date().toLocaleString("sv-SE");
               console.log(this.order_set_time)
            }
        },

	});
});