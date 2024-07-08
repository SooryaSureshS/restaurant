odoo.define('gio_obstgemuese_theme.header', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var PortalSidebar = require('portal.PortalSidebar');
    var ajax = require("web.ajax");
    var core = require('web.core');

    publicWidget.registry.header = publicWidget.Widget.extend({
    /**
     * jQuery selector for the element.
     * @property {String} selector
     */
        selector: '#wrapwrap',
     /**
     * The events this widget listens to.
     * @property {Object} events
     */
        events: {
            'click .close_icon': '_onClickClose',
            'click .navbar-toggler': '_onClickToggle',
            'click .ob_nav_search': '_onClickSearchPop',
            'click .ob_search_close': '_onClickSearchClose',
            'keyup .ob_search_input': '_onKeyUpSearch',
            'keydown .ob_search_input': '_onKeyDownSearch',
            'click .scroll_to_top': '_onclickScrollToTop',
            'click .ob_cart': 'async _onClickOpenCart',
            'click .ob-share-social': '_onClickSocialShare',
            'click .main-menu-section': '_onClickMainMenuSection',
            'keyup .header-search-input': '_onKeyUpSearchInputForm',
            'click .header-search-input': '_onClickSearchInputForm',
        },
        /**
         * This function toggles the 'toggle_active' class and makes the '.cart_container' element visible by adjusting its left position.
         * It also sets the overflow-y property of the '#wrapwrap' element to 'hidden', fades in the '.navbar' and '.cart-ui-block-container' elements, and calls the 'load_cart' function.
         * The left position of '.cart_container' is set to '0%' if the window width is less than 750px and to '67%' otherwise.
         *
         * @function
         */
        _onClickOpenCart: function () {
            $('.cart_container').addClass('toggle_active');
            $('#wrapwrap').css('overflow-y', 'hidden')
            $('.navbar').fadeIn(250)
            $('.cart-ui-block-container').fadeIn(250)
            this.load_cart()
            if ($(window).width() < 750) {
                $('.cart_container').animate({
                    left: '0%'
                }, 250);
            } else {
                $('.cart_container').animate({
                    left: '67%'
                }, 250);
            }
        },
        /**
         * load_cart is a function that fetches the cart details from the server through an AJAX JSON RPC call to the endpoint "/get/cart/values".
         * It then updates the UI elements with the cart details such as the item count, total amount, and the product details.
         * If the cart is empty, it displays a message and a button to redirect to the shop page.
         *
         * @function
         */
        load_cart: function () {
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
                        $('.offcanvas-cart-actions-summary').css({
                            'display': 'none'
                        })
                        $('.order_line').html('<div role="alert" class="alert alert-info cart-custom-alert"><div class="alert-content-container"><div class="alert-content"><font style="vertical-align: inherit;"><font style="vertical-align: inherit;"> Your shopping basket is empty. </font><font style="vertical-align: inherit;">Go ahead and fill it with products! </font></font><span class="close-alert"></span></div></div></div><a href="/shop" class="btn btn-secondary btn-center cart-secondary-btn"><font style="vertical-align: inherit;"><font class="" style="vertical-align: inherit;">Shopping now</font></font> </a>')
                    }
                });
        },
        /**
         * start - A function that styles the .navbar element with CSS attributes to make it fixed, with a transparent background, and a box shadow.
         *
         * The function also styles the .header-search-input element if it exists. The max-width is set to 66% and the width to the length of its value multiplied by 50 pixels.
         */
        start: function () {
            $('.navbar').css({
                'position': 'fixed',
                'background': 'none',
                'box-shadow': 'rgb(255 255 255 / 85%) -5px 128px 46px -69px inset'
            })
            $(".header-search-input").trigger("keyup");
        },
        /**
         * _onClickClose is a jQuery function that closes the overlay and animates the transition.
         *
         * The function sets the opacity of the close icon to 0 over 100 milliseconds,
         * animates the background color of the overlay to be fully transparent over 50 milliseconds,
         * and then reduces the width of the overlay and the top menu collapse to 0% over 250 milliseconds.
         * Finally, the function hides the overlay and removes the 'toggle_active' class.
         */
        _onClickClose: function () {
            $('.close_icon').animate({
                opacity: '0'
            }, 100);
            $('.overlay').animate({
                backgroundColor: "rgba(239,239,239,.0)"
            }, 50);
            $('.overlay').animate({
                width: '0%'
            }, 250);
            $('#top_menu_collapse').animate({
                width: '0%'
            }, 250);
            $('.overlay').hide(10)
            $('.overlay').removeClass('toggle_active')
        },
        /**
         * _onClickToggle is a jQuery function that animates the display of an overlay and the #top_menu_collapse element.
         * It makes the close_icon opaque, displays the overlay, changes its width to 100%, display to 'block' and background color to "rgba(239,239,239,.7)",
         * and adds the class 'toggle_active' to the overlay. The function also animates the width of #top_menu_collapse to 50% and its display to 'block'.
         */
        _onClickToggle: function () {
            $('.close_icon').animate({
                opacity: '1'
            }, 100);
            $('.overlay').show()
            $('.overlay').animate({
                width: '100%',
                display: 'block',
                backgroundColor: "rgba(239,239,239,.7)"
            }, 250);
            $('.overlay').addClass('toggle_active')
            $('#top_menu_collapse').animate({
                width: '50%',
                display: 'block'
            }, 250);
        },
        /**
         * _onClickSearchPop - Show the search overlay when the search icon is clicked.
         *
         * This function is triggered when the search icon is clicked and performs the
         * following actions:
         *   1. Show the '.ob_search_overlay' element.
         *   2. Animate the height of '.ob_search_overlay' to 100% and set its display to 'block'.
         *   3. Animate the opacity of '.ob_search_close' to 1.
         *   4. Add the class 'toggle_active' to '.ob_search_overlay'.
         */
        _onClickSearchPop: function () {
            $('.ob_search_overlay').show()
            $('.ob_search_overlay').animate({
                height: '100%',
                display: 'block'
            }, 500);
            $('.ob_search_close').animate({
                opacity: '1'
            }, 400);
            $('.ob_search_overlay').addClass('toggle_active')
        },
        /**
         * _onClickSearchClose is a jQuery function that is used to close the search overlay.
         *
         * This function animates the height of the `.ob_search_overlay` element to `0%` and then hides it with a delay of 10 milliseconds. It also removes the `toggle_active` class from the `.ob_search_overlay` element.
         */
        _onClickSearchClose: function () {
            $('.ob_search_overlay').animate({
                height: '0%'
            }, 500);
            $('.ob_search_overlay').hide(10)
            $('.ob_search_overlay').removeClass('toggle_active')

        },
        /**
         * Handles the behavior of the search input form on the key up event.
         *
         * @function
         * @param {Object} events - Event object containing the target element.
         *
         * The function sets the width and maximum width of the search input form
         * based on the length of the inputted value. It also toggles the visibility
         * of the search results page by hiding or displaying it based on whether
         * there is a value in the search input form.
         */
        _onKeyUpSearchInputForm: function (events) {
            var target = $(events.target)
            if (!target.val()) {
                target.css({
                    'max-width': '100%',
                    'width': '100%'
                })
                $('.search-results-page').css({
                    'display': 'none'
                })
            } else {
                var width_px = 50
                target.css({
                    'max-width': '66%',
                    'width': target.val().length * width_px + 'px'
                })
                $('.search-results-page').css({
                    'display': 'block'
                })
            }
        },
        /**
         * _onClickSearchInputForm - Show/hide the search results page based on the value entered in the search input form
         *
         * @param  {object} events - The click event triggered on the search input form
         *
         * This function performs the following actions:
         * 1. Retrieve the target element from the click event.
         * 2. If the target value is empty, then:
         *    a. Set the max-width and width of the target to 100%.
         *    b. Set the display of the `.search-results-page` element to 'none'.
         * 3. If the target value is not empty, then:
         *    a. Calculate the width of the target using the value length and a predefined width in pixels.
         *    b. Set the max-width of the target to 66% and its width to the calculated width.
         *    c. Set the display of the `.search-results-page` element to 'block'.
         */
        _onClickSearchInputForm: function (events) {
            var target = $(events.target)
            if (!target.val()) {
                target.css({
                    'max-width': '100%',
                    'width': '100%'
                })
                $('.search-results-page').css({
                    'display': 'none'
                })
            } else {
                var width_px = 50
                target.css({
                    'max-width': '66%',
                    'width': target.val().length * width_px + 'px'
                })
                $('.search-results-page').css({
                    'display': 'block'
                })
            }
        },
        /**
         *  _onKeyUpSearch is a jQuery function that is triggered when a key is pressed in the search input field.
         *  It checks if the key pressed is the "enter" key (keyCode 13), and if so, it retrieves the value of the input field
         *  and removes any existing product cards. The function then redirects the user to the search results page with the search keyword.
         *
         * @param {object} events - The event object containing information about the key event.
         */
        _onKeyUpSearch: function (events) {
            if (event.keyCode === 13) {
                var target = $(events.target)
                var search_key = target.val()
                $('.ob_product_card').remove()
                window.location.href = '/search/products?search=' + search_key
            }
        },
        /**
         * _onKeyDownSearch - This function is triggered when the search input form is clicked.
         *
         * @returns {void}
         */
        _onKeyDownSearch: function () {
            $('.ob_product_card').remove()
        },
        /**
         * _onclickScrollToTop - a function that animates the scrolling to the top of the page when called
         *
         * The function triggers a scroll animation to the top of the page (0 position on Y-axis)
         * with a duration of 400ms.
         */
        _onclickScrollToTop: function () {
            $('html,body').animate({
                scrollTop: 0
            }, 400);
            return false;
        },
        /**
         * Toggles the visibility of the `.social-media-list` element.
         * If the element is hidden, it will show. If it is visible, it will hide.
         */
        _onClickSocialShare: function () {
            var social_dict = {
                'none': 'block',
                'block': 'none'
            }
            $('.social-media-list').css({
                'display': social_dict[$(".social-media-list").css("display")]
            });
        },
        /**
         * _onClickMainMenuSection function is a jquery function that closes the main menu section when a target element with an id different from 'top_menu_collapse' is clicked.
         *
         * @function
         * @param {Object} ev - A jQuery event object that holds information about the click event.
         *
         * @return {void}
         */
        _onClickMainMenuSection: function (ev) {
            if ($(ev.target).attr('id') != 'top_menu_collapse') {
                this._onClickClose();
            }
        }
    });
});
