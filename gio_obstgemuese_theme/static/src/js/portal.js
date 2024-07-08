odoo.define('gio_obstgemuese_theme.portal', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var PortalSidebar = require('portal.PortalSidebar');
    var ajax = require("web.ajax");
    var core = require('web.core');
    var newsletter = require('gio_obstgemuese_theme.newsletter');
    /**
     * Newsletter Subscribe widget
     * @class NewsletterSubscribe
     * @extends publicWidget.Widget
     */
    publicWidget.registry.portal = publicWidget.Widget.extend({
        /**
         * CSS selector for the widget
         * @property {String} selector
         */
        selector: '.ob_portal_wrap',
        /**
         * Dictionary of events to listen for and methods to trigger
         * @property {Object} read_events
         */
        events: {
            'click .ob_portal_tab_links': '_onClickOpenTab',
            'click .js_overview_check_newsletter': '_onClickOverviewNewClick',
            'click .js_show_order_line': '_onClickShowOrderLine',
            'click .profile_image_ob_add': '_onClickAddImage',
            'click .save_first_last_name_picture_submit': '_onClickSaveFl_name_picture',
            'change .ob_add_image': '_onChange_image',
            'click .ob_portal_pop_up_close': 'ob_portal_pop_up_close',
            'click .change_email': 'change_email_toggle',
            'click .change_password': 'change_password_toggle',
            'click .email_change_save': '_change_email_save',
            'click .password_change_save': '_change_password_save',
            'click .my_account_address_btn_edit': '_onClickMyAccountAddressEdit',
            'click .my_acct_add_btn_back': '_onClickMyAccountAddressBack',
            'click .add_shipping_address_btn': '_onClickMyAccountAddShippingAddress',
            'click .my_acct_shipping_add_btn_back': '_onClickMyAccountAddShippingAddressCancel',
            'click .my_acct_edit_billing_address_btn': '_onClickMyAccountEditBillingAddress',
            'click .my_account_shipping_address_update_cls': '_onClickMyAccountEditShippingAddress',
            'change select[name="country_id"]': '_onChangeCountry',
        },
        /**
         * Event handler for clicking on the "Overview New" checkbox.
         * Triggers the _onSubscribeClick function if the checkbox is checked.
         *
         * @param {Object} events - The event object associated with the click.
         */
        _onClickOverviewNewClick: function (events) {
            if ($(events.target).is(":checked")) {
                publicWidget.registry.newsletter_subscribe.prototype
                    ._onSubscribeClick()
            }
        },
        /**
         * Changes the password of the user.
         *
         * This function performs the following actions:
         * 1. Retrieves the current password, new password, and confirmed new password from the form fields
         * 2. Validates if all fields are filled and if the new password matches the confirmed password
         * 3. If the validation is successful, it sends a JSON-RPC call to `/change/password`
         * 4. If the password change was successful, it displays a success message and redirects to the login page.
         * 5. If the password change was unsuccessful, it displays an error message indicating the reason.
         *
         * @param {Object} this - A reference to the object that invokes the function.
         */
        _change_password_save: function () {
            var new_password = $('.new_password').val()
            var conf_password = $('.conf_new_password').val()
            var password = $('.curr_password_p').val()
            var html = $('#wrap').last()
            var head = "Validation Error"
            if (!new_password || !conf_password || !password) {
                var text = "fill up the fields"
                this.portal_pop_up(html, head, text)
            } else if (new_password != conf_password) {
                var text = "Password does not match"
                this.portal_pop_up(html, head, text)
            } else {
                ajax.jsonRpc('/change/password', 'call', {
                        conf_password,
                        password
                    })
                    .then((result) => {
                        if (result == 'change') {
                            var head = "Successful change"
                            var text = "Password has successfully changed"
                            this.portal_pop_up(html, head, text)
                            window.location.href = "/web/login"
                        } else if (result == 'nochange') {
                            var head = "Alert"
                            var text = "Password does not change please try again"
                            this.portal_pop_up(html, head, text)
                        } else if (result == 'error') {
                            var head = "Alert"
                            var text = "Incorrect Password, Please enter right password"
                            this.portal_pop_up(html, head, text)
                        }
                    });
            }
        },
        /**
         * change_email_save: function to change the email address.
         *
         * @param {event} events - The event which triggers the function.
         *
         * This function retrieves the new email address, confirmed new email address, and the current password from the input fields.
         * Then, it checks if the two email addresses match and if the email format is valid.
         * If the email format is invalid, a pop-up with a "Validation Error" header and "Enter correct email address" message appears.
         * If the fields are not filled, a pop-up with a "Validation Error" header and "fill up the fields" message appears.
         * If the two email addresses do not match, a pop-up with a "Validation Error" header and "E-mails does not match" message appears.
         * If the fields are filled and the email addresses match, an ajax call is made to the server with the confirmed email and password.
         * The server will return the result of the email change request which can be "exist", "change", "nochange", or "error".
         * Depending on the result, a pop-up with different header and message will appear.
         * If the email change is successful, the user will be redirected to the login page.
         */
        _change_email_save: function (events) {
            var new_email = $('.new_email').val()
            var conf_new_email = $('.conf_new_email').val()
            var password = $('.curr_password_e').val()
            var html = $('#wrap').last()
            var head = "Validation Error"
            if (this.email_validation(new_email) != true && this.email_validation(conf_new_email) != true) {
                var text = "Enter correct email address"
                this.portal_pop_up(html, head, text)
            } else if (!new_email || !conf_new_email || !password) {
                var text = "fill up the fields"
                this.portal_pop_up(html, head, text)
            } else if (new_email != conf_new_email) {
                var text = "E-mails does not match"
                this.portal_pop_up(html, head, text)
            } else {
                ajax.jsonRpc('/change/email', 'call', {
                    conf_new_email,
                    password
                }).then((result) => {
                    if (result == 'exist') {
                        var head = "Alert"
                        var text = "E-mail already exists"
                        this.portal_pop_up(html, head, text)
                    } else if (result == 'change') {
                        var head = "Successful change"
                        var text = "E-mail has successfully changed"
                        this.portal_pop_up(html, head, text)
                        window.location.href = "/web/login"
                    } else if (result == 'nochange') {
                        var head = "Alert"
                        var text = "E-mail does not change please try again"
                        this.portal_pop_up(html, head, text)
                    } else if (result == 'error') {
                        var head = "Alert"
                        var text = "Incorrect Password, Please enter right password"
                        this.portal_pop_up(html, head, text)
                    }
                });
            }
        },
        /**
         * Validate an email address.
         *
         * @param {string} val - The email address to be validated.
         * @returns {boolean} result - True if the email address is valid, False otherwise.
         */
        email_validation: function (val) {
            var pattern = new RegExp("^[_A-Za-z0-9-]+(\\.[_A-Za-z0-9-]+)*@[A-Za-z0-9]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})$");
            var result = pattern.test(val);
            return result
        },
        /**
         * Toggles display of the change password container and hides change email container.
         */
        change_password_toggle: function () {
            $('.change_password_container').toggle('slow');
            $('.change_email_container').hide('slow')
        },
        /**
         * Toggles display of the change email container and hides change password container.
         */
        change_email_toggle: function () {
            $('.change_email_container').toggle('slow');
            $('.change_password_container').hide('slow')
        },
        /**
         * Saves changes to first name, last name, and profile picture.
         */
        _onClickSaveFl_name_picture: function () {
            var first_name = $('#save_first_last_name_picture #first_name').val()
            var last_name = $('#save_first_last_name_picture #Surname').val()
            if ($('.profile_image_ob_add img').hasClass('is_changed')) {
                var image = $('.profile_image_ob_add img').attr('src')
                $('.profile_image_ob_add img').removeClass('is_changed')
            } else {
                var image = false;
            }
            ajax.jsonRpc('/account/save/Fl_name_picture', 'call', {
                first_name,
                last_name,
                image
            }).then((result) => {
                var html = $('#wrap').last()
                var head = "Successful change"
                var text = "You have successfully changed your name and profile picture."
                this.portal_pop_up(html, head, text)
            });
        },
        /**
         * Closes the portal pop up.
         */
        ob_portal_pop_up_close: function () {
            $('#ob_portal_pop_up').remove()
        },
        /*    custom pop up use anywhere*/
        /**
         * Displays a custom pop up with the given header and text.
         * @param {jQuery} html - The element to append the pop up to.
         * @param {string} head - The header text for the pop up.
         * @param {string} text - The body text for the pop up.
         */
        portal_pop_up: function (html, head, text) {
            html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>" + head + "</h1><p>" + text + "</p></div></div>")
        },
        /**
         * Changes the profile picture to the selected image.
         * @param {Event} events - The event that triggered this function.
         */
        _onChange_image: function (events) {
            var image = $(events.target)[0].files[0]
            var reader = new FileReader();
            $('.profile_image_ob_add img').addClass('is_changed');
            reader.onload = function () {
                var preview = $('.profile_image_ob_add img')
                var read_image = reader.result;
                preview.attr("src", read_image);
            }
            reader.readAsDataURL(image)
        },
        /**
         * Loads the given image and returns the Data URL
         * @param {File} image - The image file to load
         * @return {string} - The Data URL representation of the image
         */
        get_image: function (image) {
            var preview = $('.profile_image_ob_add img')
            var reader = new FileReader();
            reader.onload = function () {
                var read_image = reader.result;
                preview.src = read_image;
                return read_image
            }
            reader.readAsDataURL(image)
        },
        /**
         * Handles the click event on the "Add Image" button
         * @param {Event} events - The click event object
         */
        _onClickAddImage: function (events) {
            $('.ob_add_image').click()
        },
        /**
         * Handles the click event on the "Show/Hide Order Line" button
         * @param {Event} events - The click event object
         */
        _onClickShowOrderLine: function (events) {
            var order_id = $(events.target).attr('id')

            if ($('#orderid_' + order_id).is(':visible')) {
                $('#orderid_' + order_id).hide('slide')
                $(events.target).html('to show')
                $(events.target).css({
                    'color': 'black'
                })
            } else {
                $('#orderid_' + order_id).toggle('slow')
                $(events.target).html('hide')
                $(events.target).css({
                    'color': '#eeca00'
                })
            }
        },
        /**
         * Handles the start of the portal
         */
        start: function () {
            $("#defaultOpen").click();
        },
        /**
         * Handles the click event on the tab links
         * @param {Event} events - The click event object
         */
        _onClickOpenTab: function (events) {
            var tab_id = $(events.target).val()
            var i
            var tab_content = $(".tab_content");
            _.each(tab_content, function (tab_content) {
                tab_content.style.display = 'none'
            });
            $(".ob_portal_tab_links").removeClass('active')
            $('#' + tab_id).show()
            $('#' + tab_id).load(window.location.href + ' #' + tab_id);
            $(events.target).addClass('active')

        },
        /**
         * Handles the click event on the "Edit" button in the My Account page for a shipping address
         * @param {Event} ev - The click event object
         */
        _onClickMyAccountAddressEdit: function (ev) {
            var address_id = "#partner_address_" + $(ev.target).attr('id')
            $(address_id).css('display', 'block');
            $(ev.target).parents('.card-footer').css('display', 'none');
            $(ev.target).parents('.card-footer').prev().css('display', 'none');
        },
        /**
         * _onClickMyAccountAddressBack - function to handle the event of clicking the back button on an address edit form
         * @param {Object} ev - The event object
         * @returns {null}
         */

        _onClickMyAccountAddressBack: function (ev) {
            var address_id = "#partner_address_" + $(ev.target).attr('id')
            $(ev.target).parents().parents().parents(address_id).css('display', 'none');
            $(ev.target).parents().parents().parents(address_id).prev().children('.card').children('.card-body').css('display', 'block');
            $(ev.target).parents().parents().parents(address_id).prev().children('.card').children('.card-footer').css('display', 'block');
        },
        /**
         * _onClickMyAccountAddShippingAddress - function to handle the event of clicking the "Add Shipping Address" button
         *
         * @param {Object} ev - The event object
         *
         * @returns {null}
         */
        _onClickMyAccountAddShippingAddress: function (ev) {
            $('.add_shipping_address_cls').css('display', 'block');
            $("html, body").animate({
                scrollTop: $(document).height()
            }, 100);
        },
        /**
         * _onClickMyAccountAddShippingAddressCancel - function to handle the event of clicking the "Cancel" button on the add shipping address form
         *
         * @param {Object} ev - The event object
         *
         * @returns {null}
         */
        _onClickMyAccountAddShippingAddressCancel: function (ev) {
            $('.add_shipping_address_cls').css('display', 'none');
            $("html, body").animate({
                scrollTop: $(document).height()
            }, 100);
        },
        /**
         * _onClickMyAccountEditBillingAddress is a function that is triggered when clicking on an element with the class `kanban_billing_address_edit_cls`.
         * It gathers values from the input and select elements within the parent `form-group` of the target element.
         * The values are then stored in an object and sent as a JSON-RPC call to the URL "/my/account/address".
         * The result of the JSON-RPC call is used to display a pop-up message with the contents of `result.message` for 1 second.
         * If `result.status` is truthy, the class `bill_add_edit_back` will be triggered to click, and the contents of the `#registration` element will be reloaded.
         * If `result.status` is falsy, a pop-up message with the contents of `result.message` will be displayed for 1 second.
         *
         * @param {Object} events - The event object passed to the function.
         */
        _onClickMyAccountEditBillingAddress: function (events) {
            var parent_div_input = $(events.target).parents('.kanban_billing_address_edit_cls').children('.form-row').children('.form-group').children('input')
            var parent_div_select = $(events.target).parents('.kanban_billing_address_edit_cls').children('.form-row').children('.form-group').children('select')
            var value_dit = {}
            _.each(parent_div_input, function (value) {
                value_dit[$(value).attr('name')] = $(value).val()
            });
            _.each(parent_div_select, function (value) {
                value_dit[$(value).attr('name')] = $(value).val()
            });
            value_dit['mode'] = ['edit', 'billing']
            ajax.jsonRpc('/my/account/address', 'call', value_dit)
                .then(function (result) {
                    if (result.status) {
                        var html = $('#wrapwrap').last()
                        var head = result.message
                        var text = result.message
                        html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>" + head + "</h1><p>" + text + "</p></div></div>")
                        setTimeout(function () {
                            $('#ob_portal_pop_up').delay(1000).remove();
                        }, 1000);
                        $('.bill_add_edit_back').click();
                        $('#registration').load(window.location.href + ' #registration');
                    } else {
                        var html = $('#wrapwrap').last()
                        var head = result.message
                        var text = result.message
                        html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>" + head + "</h1><p>" + text + "</p></div></div>")
                        setTimeout(function () {
                            $('#ob_portal_pop_up').delay(1000).remove();
                        }, 1000);
                    }

                });
        },
        /**
        * The _onClickMyAccountEditShippingAddress function is used to edit the shipping address of a user's account.
        *
        * @param {Object} events - The events object contains the target element that triggered the function.
        *
        * This function retrieves the input values and select values from the target element's parent div with class `kanban_shipping_address_edit_cls`.
        * The values are stored in the `value_dit` object with the input/select name as the key and value as the value.
        * The mode is set to `edit` and `shipping`.
        *
        * An ajax call is then made to the "/my/account/address" endpoint with the `value_dit` object as an argument.
        *
        * If the result from the ajax call returns a success status, a pop up with the result message is displayed and the page reloads.
        * If the result from the ajax call returns an error, a pop up with the result message is displayed.
        */
        _onClickMyAccountEditShippingAddress: function (events) {
            var parent_div_input = $(events.target).parents('.kanban_shipping_address_edit_cls').children('.form-row').children('.form-group').children('input')
            var parent_div_select = $(events.target).parents('.kanban_shipping_address_edit_cls').children('.form-row').children('.form-group').children('select')
            var value_dit = {}
            _.each(parent_div_input, function (value) {
                value_dit[$(value).attr('name')] = $(value).val()
            });
            _.each(parent_div_select, function (value) {
                value_dit[$(value).attr('name')] = $(value).val()
            });
            value_dit['mode'] = ['edit', 'shipping']
            ajax.jsonRpc('/my/account/address', 'call', value_dit)
                .then(function (result) {
                    if (result.status) {
                        var html = $('#wrapwrap').last()
                        var head = result.message
                        var text = result.message
                        html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>" + head + "</h1><p>" + text + "</p></div></div>")
                        setTimeout(function () {
                            $('#ob_portal_pop_up').delay(1000).remove();
                        }, 1000);
                        $('.bill_add_edit_back').click();
                        $('#registration').load(window.location.href + ' #registration');
                    } else {
                        var html = $('#wrapwrap').last()
                        var head = result.message
                        var text = result.message
                        html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>" + head + "</h1><p>" + text + "</p></div></div>")
                        setTimeout(function () {
                            $('#ob_portal_pop_up').delay(1000).remove();
                        }, 1000);
                    }

                });
        },
        /**
         * Handles change event of the country select field.
         *
         * Makes an RPC request to retrieve the states associated with the selected country
         * and updates the state select field accordingly.
         *
         * @param {Object} ev - Event object triggered by the change event of the country select field.
         *
         * @return {undefined}
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
                var selectStates = $(ev.target).parent('.div_country').siblings('.div_state').children("select[name='state_id']");
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
