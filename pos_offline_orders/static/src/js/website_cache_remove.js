odoo.define('pos_offline_orders.website_cache_remove', function (require) {
    "use strict";

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;
    $(document).ready(function() {
        console.log("DDDDDD")
        ajax.jsonRpc('/clear/order', 'call', {"ready": 1}).then(function(res) {
            if(res === false){
                window.location.reload()
            }
            else{
                console.log("PPPPP")
            }
        });

    })
})