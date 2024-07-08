odoo.define('gio_obstgemuese_theme.login_register', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var PortalSidebar = require('portal.PortalSidebar');
    var ajax = require("web.ajax");
    var core = require('web.core');

    publicWidget.registry.login_register = publicWidget.Widget.extend({
    /**
     * jQuery selector for the element.
     * @property {String} selector
     */
        selector: '.oe_website_login_container',
     /**
     * The events this widget listens to.
     * @property {Object} events
     */
        events: {
            'click .del_add_checkbox_js': '_onClickCheckboxShowShipping',
            'click .log_reg_btn': '_onClickLogin',
            'focusout .login_input': '_onFocusOutLoginInputs',
            'focusout .reg_input': '_onFocusOutRegisterInputs',
            'keyup .login_input': '_onKeyupInputValidation',
            'keyup .reg_input': '_onKeyupRegInputValidation',
            'click .privacy_policy_js': '_onClickPrivacyPolicy',
            'change select[id="country_id"]': '_onChangeCountry',
        },
        /**
         * Start the widget.
         * @method start
         */
        start: function () {
            $('.obst_sign_up_js').attr('disabled', 'disabled');
        },
        /**
         * Handle the click event on the privacy policy checkbox.
         *
         * @param {jQuery.Event} events
         * @private
         */
        _onClickPrivacyPolicy: function (events) {
            if ($(events.target).is(':checked') == true) {
                $('.obst_sign_up_js').removeAttr('disabled');
            } else {
                $('.obst_sign_up_js').attr('disabled', 'disabled');
            }
        },
        /**
         * Handle the key up event on the login inputs.
         *
         * @param {jQuery.Event} events
         * @private
         */
        _onKeyupInputValidation: function (events) {
            var input_id = $(events.target).attr('id')
            var value = $(events.target).val()
            if (input_id == 'login') {
                var pattern = new RegExp("^[_A-Za-z0-9-]+(\\.[_A-Za-z0-9-]+)*@[A-Za-z0-9]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})$");
                var result = pattern.test(value);
                if (result == false) {
                    $(events.target).parents().children('.validation_error_email').html("Please enter a valid email address.")
                    $(events.target).css({
                        'border': '1px solid #eeca00'
                    })
                    $(events.target).siblings('.input_close').css({
                        'display': 'block'
                    })
                    $(events.target).siblings('.input_tick').css({
                        'display': 'none'
                    })
                } else {
                    $(events.target).css({
                        'border': '1px solid black'
                    })
                    $(events.target).parents().children('.validation_error_email').html("")
                    $(events.target).siblings('.input_close').css({
                        'display': 'none'
                    })
                    $(events.target).siblings('.input_tick').css({
                        'display': 'block'
                    })
                }

            }
            if (input_id == 'password') {
                if (value.length >= 8) {
                    $(events.target).css({
                        'border': '1px solid black'
                    })
                    $(events.target).parents().children('.validation_error_password').html("")
                    $(events.target).siblings('.input_close').css({
                        'display': 'none'
                    })
                    $(events.target).siblings('.input_tick').css({
                        'display': 'block'
                    })
                } else {
                    $(events.target).parents().children('.validation_error_password').html("password must contain 8 characters.")
                    $(events.target).css({
                        'border': '1px solid #eeca00'
                    })
                    $(events.target).siblings('.input_close').css({
                        'display': 'block'
                    })
                    $(events.target).siblings('.input_tick').css({
                        'display': 'none'
                    })
                }
            }
        },
        /**
         * Function to validate an input field on keyup event.
         *
         * @param {Object} events - The keyup event object.
         *
         * The function does the following:
         * 1. Retrieves the value of the input field that triggered the event.
         * 2. If the length of the value is greater than or equal to 1, the input field border is set to black and
         *    the error message and close icon are hidden, and the tick icon is displayed.
         * 3. If the length of the value is less than 1, the error message "Please fill up the field." is displayed,
         *    the input field border is set to yellow, and the close icon is displayed while the tick icon is hidden.
         */
        _onKeyupRegInputValidation: function (events) {
            var value = $(events.target).val()
            if (value.length >= 1) {
                $(events.target).css({
                    'border': '1px solid black'
                })
                $(events.target).parents().children('.validation_error').html("")
                $(events.target).siblings('.input_close').css({
                    'display': 'none'
                })
                $(events.target).siblings('.input_tick').css({
                    'display': 'block'
                })
            } else {
                $(events.target).parents().children('.validation_error').html("Please fill up the field.")
                $(events.target).css({
                    'border': '1px solid #eeca00'
                })
                $(events.target).siblings('.input_close').css({
                    'display': 'block'
                })
                $(events.target).siblings('.input_tick').css({
                    'display': 'none'
                })
            }
        },
        /**
         *  _onClickCheckboxShowShipping is a jQuery function that is used to toggle the visibility of the shipping address container
         *  when the checkbox is selected or deselected.
         *
         *  @param {Object} events - The event object triggered by the click event on the checkbox.
         *
         *  @return {undefined} This function does not return any value.
         */
        _onClickCheckboxShowShipping: function (events) {
            if ($(events.target).is(':checked') == true) {
                $('.shipping_address').toggle('slow')
            } else {
                $('.shipping_address').toggle('hide')
            }
        },
        /**
         * Function to handle the click event on login button
         *
         * @function
         * @private
         * @memberof module:index
         */
        _onClickLogin: function () {
            if ($('.rem_me_checkbox').is(':checked')) {

            }
        },
        /**
         * Function to handle the focus out event on the login inputs and style the input field if both inputs are empty.
         * @function
         * @param {Object} events - Event object from the focus out event on the input field.
         * @returns {null}
         */
        _onFocusOutLoginInputs: function (events) {
            if (!$('.login_input:first').val() && !$('.login_input:last').val()) {
                $('.login_input').css({
                    'border': '1px solid #eeca00'
                })
            }
        },
        /**
         * This function is used to handle the focus out event on register inputs and set appropriate border color
         * based on whether the input is empty or filled.
         *
         * @param {object} events - The event object generated by the focus out event on register inputs.
         *
         * @returns {undefined} Returns nothing.
         */
        _onFocusOutRegisterInputs: function (events) {
            if (!$('.reg_input').val()) {
                $('.reg_input').css({
                    'border': '1px solid #eeca00'
                })
            }
            if ($(events.target).val()) {
                $(events.target).css({
                    'border': '1px solid black'
                })
            } else {
                $(events.target).css({
                    'border': '1px solid #eeca00'
                })
            }
        },
        /**
         * _onChangeCountry is a function that handles the change event of a country select input.
         * The function makes an RPC request to the "/shop/country_info/" route with the selected country code as a parameter.
         * The response data is then used to populate the state select input and toggle its visibility based on the data received.
         *
         * @param {Event} ev - The change event object that triggered the function.
         */
        _onChangeCountry: function (ev) {
            if (!$(ev.target).val()) {
                return;
            }
            this._rpc({
                route: "/shop/country_info/" + $(ev.target).val(),
                params: {
                    mode: $(ev.target).attr('mode'),
                },
            }).then(function (data) {
                var selectStates = $(ev.target).parent('.div_country').siblings('.div_state').children("select[id='state_id']");
                if (data.states.length || data.state_required) {
                    selectStates.html('');
                    _.each(data.states, function (x) {
                        var opt = $('<option>').text(x[1])
                            .attr('value', x[0])
                            .attr('data-code', x[2]);
                        selectStates.append(opt);
                    });
                    selectStates.parent('div').show();
                } else {
                    selectStates.val('').parent('div').hide();
                }
                selectStates.data('init', 0);
            });
        },
    });
});