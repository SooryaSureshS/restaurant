odoo.define('gio_obstgemuese_theme.obst_appointment', function (require) {
    'use strict';

    var PublicWidget = require('web.public.widget')
    var ajax = require("web.ajax");
    var core = require('web.core');

    PublicWidget.registry.appointment = PublicWidget.Widget.extend({
        /**
         * jQuery selector for the element.
         * @property {String} selector
         */
        selector: "#wrapwrap",
        /**
         * The events this widget listens to.
         * @property {Object} events
         */
        events: {
            'change .filter_select_category_appointment': '_OnchangeAppointmentSelection',
            'change .filter_select_appointment_day': '_OnchangeAppointmentDatetimeSelection',
            'click .obst-previous-calender': '_onClickCalendarNavigate',
            'click .reservation-submit-btn': '_appointment_submit',
            'focus input, textarea': '_input_focus_function',
        },
        /**
         * OnchangeAppointmentSelection is a JavaScript function that changes the appointment form based on the selected form type.
         * @param {Object} ev - Event object that contains information about the user's action (e.g., clicking a button).
         * @function
         */
        _OnchangeAppointmentSelection: function (ev) {
            var form_id = $(ev.target).val()
            window.location.href = '/book-us?form_id=' + form_id
        },
        /**
         * Handles the change event for the appointment datetime selection.
         *
         * Parses the selected appointment value and sets the values for
         * `employee_id`, `datetime_str`, and `duration_str` in the
         * corresponding HTML elements.
         *
         * @param {Object} ev - The change event object.
         */
        _OnchangeAppointmentDatetimeSelection: function (ev) {
            var appointment_val = JSON.parse($(ev.target).val())
            $('#employee_id').val(appointment_val['employee_id'])
            $('#datetime_str').val(appointment_val['datetime'])
            $('#duration_str').val(appointment_val['duration'])
        },
        /**
         * Handles the click event for the calendar navigation.
         *
         * Retrieves the currently displayed month, performs the navigation
         * action based on the `action` attribute of the clicked element,
         * and displays the next or previous month if it exists.
         *
         * @param {Object} ev - The click event object.
         */
        _onClickCalendarNavigate: function (ev) {
            var parent = this.$('.o_appointment_month:not(.d-none)');
            var action = $(ev.target).attr('action')
            let monthID = parseInt(parent.attr('id').split('-')[1]);
            monthID += parseInt(action);
            if ($(`div#month-${monthID}`).length == 1) {
                parent.addClass('d-none');
                this.$(`div#month-${monthID}`).removeClass('d-none');
            }

        },
        /**
         * Adds the `was-validated` class to the form element.
         *
         * This is used to apply bootstrap styling to show validation errors
         * when the input elements in the form receive focus.
         */
        _input_focus_function: function () {
            $('form').addClass('was-validated')
        },
        /**
         * Handles the appointment submission process.
         *
         * Validates the input fields in the form and displays error messages
         * for any unfilled fields. If all fields are filled, triggers a click
         * event for the `reservation-submit-btn-actl` element to submit the
         * form data.
         *
         * Additionally, a pop-up is displayed if the appointment date has not
         * been selected from the calendar.
         */
        _appointment_submit: function () {
            var csrf_token = core.csrf_token
            var input_form = $('.form-control')
            var appointment_type = $('#appointment_type').val()
            var input_count = 0
            var calender_lis = ['employee_id', 'duration_str', 'datetime_str']
            var unfilled_fields = []
            var is_date_selected
            var val_dict = {}
            $('.website_form_field_valid').css({
                'display': 'none'
            })
            _.each(input_form, function (value) {
                if ($(value).val().length <= 0) {
                    input_count += 1
                    unfilled_fields.push($(value).attr('name'))
                    $(value).next('.website_form_field_valid').css({
                        'display': 'block'
                    })
                }
            });
            _.each(unfilled_fields, function (value) {
                if (calender_lis.includes(value)) {
                    is_date_selected = true
                }
            });
            if (is_date_selected) {
                var html = $('#wrapwrap').last()
                var head = 'Date Not Selected'
                var text = 'Select Appointment Date from Calendar'
                html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>" + head + "</h1><p>" + text + "</p></div></div>")
                setTimeout(function () {
                    $('#ob_portal_pop_up').delay(1000).remove();
                }, 1000);
            }
            if (input_count == 0) {
                $('.reservation-submit-btn-actl').click();
            }
        },
    });
})