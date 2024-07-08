odoo.define('gio_obstgemuese_theme.cart', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var PortalSidebar = require('portal.PortalSidebar');
    var ajax = require("web.ajax");
    var core = require('web.core');

    publicWidget.registry.cart = publicWidget.Widget.extend({
        /**
         * jQuery selector for the element.
         * @property {String} selector
         */
        selector: '.cart_container',
        /**
         * The events this widget listens to.
         * @property {Object} events
         */
        events: {
            'click .cart_close': '_onClickCloseCart',
            'click .cart_trash': '_onClickCartTrash',
            'click .cart-ui-block-container': '_onClickCloseCartClose',
        },

        /**
         * Closes the cart container by animating it off the screen and
         * removing its active state.
         *
         * This function also hides the `cart-ui-block-container` element
         * and restores the `overflow-y` property of the `wrapwrap` element
         * to `scroll`.
         */
        _onClickCloseCart: function () {
            $('.cart_container').animate({
                left: '110%'
            }, 250);
            $('.cart_container').removeClass('toggle_active');
            $('.cart-ui-block-container').fadeOut(250)
            $('#wrapwrap').css('overflow-y', 'scroll')
        },
        /**
         * Closes the cart container by animating it off the screen and
         * removing its active state.
         *
         * This function also hides the `cart-ui-block-container` element
         * and restores the `overflow-y` property of the `wrapwrap` element
         * to `scroll`.
         */
        _onClickCloseCartClose: function () {
            $('.cart_container').animate({
                left: '110%'
            }, 250);
            $('.cart_container').removeClass('toggle_active');
            $('.cart-ui-block-container').fadeOut(250)
            $('#wrapwrap').css('overflow-y', 'scroll')
        },
        /**
         * onClickCartTrash is a jQuery function that removes a line item from the cart.
         *
         * @param {Event} ev - The click event that triggers the function.
         *
         * The function retrieves the line_id of the clicked item from the DOM,
         * and makes a JSON-RPC call to the `/remove/order/line` endpoint to remove the item.
         * If the call is successful, the function updates the cart summary and
         * removes the line item from the display.
         * If the cart becomes empty, the function updates the display to show
         * an empty cart message.
         */
        _onClickCartTrash: function (ev) {
            var line_id = $(ev.target).siblings('.line_id').val()
            var order_line = 'order_lines_' + line_id

            ajax.jsonRpc('/remove/order/line', 'call', {
                    'line_id': line_id
                })
                .then(function (result) {
                    if (result == true) {
                        ajax.jsonRpc('/get/cart/values', 'call', {})
                            .then(function (result) {
                                if (result.cart_item) {
                                    $('.item_count').html(result.values.length + ' items')
                                    $('.summary-total').text("CHF " + result.amount_total + ".-")
                                    $('.order_lines').remove()
                                    $('.offcanvas-cart-actions-summary').css({
                                        'display': 'block'
                                    })
                                    $('.cart-custom-alert').css({
                                        'display': 'none'
                                    })
                                    $('.cart-secondary-btn').css({
                                        'display': 'none'
                                    })
                                    _.each(result.values, function (result) {
                                        var attribute_val = []
                                        for (var key in result.variant) {
                                            var value = result.variant[key];
                                            attribute_val.push("<div class='col-md-12'><span><b>" + key + "</b>: " + value + "</span></div>")
                                        }
                                        var attr_str = attribute_val.join("")

                                        $('.order_line').append("<div class='col-md-12 order_lines order_lines_" + result.line_id + " pb-5'><div class='row'><div class='col-4'><img src='data:image/png;base64," + result.product_img + "' t-options='{'widget': 'image',}' width='100%'/></div><div class='col-6 p-0'><h4 class='GT_Pressura_Pro_Mono'>" + result.product_name + "</h4><h4 class='GT_Pressura_Pro_Mono'><span>" + result.symbol + "</span>" + result.price + "</h4>" + attr_str + "<div class='col-md-12'><span><b>Menge</b>: " + result.qty + "</span></div></div><div class='col-2'><img src='/gio_obstgemuese_theme/static/src/svg/08-trash2.svg' class='cart_trash'/><input type='hidden' value='" + result.line_id + "' class='line_id'></input></div></div></div>")
                                    });
                                } else {
                                    $('.order_line').css({
                                        'height': '100%'
                                    })
                                    $('.item_count').html('0 items')
                                    $('.offcanvas-cart-actions-summary').css({
                                        'display': 'none'
                                    })
                                    $('.order_line').html('<div role="alert" class="alert alert-info cart-custom-alert"><div class="alert-content-container"><div class="alert-content"><font style="vertical-align: inherit;"><font style="vertical-align: inherit;"> Your shopping basket is empty. </font><font style="vertical-align: inherit;">Go ahead and fill it with products! </font></font><span class="close-alert"></span></div></div></div><a href="/shop" class="btn btn-secondary btn-center cart-secondary-btn"><font style="vertical-align: inherit;"><font class="" style="vertical-align: inherit;">Shopping now</font></font> </a>')
                                }
                            });
                    }
                });
        },
    });
});
odoo.define('gio_obstgemuese_theme.website_sale_inherit', function (require) {
    'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var WebsiteSale = require('website_sale.website_sale');
    require('website_sale.website_sale');
    /**
     * Extends the _onClickAdd function of the WebsiteSale widget to also trigger the _onClickOpenCart function of the header widget after the original function is completed.
     *
     * @param {Event} ev - The click event that triggered the function
     * @returns {Promise} A promise that resolves when the original _onClickAdd function is completed and the _onClickOpenCart function of the header widget is triggered.
     */
    publicWidget.registry.WebsiteSale.include({
        async _onClickAdd(ev) {
            return this._super.apply(this, arguments).then(function () {
                publicWidget.registry.header.prototype._onClickOpenCart();
            });
        }
    });
});
