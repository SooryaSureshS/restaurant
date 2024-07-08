odoo.define('contact_filters.action_button', function (require) {
"use strict";
var core = require('web.core');
var ListController = require('web.ListController');
var rpc = require('web.rpc');
var session = require('web.session');
var _t = core._t;
var Dialog = require('web.Dialog');

ListController.include({
   renderButtons: function($node) {
       this._super.apply(this, arguments);
           if (this.$buttons) {
             this.$buttons.find('.oe_action_button_purchase').click(this.proxy('action_def_purchase')) ;

           }
   },
   action_def_purchase: function () {
            var self =this
            return self.do_action({name: _t('Purchase Filters'),
                                    type: 'ir.actions.act_window',
                                    res_model: 'purchase.filter.wizard',
                                    views: [[false, 'form']],
                                    view_mode: 'form',
                                    target: 'new',
                                    context: {default_product_specific_filter:true}
                                });
            },
   });
});