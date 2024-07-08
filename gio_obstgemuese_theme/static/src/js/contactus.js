odoo.define('gio_obstgemuese_theme.contactus', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var PortalSidebar = require('portal.PortalSidebar');
    var ajax = require("web.ajax");
    var core = require('web.core');
    var newsletter = require('gio_obstgemuese_theme.newsletter');

    var _t = core._t;
    var qweb = core.qweb;

    publicWidget.registry.contactus = publicWidget.Widget.extend({
    /**
     * jQuery selector for the element.
     * @property {String} selector
     */
        selector: '.contact_wrap',
    /**
     * The events this widget listens to.
     * @property {Object} events
     */
        events: {
            'click .send-contact-form-cls': '_contact_form_send_fn'
        },
        /**
         * start function initializes the map and sets the initMap function to window.
         *
         * @function
         * @name start
         *
         * @return {undefined}
         */
        start: function () {
            this.initMap()
            window.initMap = initMap;
        },
        /**
         * Initializes a Google Map centered at Uluru, Australia
         * with zoom level 12.
         *
         * The map is created using Google Maps API and is placed in a
         * HTML element with id "g_map".
         *
         * The map is configured with several options to remove certain controls,
         * including zoom control, map type control, scale control, street view control,
         * rotate control and full screen control.
         *
         * A marker is placed at the Uluru location.
         */
        initMap: function () {
            const uluru = {
                lat: -25.344,
                lng: 131.031
            };
            const map = new google.maps.Map(document.getElementById("g_map"), {
                zoom: 12,
                center: uluru,
                zoomControl: false,
                mapTypeControl: false,
                scaleControl: false,
                streetViewControl: false,
                rotateControl: false,
                fullscreenControl: false
            });
            const marker = new google.maps.Marker({
                position: uluru,
                map: map,
            });
        },
        /**
         * Sends the customer's contact form data to the server for processing.
         *
         * This function validates the input form fields, adds a class to the form,
         * and collects the form data in a dictionary.
         * If all fields are valid, the function sends an AJAX post request to the server
         * with the form data and displays a success message if the server response is positive.
         *
         * @param {Object} e - The event object triggered by the form submit action.
         */
        _contact_form_send_fn: function (e) {
            $('form').addClass('was-validated')
            var input_form = $('.s_website_form_input')
            var is_valid = 0
            _.each(input_form, function (value) {
                if ($(value).css('border-color') != 'rgb(0, 0, 0)') {
                    $(value).next('.website_form_field_valid').css({
                        'display': 'block'
                    })
                } else {
                    $(value).next('.website_form_field_valid').css({
                        'display': 'none'
                    })
                    is_valid = is_valid + 1
                }
            });
            if (is_valid == 4) {
                $('.send-contact-form-cls').addClass('disabled')
                var value_dit = {
                    'name': $('#CustomerName').val(),
                    'email_from': $('#CustomerEmail').val(),
                    'email_to': $('#contactDepartment').val(),
                    'description': $('#ContactMessage').val(),
                    'csrf_token': $('#CsrfToken').val()
                }
                ajax.post('/website/form/mail.mail', value_dit)
                    .then(function (result) {
                        if (result) {
                            $('.contact-form-section').css({
                                'display': 'none'
                            })
                            $('.contact-headline-hide-cls').css({
                                'display': 'none'
                            })
                            $('.contact-form-success-section').css({
                                'display': 'block'
                            })
                        }
                    });
            }
        },
    });
    /**
     * $(document).ready is a built-in jQuery function that is called when the DOM is fully loaded.
     *
     * This function is attached to the `ready` event in the document object.
     * Within the function, it sets tooltips for the tabs in the navigation and adds an event listener to the tabs to handle their behavior when switching.
     */
    $(document).ready(function () {
        $('.nav-tabs > li a[title]').tooltip();
        $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
            var target = $(e.target);
            if (target.parent().hasClass('disabled')) {
                return false;
            }
        });

    });
    /**
     * @function nextTab
     * @description This function triggers a click event on the next tab element.
     * @param {Element} elem The current tab element.
     */
    function nextTab(elem) {
        $(elem).next().find('a[data-toggle="tab"]').click();
    }
    /**
     *  prevTab function is a jQuery function that triggers a click event on the previous tab of the given element.
     *  @param {Object} elem The HTML element to start searching for the previous tab
     *  @returns {undefined} This function does not return anything
     */
    function prevTab(elem) {
        $(elem).prev().find('a[data-toggle="tab"]').click();
    }
    /**
     * The function is an event listener that adds the 'active' class to the clicked
     * tab element and removes it from the previously active tab.
     */
    $('.nav-tabs').on('click', 'li', function () {
        $('.nav-tabs li.active').removeClass('active');
        $(this).addClass('active');
    });
});