odoo.define('gio_obstgemuese_theme.product_detail_custom', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var PortalSidebar = require('portal.PortalSidebar');
var ajax = require("web.ajax");
var core = require('web.core');
var rpc = require('web.rpc');

publicWidget.registry.product_detail_custom = publicWidget.Widget.extend({
    selector: '.product-detail',
    events:{
        'change .js_variant_change':'_onClickVariantChange',
    },
    _onClickVariantChange:function(ev){

        },
    });
});