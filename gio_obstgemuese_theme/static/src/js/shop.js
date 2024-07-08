odoo.define('gio_obstgemuese_theme.shop', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var PortalSidebar = require('portal.PortalSidebar');
    var ajax = require("web.ajax");
    var core = require('web.core');
    /**
     * shop Widget
     *
     * Extends publicWidget.Widget to provide a custom widget for shop pages in the gio_obstgemuese_theme.
     *
     * @class
     * @property {string} selector - The selector of the HTML element to bind the widget to
     * @property {Object} events - Event handlers for changes in form inputs and click events
     */
    publicWidget.registry.shop = publicWidget.Widget.extend({
        selector: '#wrapwrap',
        events: {
            'change form.js_attributes input, form.js_attributes select': '_onChangeAttribute',
            'change .custom-sort-select': '_onChangeSortSelect',
            'change .filter_select_category': '_onChangeFilterSelectCategory',
            'click .obst_mob_dots': '_onClickOpenFilter',
            'click .filter_use': '_onClickFilterUse',
            'click .filter-multi-select-sortiment': '_onClickDropDownSelection',
            'click .sidebar-filter-toggle': '_onClickOpenMobileMenu',
            'click .menu-box-close': '_onClickCloseMenuBox',
        },
        /**
         * start
         *
         * Initializes the shop widget and sets styles for different paths
         */
        start: function () {
            var path_name = window.location.href
            $('.o_carousel_product_indicators').css({
                'display': 'none'
            })
            $('.carousel-indicators').css({
                'display': 'none'
            })
            if (path_name.includes('category') || path_name.includes('shop?search')) {
                var select_val = parseInt((path_name.split('/')[3]).split('-')[1])
                $('.filter_select_category').val(select_val)
                $('.sort_reset_filter').css({
                    'display': 'block'
                })
                $('.filter-reset-all-products').removeClass('d-none')
                $('.mobile-reset-button').removeClass('d-none')
                $('.filter-reset-all-products').addClass('show')
                $('.mobile-reset-button').addClass('show')
            }
            if (path_name.includes('shop')) {
                $('.o_carousel_product_indicators').css({
                    'display': 'none'
                })
                $('.carousel-indicators').css({
                    'display': 'none'
                })
            }
        },
        _onClickOpenMobileMenu: function(ev){
            $('.menu-box-container').addClass('toggle_active');
            $('#wrapwrap').css('overflow-y', 'hidden')
            $('.sidebar-filter-toggle').css({'display': 'none'})
            $('.navbar').fadeIn(250)
            $('.chat-box-ui-block').fadeIn(250)
            if ($(window).width() < 750) {
                $('.menu-box-container').animate({
                    left: '0%'
                }, 250);
            } else {
                $('.menu-box-container').animate({
                    left: '67%'
                }, 250);
            }
        },
        _onClickCloseMenuBox: function () {
            $('.menu-box-container').animate({
                left: '110%'
            }, 250);
            $('.menu-box-container').removeClass('toggle_active');
            $('.chat-box-ui-block').fadeOut(250)
            $('.sidebar-filter-toggle').css({'display': 'block'})
            $('#wrapwrap').css('overflow-y', 'scroll')
        },
        /**
         * _onChangeAttribute
         *
         * Event handler for changes in form inputs
         *
         * @param {Event} ev - The change event
         */
        _onChangeAttribute: function (ev) {
            if (!ev.isDefaultPrevented()) {
                ev.preventDefault();
                if (ev.currentTarget.id  == 'CategoryFilter') {
                    window.location.href = $(ev.target).val()
                }else{
                    $(ev.currentTarget).closest("form").submit();
                }
            }
        },
        _onChangeSortSelect: function (ev){
            if (!ev.isDefaultPrevented()) {
                ev.preventDefault();
                window.location.href = $(ev.target).val()
            }
        },
        /**
         * _onChangeFilterSelectCategory
         *
         * Event handler for changes in the filter select category dropdown
         *
         * @param {Event} ev - The change event
         */
        _onChangeFilterSelectCategory: function (ev) {
            var id = $(ev.target).val()
            var name = $(".filter_select_category option:selected").text();
            var cat = name + '-' + id

            let host = location.host;
            var url = location.href
            if (url.includes('/shop')) {
                location.href = 'http://' + host + "/shop/category/" + cat
            }
            if (name == 'All Products') {
                location.href = 'http://' + host + '/shop'
            }
        },
        /**
         * Toggles the visibility of the obst_product_filter element.
         * Adds the "toggle_active" class to the element and sets the display property to "flex".
         * Animates the width of the element to 100%.
         */
//        _onClickOpenFilter: function () {
//            $('.obst_product_filter').addClass('toggle_active')
//            $('.obst_product_filter').css({
//                'display': 'flex'
//            })
//            $('.obst_product_filter').animate({
//                width: '100%'
//            }, 500);
//        },
        /**
         * Animates the width of the obst_product_filter element to 0% and sets its display property to "none" after a 450ms delay.
         * Removes the "toggle_active" class from the element.
         */
        _onClickFilterUse: function () {
            $('.obst_product_filter').animate({
                width: '0%'
            }, 500);
            setTimeout(function () {
                $('.obst_product_filter').css({
                    'display': 'none'
                })
            }, 450);
            $('.obst_product_filter').removeClass('toggle_active')
        },
    });
});

odoo.define('gio_obstgemuese_theme.custom_shop_mobile', function (require) {
    "use strict";
    var ajax = require("web.ajax");

    $(document).ready(function() {
        /*
         *Products filtering on mobile
         **/
        $('body').on('click', '.sidebar-filter-toggle, .sidebar-filter-close, .filter-search, .modal-backdrop-sidebar-filter', function(e) {
            $('.modal-backdrop.modal-backdrop-sidebar-filter').remove();
            if ($('.cms-block-sidebar-filter').hasClass('is-open')) {
                $('.modal-backdrop.modal-backdrop-sidebar-filter').removeClass('modal-backdrop-open');
                $('.cms-block-sidebar-filter').removeClass('is-open');
                $('.modal-backdrop.modal-backdrop-sidebar-filter').remove();
                $('html').removeClass('no-scroll');
            } else {
                $('body').append('<div class="modal-backdrop modal-backdrop-sidebar-filter"></div>');
                $('.cms-block-sidebar-filter').addClass('is-open');
                $('.modal-backdrop.modal-backdrop-sidebar-filter').addClass('modal-backdrop-open');
                $('html').addClass('no-scroll');
            }

            if (e.target.className === 'filter-search') {
                var currentSelection = $(".sorting.custom-select").val();
                var newSelection = $(".sorting-custom").val();
                if (currentSelection !== newSelection) {
                    $(location).attr('href', updateQueryStringParameter($(location).attr('href'), 'order', newSelection));
                }
            }

            e.preventDefault();
            e.stopPropagation();
        });

        function updateQueryStringParameter(uri, key, value) {
            var re = new RegExp("([?&])" + key + "=.*?(&|$)","i");
            var separator = uri.indexOf('?') !== -1 ? "&" : "?";
            return uri.match(re) ? uri.replace(re, '$1' + key + "=" + value + '$2') : uri + separator + key + "=" + value;
        }
    });
});