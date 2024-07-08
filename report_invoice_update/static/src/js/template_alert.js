odoo.define('report_invoice_update', (require)=>{
"use strict";

    var ListView = require('web.ListView');
    var pyUtils = require('web.py_utils');

    ListView.include({

            init: function (viewInfo, params) {
                var self = this;
                this._super.apply(this, arguments);
                var pyevalContext = py.dict.fromJSON(_.pick(params.context, function(value, key, object) {return !_.isUndefined(value)}) || {});
                var expandGroups = !!JSON.parse(pyUtils.py_eval(this.arch.attrs.expand || "0", {'context': pyevalContext}));
                this.loadParams.limit = this.loadParams.limit || 300;
                this.loadParams.openGroupByDefault = expandGroups;
                var groupsLimit = parseInt(this.arch.attrs.groups_limit, 10);
                this.loadParams.groupsLimit = groupsLimit || (expandGroups ? 10 : 300);

                }

    });



});


