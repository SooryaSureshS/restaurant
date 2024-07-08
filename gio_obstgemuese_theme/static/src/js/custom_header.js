/**
 * Add the custom header code for the Gio Obstgemuese Theme
 *
 * This function listens for the page's scroll event and modifies the css of
 * the .navbar and .obst_product_filter_tab elements.
 *
 * Also listens for the end of the page and triggers an AJAX request to load
 * the next set of products.
 *
 * And sets up the carousel in the show-neighbors element to show the next
 * and previous items.
 *
 * @param {Object} require - RequireJS module
 * @returns {undefined}
 */
odoo.define('gio_obstgemuese_theme.custom_header_code', function (require) {
    "use strict";
    var ajax = require("web.ajax");

    $(document).ready(function (e) {
        /**
         * Store the last scroll top position
         *
         * @type {number}
         */
        var lastScrollTop = 0;
        /**
         * Scroll event listener for #wrapwrap
         *
         * Modifies the css of .navbar and .obst_product_filter_tab based on
         * the current scroll position and url.
         */
        $('#wrapwrap').scroll(function () {
            var height = $(this).scrollTop();
            var url = location.href
            if (height > lastScrollTop) {
                $('.navbar').css({
                    'position': 'absolute'
                })
                if (url.includes("/shop")) {
                    $('.obst_product_filter_tab').css({
                        'position': 'absolute'
                    })
                }
            } else {
                if (height < 1) {
                    $('.navbar').css({
                        'position': 'fixed',
                        'background': 'none',
                        'box-shadow': 'rgb(255 255 255 / 85%) -5px 128px 46px -69px inset !important'
                    })
                    if (url.includes("/shop")) {
                        $('.obst_product_filter_tab').css({
                            'position': 'fixed'
                        })
                    }
                } else {
                    $('.navbar').css({
                        'position': 'fixed',
                        'background': 'white'
                    })
                    if (url.includes("/shop")) {
                        $('.obst_product_filter_tab').css({
                            'position': 'fixed'
                        })
                    }
                }
            }
            lastScrollTop = height;
        });
        /**
         * Scroll event listener for #wrapwrap when on the /shop page
         *
         * Makes an AJAX request to load the next set of products when the
         * end of the page is reached.
         */
        $('#wrapwrap').scroll(function () {
            if (location.pathname.includes("/shop")) {
                if ($('tbody').length != 0) {
                    if ($(window).scrollTop() >= $('tbody').offset().top + $('tbody').outerHeight() - window.innerHeight) {
                        if ($('#page_limit').val() == 'false') {
                            if ($('#scroll_action').val() == 'true') {
                                var end_point
                                var website_location = location.pathname
                                var pagination = parseInt($('#website_pagination').val()) + 1
                                if (location.pathname.includes("/shop")) {
                                    var end_point = '/shop/pagination/';
                                }
                                if (location.pathname.includes("/shop/category")) {
                                    var path = location.pathname.split("/").pop();
                                    var end_point = '/shop/pagination_category/' + path + '/page/';
                                }
                                $('#scroll_action').val('false')
                                setTimeout(function () {
                                    ajax.jsonRpc(end_point + pagination.toString(), 'call', {})
                                        .then(function (result) {
                                            if (result.template_ok) {
                                                $('.table_body_shop').append(result.tr_lis)
                                                $('.table_body_shop_mobile').append(result.tr_lis_mobile)
                                                $('#website_pagination').val(pagination.toString())
                                                $('#website_current_url').val(website_location)
                                                $('#scroll_action').val('true')
                                            } else if (result.pagination_limit) {
                                                $('#product_pager_spinner').css({
                                                    'display': 'none'
                                                });
                                                $('.pagination-limit').css({
                                                    'display': 'block'
                                                });
                                                $('#page_limit').val('true')
                                            }
                                        });
                                }, 1000);
                            }
                        }
                    }
                }
            }
        });
        /**
         * This jQuery function manipulates the HTML elements with class `.carousel-item` and `.show-neighbors` to display their next and previous sibling elements.
         * If the next or previous sibling does not exist, it selects the first or last sibling respectively.
         * It then clones the first child of the next sibling and appends it to the current element.
         * Similarly, it clones the second last child of the previous sibling and prepends it to the current element.
         *
         * @return {undefined} This function does not return any value.
         */
        $('.carousel-item', '.show-neighbors').each(function () {
            var next = $(this).next();
            if (!next.length) {
                next = $(this).siblings(':first');
            }
            next.children(':first-child').clone().appendTo($(this));
        }).each(function () {
            var prev = $(this).prev();
            if (!prev.length) {
                prev = $(this).siblings(':last');
            }
            prev.children(':nth-last-child(2)').clone().prependTo($(this));
        });

    });
});