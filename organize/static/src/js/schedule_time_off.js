odoo.define('organize.slot_discard_button', function (require) {
"use strict";

var BasicController = require('web.BasicController');
var core = require('web.core');
var Dialog = require('web.Dialog');
var dialogs = require('web.view_dialogs');
var FormControllers = require('web.FormController');

var _t = core._t;
var qweb = core.qweb;
var rpc = require('web.rpc');
var Dialog = require('web.Dialog');
var QWeb = core.qweb;

FormControllers.include({
    _onButtonClicked: function (ev) {
        // stop the event's propagation as a form controller might have other
        // form controllers in its descendants (e.g. in a FormViewDialog)
        ev.stopPropagation();
        var self = this;
        this._super.apply(this, arguments);
        var attrs = ev.data.attrs;
        if(attrs.name == "organize_discard"){
            window.location.reload();
        }
    },
    });
});