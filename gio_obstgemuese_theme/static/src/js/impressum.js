odoo.define('gio_obstgemuese_website.impressum', function (require) {
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    const dom = require('web.dom');
    var Dialog = require('web.Dialog');
    var utils = require('web.utils');
    var publicWidget = require('web.public.widget');
    const session = require('web.session');
    const {
        ReCaptcha
    } = require('google_recaptcha.ReCaptchaV3');

    var _t = core._t;

    publicWidget.registry.impressum = publicWidget.Widget.extend({
    /**
     * jQuery selector for the element.
     * @property {String} selector
     */
        selector: ".impressum-newsletter",
        disabledInEditableMode: false,
     /**
     * The events this widget listens to.
     * @property {Object} events
     */
        read_events: {
            'click .js_subscribe_mymail': '_onSubscribeClickMyMail',
        },
        /**
         * _onSubscribeClickMyMail is a jQuery function that is triggered when
         the user clicks the subscribe button.
         * It performs various operations such as validation of email address,
         recaptcha token verification,
         * and sending a request to the server to subscribe for a newsletter.
         *
         * @param {Object} this - refers to the current object context
         * @returns {Boolean} - returns false if the email address is invalid
         or the recaptcha token is not valid.
         */
        _onSubscribeClickMyMail: async function () {

            var self = this;
            var $email = this.$(".js_subscribe_email:visible");

            if ($email.length && !$email.val().match(/.+@.+/)) {
                this.$target.addClass('o_has_error').find('.form-control').addClass('is-invalid');
                self.displayNotification({
                    type: 'warning',
                    title: _t('Warning'),
                    message: "Invalid Email Address",
                    sticky: true,
                });
                return false;
            }
            this.$target.removeClass('o_has_error').find('.form-control').removeClass('is-invalid');
            if (this._recaptcha) {
                tokenObj = await this._recaptcha.getToken('website_mass_mailing_subscribe');
                if (tokenObj.error) {
                    self.displayNotification({
                        type: 'danger',
                        title: _t("Error"),
                        message: tokenObj.error,
                        sticky: true,
                    });
                    return false;
                }
            }
            const params = {
                'list_id': 1,
                'email': $email.length ? $email.val() : false,
            };
            if (this._recaptcha) {
                params['recaptcha_token_response'] = tokenObj.token;
            }
            this._rpc({
                route: '/website_mass_mailing/subscribe',
                params: params,
            }).then(function (result) {
                let toastType = result.toast_type;
                if (toastType === 'success') {
                    self.$("#newsletter-subscribe").addClass('d-none');
                    self.$("#thanks-for-subscribing").removeClass('d-none');
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
