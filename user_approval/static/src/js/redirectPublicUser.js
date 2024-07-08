odoo.define('user_approval.redirectPublicUser', function (require) {
'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc')
    publicWidget.registry.PublicUserRedirection = publicWidget.Widget.extend({
        selector: '#wrapwrap',

        init: function () {
            $.blockUI();
            rpc.query({
                route: "/restrict-user",
                params: {'loc':window.location.pathname},
            }).then(function (data) {
                if (data) {
                    window.location.href = '/web/login'
                }
                setTimeout(function(){
                    $.unblockUI();
                    document.getElementById('wrapwrap').style.cssText = 'display:block !important';
                }, 500);
            });
            this._super.apply(this, arguments);
        },
    });
});
