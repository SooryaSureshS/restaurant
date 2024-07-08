odoo.define('mask_cutomization.portal', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');

var rpc = require('web.rpc');

var QWeb = core.qweb;
publicWidget.registry.AccountPortal = publicWidget.Widget.extend({
    selector: '#skypro_portal',
    events: {
        'click .billing_address': '_billing_address',
        'click .delivery_address': '_delivery_address',
        'click #edit_information': '_edit_information',
        'click #edit_save_changes': '_edit_save_changes',
        'click #edit_cancel_changes': '_edit_cancel_changes',
        'change #edit_country': '_edit_country',
        'click #add_new_address': '_add_new_address',
        'click #information_tab': '_information_tab',
        'click #change_password': '_change_password',
        'click #confirm_password_sk': '_confirm_password_sk',
        'click #cancel_password_sk': '_cancel_password_sk',
        'click #my_orders_tab': '_my_orders_tab',
        'click .draft_orders_list': '_draft_orders_list',
        'click .sale_orders_list': '_sale_orders_list',
        'click #my_order_process_tab': '_my_order_process_tab',
        'click #logout_info': '_logout_info',
        'click #contact_us_info': '_contact_us_info',
        'click #payment_and_delivery_info': '_payment_and_delivery_info',
        'click #privacy_policy_info': '_privacy_policy_info',
        'click .js_change_lang1': '_js_change_lang',
        'click .cancel_language': '_cancel_language',
        'click #language_div_info': '_language_div_info',
        'click .invoice_button': '_invoice_button',
        'click #fire_base_notification': '_fire_base_notification',
        'click .js_change_notification': '_js_change_notification',
    },
    template: null,
//    xmlDependencies: ['mask_cutomization/static/src/xml/template.xml'],
////    cssLibs: null,
//    cssLibs: [
//        '/mask_cutomization/static/src/scss/account_my_profile_page.css'
//    ],
    jsLibs: null,
    assetLibs: null,
    /**
     * @constructor
     */
    init: function () {
        console.log("portal access")
//        this._loadTemplates();
        var self = this;
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    willStart: function () {
        var proms = [];
        if (this.xmlDependencies) {
            proms.push.apply(proms, _.map(this.xmlDependencies, function (xmlPath) {
                return ajax.loadXML(xmlPath, core.qweb);
            }));
        }
        this._load_personal_info();
//        this._loadTemplatesCss();
        return Promise.all(proms);
    },
    _draft_orders_list: function (ev) {
        var self = this;
        var draft_value = $(ev.currentTarget).attr('data-value');
        var $draft_sale = $(ev.currentTarget).closest('.sale_description_draft_subtab');
        $('.sale_description_draft_subtab').each(function(){
            $(this).hide('swing');
        });
        $('.draft_orders_list').each(function(){
            $(this).find('.down_arrow').show('swing');
            $(this).find('.up_arrow').hide('swing');
        });
        var dim = $('#drfat'+draft_value).is(":visible");
        if (dim == false){
            $('#drfat'+draft_value).show('swing');
            $(ev.currentTarget).find('.down_arrow').hide();
            $(ev.currentTarget).find('.up_arrow').show()
        }else{
            $(ev.currentTarget).find('.down_arrow').show()
            $(ev.currentTarget).find('.up_arrow').hide()
        }

    },
    _sale_orders_list: function (ev) {
        var self = this;
        var draft_value = $(ev.currentTarget).attr('data-value');
        var $draft_sale = $(ev.currentTarget).closest('.sale_description_draft_subtab');
        $('.sale_description_sale_subtab').each(function(){
            $(this).hide('swing');
        });
         $('.sale_orders_list').each(function(){
            $(this).find('.down_arrow').show('swing');
            $(this).find('.up_arrow').hide('swing');
        });
        var dim = $('#sale'+draft_value).is(":visible");
        if (dim == false){
            $('#sale'+draft_value).show('swing');
            $(ev.currentTarget).find('.down_arrow').hide();
            $(ev.currentTarget).find('.up_arrow').show()
        }else{
            $(ev.currentTarget).find('.down_arrow').show()
            $(ev.currentTarget).find('.up_arrow').hide()
        }

    },
    _change_password: function (ev) {
        var self = this;
        self._display_none();
        $('#change_password_tab').show('swing');
    },
    _load_personal_info: function () {
        var self = this;
        self._rpc({
                    route: "/portal/information",
                }).then(function (result) {
            });
    },
    _loadTemplates: function(){
        return ajax.loadXML('/mask_cutomization/static/src/xml/template.xml', QWeb);
    },
    _loadTemplatesCss: function(){
        return ajax.loadCSS('/mask_cutomization/static/src/scss/account_my_profile_page.css');
    },
    _billing_address: function (ev) {
         var self = this;
         var billing_id = $(ev.currentTarget).attr('data-value');
         self._rpc({
                    route: "/portal/session/save",
                    params: {
                        address: billing_id,
                        type: "billing"
                    },
                }).then(function (result) {
                console.log("innn")
         });
         $('#selected_billing_address').val("");
         $('#edit_information').attr('disabled','disabled');
         $('.delivery_kanban').each(function (){
            $(this).removeClass('address_selected');
         });
         if (billing_id) {
             $(ev.currentTarget).addClass('address_selected')
             $('#selected_billing_address').val(billing_id).trigger('change')
             $('#edit_information').removeAttr('disabled');
         }
    },
    _delivery_address: function (ev) {
         var self = this;
         var billing_id = $(ev.currentTarget).attr('data-value');
         self._rpc({
                    route: "/portal/session/save",
                    params: {
                        address: billing_id,
                        type: "delivery"
                    },
                }).then(function (result) {
                console.log("innn")
         });
         $('#selected_delivery_address').val("");
         $('#edit_information').attr('disabled','disabled');
         $('.delivery_kanban').each(function (){
            $(this).removeClass('address_selected');

         });
         if (billing_id) {
             $(ev.currentTarget).addClass('address_selected')
             $('#selected_delivery_address').val(billing_id).trigger('change')
              $('#edit_information').removeAttr('disabled');
         }
    },
    _display_none: function () {
         $('.left_info_tab').each(function (){
            $(this).hide('swing');
        });
    },
    _edit_information: function (ev) {
        var self = this;
        console.log("edit information")
        $('#personal_information_widget').hide('swing');
//        $('#edit-information-form').show('swing');
        $('.address_selected').each(function (){
            console.log("eeeeee",$(this))
            $('#edit_partner_id').val($(this).attr('data-value'))
//            edit-information-form
//
            $("#edit-information-form").load(location.href + " #edit-information-form>*", "");
             $('#edit-information-form').show('swing');
        });
    },
    _edit_country: function (ev) {
        var self = this;
        console.log("edit country",ev)
        var country = $(ev.currentTarget).val();
        console.log("infoooooo",country)
        $('#edit_state').empty()
        if (country) {
            self._rpc({
                    route: "/res/country/read",
                    params: {
                        country: country
                    },
                }).then(function (result) {
                    if (result) {
                    _.each(result, function (state_li) {
                        console.log("cccc",state_li)
                        $('#edit_state').append('<option value='+state_li["id"]+'>'+state_li["name"]+'</option>');
                    });

                    }
                });
        }
    },
    _edit_save_changes: function (ev) {
        var self = this;
        var $form = $(ev.currentTarget).closest('form');
        $form.submit();
    },
    _edit_cancel_changes: function (ev) {
        var self = this;
        console.log("cancel")
        window.location.reload();
    },
    _add_new_address: function (ev) {
        var self = this;
        $('#edit_firstname').val("")
        $('#edit_lastname').val("")
        $('#edit_email').val("")
        $('#edit_company').val("")
        $('#edit_phone').val("")
        $('#edit_street').val("")
        $('#edit_street2').val("")
        $("#edit_phone_code > option").each(function() {
            console.log("vvvv852 street",this.value)
            if (this.value == 852) {
                $("#edit_phone_code").val(this.value);
            }
        });
        $("#edit_country").val($("#edit_country option:first").val());
        $("#edit_state").val($("#edit_state option:first").val());
        $('.edit_input_field').each(function(){
            $(this).trigger('change');
        });
        $('#new_address').val('1')
        $('#new_address').trigger('change')
    },
    _information_tab: function (ev) {
        var self = this;
        self._display_none();
        $('#personal_information_widget').show('swing');
    },
    _confirm_password_sk: function (ev) {
        var self = this;
        var old_pass = $('#old_pass').val();
        var new_pass = $('#new_pass').val();
        var new_confirm = $('#new_confirm').val();
        if (old_pass && new_pass && new_confirm) {
        if (new_pass == new_confirm) {
            self._rpc({
                route: "/forgot/password/user",
                params: {
                    old_pass: old_pass,
                    new_pass: new_pass,
                    new_confirm: new_confirm,
                },
                }).then(function (result) {
                if (result) {
                    console.log("resultss",result)
                    if (result['success']){
                        $('#error_message_display').html(result['message']);
                        $('#error_message_display').show('swing');
                        setTimeout(function () {
                           $('#error_message_display').hide('swing');
                        }, 1000);
                        window.location.reload()
                    }else{
                        $('#error_message_display').html(result['error_code']);
                        $('#error_message_display').show('swing');
                        setTimeout(function () {
                           $('#error_message_display').hide('swing');
                        }, 1000);
                    }
                }
            });
        }else{
            $('#error_message_display').html('new password and confirm password are not same');
            $('#error_message_display').show('swing');
            setTimeout(function () {
               $('#error_message_display').hide('swing');
            }, 1000);
        }

        }else{
            $('#error_message_display').html('Please fill the required field');
            $('#error_message_display').show('swing');
            setTimeout(function () {
               $('#error_message_display').hide('swing');
            }, 1000);
        }


    },
    _cancel_password_sk: function (ev) {
        var self = this;
        self._display_none();
        $('#personal_information_widget').show('swing');
    },
    _my_orders_tab: function (ev) {
        var self = this;
        self._display_none();
        $('#my_orders_div').show('swing');
    },
    _my_order_process_tab: function (ev) {
        var self = this;
        window.location.href = '/my/order/process';
    },
    _logout_info: function (ev) {
        var self = this;
        window.location.href = '/web/session/logout';
    },
    _contact_us_info: function (ev) {
            var self = this;
        window.location.href = '/contact_us';
    },
    _payment_and_delivery_info: function (ev) {
        var self = this;
        window.location.href = '/payment/delivery';

    },
    _privacy_policy_info: function (ev) {
        var self = this;
        window.location.href = '/privacy/policy';
    },
    _js_change_lang: function (ev) {
        var self = this;
        ev.preventDefault();
        var $target = $(ev.currentTarget);
        var value = $target.attr('data-value');
        var redirect = {
            lang: value,
            url: encodeURIComponent($target.attr('data-redirect').replace(/[&?]edit_translations[^&?]+/, '')),
            hash: encodeURIComponent(window.location.hash)
        };
        window.location.href = _.str.sprintf("/website/lang/%(lang)s?r=%(url)s%(hash)s", redirect);
    },
    _cancel_language: function (ev) {
        var self = this;
        $('#overlay').hide('swing');
    },
    _language_div_info: function (ev) {
        var self = this;
        $('#overlay').show('swing');
    },
    _invoice_button: function (ev) {
        var self = this;
        ev.preventDefault();
        var $target = $(ev.currentTarget);
        var value = $target.attr('data-value');
        window.location.href = '/my/invoice/'+value+'';
    },
    _fire_base_notification: function (ev) {
        var self = this;
        $('#overlay_notification').show('swing');
    },
    _js_change_notification: function (ev) {
        var self = this;
        ev.preventDefault();
        var $target = $(ev.currentTarget);
        if ($(ev.currentTarget).html() == 'on'){
            self._rpc({
                route: "/notification/changed",
                params: {
                    state: 'on',
                },
                }).then(function (result) {
                    if (result) {
                        window.location.reload();
                    }
                });
        }else{
            self._rpc({
                route: "/notification/changed",
                params: {
                    state: 'off',
                },
                }).then(function (result) {
                    if (result) {
                        window.location.reload();
                    }
                });
        }
    },

});
publicWidget.registry.AccountPortal_nologin = publicWidget.Widget.extend({
    selector: '#skypro_portal_no_login',
    events: {
        'click .billing_address': '_billing_address',
        'click .delivery_address': '_delivery_address',
        'click #edit_information': '_edit_information',
        'click #edit_save_changes': '_edit_save_changes',
        'click #edit_cancel_changes': '_edit_cancel_changes',
        'change #edit_country': '_edit_country',
        'click #add_new_address': '_add_new_address',
        'click #information_tab': '_information_tab',
        'click #change_password': '_change_password',
        'click #confirm_password_sk': '_confirm_password_sk',
        'click #cancel_password_sk': '_cancel_password_sk',
        'click #my_orders_tab': '_my_orders_tab',
        'click .draft_orders_list': '_draft_orders_list',
        'click .sale_orders_list': '_sale_orders_list',
        'click #my_order_process_tab': '_my_order_process_tab',
        'click #logout_info': '_logout_info',
        'click #contact_us_info': '_contact_us_info',
        'click #payment_and_delivery_info': '_payment_and_delivery_info',
        'click #privacy_policy_info': '_privacy_policy_info',
        'click .js_change_lang1': '_js_change_lang',
        'click .cancel_language': '_cancel_language',
        'click #language_div_info': '_language_div_info',

        'click #register_login_tab': '_register_login_tab',
        'click #login_tab': '_login_tab',
        'click #fire_base_notification': '_fire_base_notification',
        'click .js_change_notification': '_js_change_notification',

    },
    template: null,
//    xmlDependencies: ['mask_cutomization/static/src/xml/template.xml'],
////    cssLibs: null,
//    cssLibs: [
//        '/mask_cutomization/static/src/scss/account_my_profile_page.css'
//    ],
    jsLibs: null,
    assetLibs: null,
    /**
     * @constructor
     */
    init: function () {
        console.log("portal access")
//        this._loadTemplates();
        var self = this;
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    willStart: function () {
        var proms = [];
        if (this.xmlDependencies) {
            proms.push.apply(proms, _.map(this.xmlDependencies, function (xmlPath) {
                return ajax.loadXML(xmlPath, core.qweb);
            }));
        }
//        this._load_personal_info();
//        this._loadTemplatesCss();
        return Promise.all(proms);
    },
    _my_order_process_tab: function (ev) {
        var self = this;
        window.location.href = '/my/order/process';
    },
    _logout_info: function (ev) {
        var self = this;
        window.location.href = '/web/session/logout';
    },
    _contact_us_info: function (ev) {
            var self = this;
        window.location.href = '/contact_us';
    },
    _payment_and_delivery_info: function (ev) {
        var self = this;
        window.location.href = '/payment/delivery';

    },
    _privacy_policy_info: function (ev) {
        var self = this;
        window.location.href = '/privacy/policy';
    },
    _register_login_tab: function (ev) {
        var self = this;
         window.location.href = '/web/login';
    },
    _login_tab: function (ev) {
        var self = this;
         window.location.href = '/web/login';
    },
    _js_change_lang: function (ev) {
        var self = this;
        ev.preventDefault();
        var $target = $(ev.currentTarget);
        var value = $target.attr('data-value');
        var redirect = {
            lang: value,
            url: encodeURIComponent($target.attr('data-redirect').replace(/[&?]edit_translations[^&?]+/, '')),
            hash: encodeURIComponent(window.location.hash)
        };
        window.location.href = _.str.sprintf("/website/lang/%(lang)s?r=%(url)s%(hash)s", redirect);
    },
    _cancel_language: function (ev) {
        var self = this;
        $('#overlay').hide('swing');
    },
    _language_div_info: function (ev) {
        var self = this;
        $('#overlay').show('swing');
    },
        _fire_base_notification: function (ev) {
        var self = this;
        $('#overlay_notification').show('swing');
    },
    _js_change_notification: function (ev) {
        var self = this;
        ev.preventDefault();
        var $target = $(ev.currentTarget);
        if ($(ev.currentTarget).html() == 'on'){
            self._rpc({
                route: "/notification/changed",
                params: {
                    state: 'on',
                },
                }).then(function (result) {
                    if (result) {
                        window.location.reload();
                    }
                });
        }else{
            self._rpc({
                route: "/notification/changed",
                params: {
                    state: 'off',
                },
                }).then(function (result) {
                    if (result) {
                        window.location.reload();
                    }
                });
        }
    },
    });
});