/**
 * Registers the newsletter subscribe widget
 * @module gio_obstgemuese_theme.newsletter
 */
odoo.define('gio_obstgemuese_theme.newsletter', function (require) {
    "use strict";

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    const {
        ReCaptcha
    } = require('google_recaptcha.ReCaptchaV3');

    var _t = core._t;
    /**
     * Newsletter Subscribe widget
     * @class NewsletterSubscribe
     * @extends publicWidget.Widget
     */
    publicWidget.registry.newsletter_subscribe = publicWidget.Widget.extend({
         /**
         * CSS selector for the widget
         * @property {String} selector
         */
        selector: "#wrapwrap",
        /**
         * Specifies if widget is disabled in editable mode
         * @property {Boolean} disabledInEditableMode
         */
        disabledInEditableMode: false,
         /**
         * Dictionary of events to listen for and methods to trigger
         * @property {Object} read_events
         */
        read_events: {
            'click .js_subscribe_btn': '_onSubscribeClick',
        },
        /**
         * Initializes the widget
         * @method init
         */
        init: function () {
            this._super(...arguments);
            this._recaptcha = new ReCaptcha();
        },
         /**
         * Starts the widget
         * @method start
         * @return {Promise} Promise object representing the result of the operation
         */
        start: function () {
            if (['/ ', '/contactus', '/about', '/my/home', '/my', '/impressum'].includes(window.location.pathname)) {
                var def = this._super.apply(this, arguments);
                if (this.editableMode) {
                    // Since there is an editor option to choose whether "Thanks" button
                    // should be visible or not, we should not vary its visibility here.
                    return def;
                }
                const always = this._updateView.bind(this);
                return Promise.all([def, this._rpc({
                    route: '/website_mass_mailing/is_subscriber',
                    params: {
                        'list_id': 1,
                    },
                }).then(always).guardedCatch(always)]);
            }
        },
         /**
         * Updates the view based on the received data
         *
         * @method _updateView
         * @private
         * @param {Object} data Data received from the server
         */
        _updateView(data) {
            const isSubscriber = data.is_subscriber;
            const subscribeBtnEl = this.$target[0].querySelector('.js_subscribe_btn');
            const thanksBtnEl = this.$target[0].querySelector('.js_subscribed_btn');
            const emailInputEl = this.$target[0].querySelector('input.js_subscribe_email');

            subscribeBtnEl.disabled = isSubscriber;
            emailInputEl.value = data.email || '';
            emailInputEl.disabled = isSubscriber;
        },
        /**
         * Subscribes a user to a mailing list with their email address and selected preferences.
         * Checks if the entered email address is valid and if there's a recaptcha token available.
         * Displays a notification with the result of the subscription attempt.
         *
         * @function
         * @async
         */
        _onSubscribeClick: async function () {
            var self = this;
            var $email = this.$(".js_subscribe_email:visible");
            var cargobike = $('.cargobike_check').is(":checked")
            var performance = $('.performance_check').is(":checked")
            if ($email.length && !$email.val().match(/.+@.+/)) {
                this.$target.addClass('o_has_error').find('.form-control').addClass('is-invalid');
                return false;
            }
            this.$target.removeClass('o_has_error').find('.form-control').removeClass('is-invalid');
            const tokenObj = await this._recaptcha.getToken('website_mass_mailing_subscribe');
            if (tokenObj.error) {
                self.displayNotification({
                    type: 'danger',
                    title: _t("Error"),
                    message: tokenObj.error,
                    sticky: true,
                });
                return false;
            }
            this._rpc({
                route: '/website_mass_mailing/subscribe',
                params: {
                    'list_id': 1,
                    'cargobike': cargobike,
                    'performance': performance,
                    'email': $email.length ? $email.val() : false,
                    recaptcha_token_response: tokenObj.token,
                },
            }).then(function (result) {
                let toastType = result.toast_type;
                if (toastType === 'success') {
                    self.$(".js_subscribe_btn").prop('disabled', !!result);
                    self.$('input.js_subscribe_email').prop('disabled', !!result);
                    self.$('.js_newsletter_message').html('subscribed')
                    const $popup = self.$target.closest('.o_newsletter_modal');
                    if ($popup.length) {
                        $popup.modal('hide');
                    }
                }
                self.displayNotification({
                    type: toastType,
                    title: toastType === 'success' ? _t('Success') : _t('Error'),
                    message: result.toast_content,
                    sticky: true,
                });
            });
        },
    });
});
