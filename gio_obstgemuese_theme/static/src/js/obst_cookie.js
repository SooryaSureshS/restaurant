odoo.define('gio_obstgemuese_theme.obst_cookie', function (require) {
    "use strict";
    var ajax = require("web.ajax");

    $(document).ready(function() {
        /*
         *Products filtering on mobile
         **/
         ajax.jsonRpc('/cookie/policy', 'call', {
                }).then(function (result) {
                if (result == 'No result'){
                    $('.cookie-permission-container').css({'display': 'block'})
                    console.log(result)
                }
            });

    });
});

odoo.define('gio_obstgemuese_theme.obst_cookie_policy', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var PortalSidebar = require('portal.PortalSidebar');
    var ajax = require("web.ajax");
    var core = require('web.core');
    publicWidget.registry.obst_cookie_policy = publicWidget.Widget.extend({

        selector: "#wrapwrap",
        /**
         * The events this widget listens to.
         * @property {Object} events
         */
        events: {
            'click .btn-accept-cookie': '_onClickAcceptCookie',
            'click .btn-close-cookie': '_onClickCloseCookie',
        },

        /**
         * Closes the cart container by animating it off the screen and
         * removing its active state.
         *
         * This function also hides the `cart-ui-block-container` element
         * and restores the `overflow-y` property of the `wrapwrap` element
         * to `scroll`.
         */
        _onClickAcceptCookie: function () {
            ajax.jsonRpc('/cookie/policy/accept', 'call', {
                }).then(function (result) {
                $('.cookie-permission-container').css({'display': 'none'})
                console.log(result)
            });
        },
        /**
         * Closes the cart container by animating it off the screen and
         * removing its active state.
         *
         * This function also hides the `cart-ui-block-container` element
         * and restores the `overflow-y` property of the `wrapwrap` element
         * to `scroll`.
         */
        _onClickCloseCookie: function () {
            $('.cookie-permission-container').css({'display': 'none'});
        },
    });
});