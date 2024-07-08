odoo.define('gio_obstgemuese_theme.checkout', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var PortalSidebar = require('portal.PortalSidebar');
var ajax = require("web.ajax");
var core = require('web.core');

var _t = core._t;
var concurrency = require('web.concurrency');
var dp = new concurrency.DropPrevious();

publicWidget.registry.step_container = publicWidget.Widget.extend({
    /**
     * jQuery selector for the element.
     * @property {String} selector
     */
    selector: '.step-container',
    /**
     * The events this widget listens to.
     * @property {Object} events
     */
    events:{
        'click .shipping_select':'onClickSelect',
        'click .ob_edit_address':'onClickBillAddressEdit',
        'click .bill_add_edit_back':'onClickBillAddressEditClose',
        'click .add_shipping_address_btn':'onClickShipAddressAdd',
        'click .ship_address_add_back':'onClickShipAddressClose',
        'click .edit_billing_address_btn':'onClickEditBillingAddress',
        'click .add_partner_address_btn':'onClickPartnerAddressAdd',
        'click .edit_billing_address_btn_modal':'onClickEditBillingAddressModal',
        'click .edit_shipping_address_btn_modal':'onClickEditShippingAddressModal',
        'click .edit_shipping_address_btn':'onClickEditShippingAddress',
        'click .kanban_shipping_address_add_cls':'onClickAddShippingAddress',
        'click .js_change_shipping': '_onClickChangeShipping',
        'click .public_usr_address_add': '_onClickAddAddressPublicUser',
        'click .next-step': '_onClickCheckoutNextTab',
        'click .shipping_next_step_btn': '_onClickCheckoutNextTabShipping',
        'click .shipping_next_step_btn_nb': '_onClickCheckoutNextTabShipping_nb',
        'click .payment_next_step_btn': '_onClickCheckoutNextTabPayment',
        'click .confirm_payment_button': '_onClickCheckoutConfirmationButton',
        'click .prev-step': '_onClickCheckoutPrevTab',
        'change select[name="shipping_id"]': '_onSetAddress',
        'click #delivery_carrier .o_delivery_carrier_select': '_onCarrierClick',
        'click .edit_shipping_method_btn_modal ': '_onClickChangeShippingMethodModal',
        'click .edit_payment_method_class ': '_onClickEditPaymentMethod',
        'change select[name="country_id"]': '_onChangeCountry',
    },
    /**
     * Initializes the behavior for the given element.
     * This function adds a bottom padding of 80px to the navbar element with `data-name` attribute equal to "Navbar"
     * only when the current window location path is "/process/checkout/page".
     *
     * @function
     * @private
     */
    init: function () {
            this._super.apply(this, arguments);
            var path = window.location.pathname
            if (path == "/process/checkout/page"){
                $('nav[data-name="Navbar"]').css('padding-bottom', '80px')
            }

        },
    /**
     * A function that hides the buttons with class '.btn-primary' and '.btn-secondary' when called.
     */
    start: function () {
        $('.btn-primary').css('display', 'none');
        $('.btn-secondary').css('display', 'none');
    },
    /**
     * onClickSelect is a jQuery function that handles the click event on a shipping method selection element.
     *
     * @function onClickSelect
     * @param {event} events - The click event object
     *
     * The function performs the following actions:
     *  1. Retrieve the value of the clicked shipping method element using its parent element
     *  2. Remove the 'shipping_selected' class from all shipping method elements
     *  3. Add the 'shipping_selected' class to the clicked shipping method element
     */
    onClickSelect:function(events){
        var id = $(events.target).parents('.shipping_select').attr('value')
        $('.shipping_select').removeClass('shipping_selected')
        $(events.target).parents('.shipping_select').addClass('shipping_selected')
    },
    /**
     * Function to handle the click event on the Billing Address Edit button.
     *
     * @param {object} events - Event object containing the information about the triggered event.
     *
     * Hides the shipping and billing address view elements and shows the corresponding address edit element
     * when the Billing Address Edit button is clicked.
     */
    onClickBillAddressEdit:function(events){
        $('.ob_edit_address').click(function() {
        $(".kanban_billing_address_edit_cls").css('display', 'none');
        $(".kanban_shipping_address_edit_cls").css('display', 'none');
        var address_id = "#partner_address_" + $(this).attr('id')
         $(address_id).css('display', 'block');
         if ($(address_id).prev()[0].className === 'kanban_billing_address_cls'){
            $('.kanban_billing_address_cls').css('display', 'none');}
         else {$('.kanban_billing_address_cls').css('display', 'block');}
         });
    },
    /**
     * onClickBillAddressEditClose is a jQuery function that handles the event when the "close" button of the billing address edit form is clicked.
     *
     * The function first shows the billing address information. Then it hides both the billing address edit form and shipping address edit form.
     * Lastly, the function animates the page to the top.
     *
     * @events {Object} events - The click event that triggers the function.
     */
    onClickBillAddressEditClose:function(events){
        $('.kanban_billing_address_cls').delay(100).fadeIn();
        $(".kanban_billing_address_edit_cls").css('display', 'none');
        $(".kanban_shipping_address_edit_cls").css('display', 'none');
        $("html, body").animate({ scrollTop: $(document).height(0,0) }, 100);
    },
    /**
     * onClickShipAddressAdd - Shows the 'add_shipping_address_cls' element with a delay and scrolls the page to the bottom.
     *
     * @param {event} events - Click event object triggered by clicking on an element.
     */
    onClickShipAddressAdd:function(events){
        $('.add_shipping_address_cls').delay(100).fadeIn();
        $("html, body").animate({ scrollTop: $(document).height() }, 100);
    },
    /**
    onClickShipAddressClose - A Jquery function that closes the add shipping address form.
    The function sets the display of the add shipping address form to "none".
    Then it animates the scrolling of the document to the top.
    @param {event} events - The event that triggers the function.
    */
    onClickShipAddressClose:function(events){
        $('.add_shipping_address_cls').css('display', 'none');
        $("html, body").animate({ scrollTop: $(document).height(0,0) }, 100);
    },
    /**
     * onClickPartnerAddressAdd is a function that sends a request to the server to add a new partner address
     * based on the input values of the form fields. The values are collected from the target event and its parent
     * elements with the class "kanban_partner_address_add_cls". The values are then passed to the server through
     * ajax.jsonRpc() function with a call to "/process/checkout/address". The result of the call is then evaluated,
     * and an informative pop-up is displayed to the user with the status and message from the server.
     * Additionally, the function reloads some parts of the page to reflect the changes.
     *
     * @param {event} events - The event that triggers the function.
     */
    onClickPartnerAddressAdd:function(events){
        var parent_div_input = $(events.target).parents('.kanban_partner_address_add_cls').children('.form-row').children('.form-group').children('input')
        var parent_div_select = $(events.target).parents('.kanban_partner_address_add_cls').children('.form-row').children('.form-group').children('select')
        var value_dit = {}
        _.each(parent_div_input, function(value){
            value_dit[$(value).attr('name')] = $(value).val()
        });
        _.each(parent_div_select, function(value){
            value_dit[$(value).attr('name')] = $(value).val()
        });
        value_dit['mode'] = ['edit', 'billing']
        ajax.jsonRpc('/process/checkout/address', 'call', value_dit)
                .then(function (result) {
                if(result.status){
                    var html = $('#wrapwrap').last()
                    var head = result.message
                    var text = result.message
                    html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>"+head+"</h1><p>"+text+"</p></div></div>")
                    setTimeout(function() {
                       $('#ob_portal_pop_up').delay(1000).remove();
                    }, 1000);
                    $('.bill_add_edit_back').click();
                    $('#step1').load(window.location.href+' #step1');
                    $('#step2').load(window.location.href+' #step2');
                    $('#step3').load(window.location.href+' #step3');
                    $('#step4').load(window.location.href+' #step4');

                    }
                else {
                    var html = $('#wrapwrap').last()
                    var head = result.message
                    var text = result.message
                    html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>"+head+"</h1><p>"+text+"</p></div></div>")
                    setTimeout(function() {
                       $('#ob_portal_pop_up').delay(1000).remove();
                    }, 1000);
                }

                });
    },
    /**
     * onClickEditBillingAddress is a jQuery function that updates the billing address of a customer.
     *
     * @param {Object} events - The event that triggered the function.
     *
     * The function works as follows:
     * 1. Get the input and select elements within the parent `.kanban_billing_address_edit_cls` div.
     * 2. Store their values in the `value_dit` object.
     * 3. Add the 'mode' key to the `value_dit` object with value `['edit', 'billing']`.
     * 4. Make an AJAX JSON-RPC call to the '/process/checkout/address' endpoint with the `value_dit` object as argument.
     * 5. If the response has a 'status' property set to `true`, display a success message and reload the #step1 element.
     * 6. If the response has a 'status' property set to `false`, display an error message.
     */
    onClickEditBillingAddress:function(events){
        var parent_div_input = $(events.target).parents('.kanban_billing_address_edit_cls').children('.form-row').children('.form-group').children('input')
        var parent_div_select = $(events.target).parents('.kanban_billing_address_edit_cls').children('.form-row').children('.form-group').children('select')
        var value_dit = {}
        _.each(parent_div_input, function(value){
            value_dit[$(value).attr('name')] = $(value).val()
        });
        _.each(parent_div_select, function(value){
            value_dit[$(value).attr('name')] = $(value).val()
        });
        value_dit['mode'] = ['edit', 'billing']
        ajax.jsonRpc('/process/checkout/address', 'call', value_dit)
                .then(function (result) {
                if(result.status){
                    var html = $('#wrapwrap').last()
                    var head = result.message
                    var text = result.message
                    html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>"+head+"</h1><p>"+text+"</p></div></div>")
                    setTimeout(function() {
                       $('#ob_portal_pop_up').delay(1000).remove();
                    }, 1000);
                    $('.bill_add_edit_back').click();
                    $('#step1').load(window.location.href+' #step1');}
                else {
                    var html = $('#wrapwrap').last()
                    var head = result.message
                    var text = result.message
                    html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>"+head+"</h1><p>"+text+"</p></div></div>")
                    setTimeout(function() {
                       $('#ob_portal_pop_up').delay(1000).remove();
                    }, 1000);
                }

                });
    },
    /**
     * onClickEditBillingAddressModal - function that makes an ajax call to update the billing address in checkout process.
     * @param {Object} events - Event object that triggered the function.
     *
     * The function first finds the input and select elements within the parent div with class `kanban_billing_address_edit_cls_modal`
     * and stores their name and value in a dictionary `value_dit`. The `mode` key of the dictionary is set to `['edit', 'billing']`.
     * Then it makes an ajax call to the endpoint `/process/checkout/address` with method `call` and the `value_dit` as the argument.
     * In the ajax's then function, if the ajax call is successful and the result has a `status` attribute with value `true`,
     * it closes the modal, reloads the billing address section, and sets the active tab.
     */
    onClickEditBillingAddressModal:function(events){
        var parent_div_input = $(events.target).parents('.kanban_billing_address_edit_cls_modal').children('.form-row').children('.form-group').children('input')
        var parent_div_select = $(events.target).parents('.kanban_billing_address_edit_cls_modal').children('.form-row').children('.form-group').children('select')
        var value_dit = {}
        _.each(parent_div_input, function(value){
            value_dit[$(value).attr('name')] = $(value).val()
        });
        _.each(parent_div_select, function(value){
            value_dit[$(value).attr('name')] = $(value).val()
        });
        value_dit['mode'] = ['edit', 'billing']
        ajax.jsonRpc('/process/checkout/address', 'call', value_dit)
                .then(function (result) {
                if(result.status){
                    var html = $('#wrapwrap').last()
                    var head = result.message
                    var text = result.message
                   $('#edit_billing_address_id').modal('hide')
                   $('.kanban_billing_address_cls_modal').load(window.location.href+' .kanban_billing_address_cls_modal');
                   var active = $('.wizard .nav-tabs li.active');
                    }
                });
    },
    onClickEditShippingAddressModal:function(events){
        var parent_div_input = $(events.target).parents('.kanban_shipping_address_edit_cls_modal').children('.form-row').children('.form-group').children('input')
        var parent_div_select = $(events.target).parents('.kanban_shipping_address_edit_cls_modal').children('.form-row').children('.form-group').children('select')
        var value_dit = {}
        var payment_acquire_name = $('#payment_acquire_name').text()
        var shipping_method_name = $('#shipping_method_name').text()
        _.each(parent_div_input, function(value){
            value_dit[$(value).attr('name')] = $(value).val()
        });
        _.each(parent_div_select, function(value){
            value_dit[$(value).attr('name')] = $(value).val()
        });
        value_dit['mode'] = ['edit', 'shipping']
        ajax.jsonRpc('/process/checkout/address', 'call', value_dit)
                .then(function (result) {
                if(result.status){
                    var html = $('#wrapwrap').last()
                    var head = result.message
                    var text = result.message
                   $('#edit_Shipping_address_id').modal('hide')
                   $('.kanban_shipping_address_cls_modal').load(window.location.href+' .kanban_shipping_address_cls_modal');
                   var active = $('.wizard .nav-tabs li.active');
                   $('#shipping_method_name').text(shipping_method_name);
                   $('#payment_acquire_name').text(payment_acquire_name);
                    }
                });
    },
    onClickEditShippingAddress:function(events){
        var parent_div_input = $(events.target).parents('.kanban_shipping_address_edit_cls').children('.form-row').children('.form-group').children('input')
        var parent_div_select = $(events.target).parents('.kanban_shipping_address_edit_cls').children('.form-row').children('.form-group').children('select')
        var value_dit = {}
        _.each(parent_div_input, function(value){
            value_dit[$(value).attr('name')] = $(value).val()
        });
        _.each(parent_div_select, function(value){
            value_dit[$(value).attr('name')] = $(value).val()
        });
        value_dit['mode'] = ['edit', 'shipping']
        ajax.jsonRpc('/process/checkout/address', 'call', value_dit)
                .then(function (result) {
                if(result.status){
                    var html = $('#wrapwrap').last()
                    var head = result.message
                    var text = result.message
                    html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>"+head+"</h1><p>"+text+"</p></div></div>")
                    setTimeout(function() {
                       $('#ob_portal_pop_up').delay(1000).remove();
                    }, 1000);
                    $('.bill_add_edit_back').click();
                    $('#registration').load(window.location.href+' #registration');
                    }
                else {
                    var html = $('#wrapwrap').last()
                    var head = result.message
                    var text = result.message
                    html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>"+head+"</h1><p>"+text+"</p></div></div>")
                    setTimeout(function() {
                       $('#ob_portal_pop_up').delay(1000).remove();
                    }, 1000);
                }

            });
    },
    onClickAddShippingAddress:function(events){
        var parent_div_input = $(events.target).parents('.add_shipping_address_cls').children('.form-row').children('.form-group').children('input')
        var parent_div_select = $(events.target).parents('.add_shipping_address_cls').children('.form-row').children('.form-group').children('select')
        var value_dit = {}
        _.each(parent_div_input, function(value){
            if (value_dit[$(value).attr('name')] != 'partner_id'){
            value_dit[$(value).attr('name')] = $(value).val()}
        });
        _.each(parent_div_select, function(value){
            value_dit[$(value).attr('name')] = $(value).val()
        });
        value_dit['mode'] = ['new', 'shipping']
        ajax.jsonRpc('/process/checkout/address', 'call', value_dit)
                .then(function (result) {
                if(result.status){
                    var html = $('#wrapwrap').last()
                    var head = result.message
                    var text = result.message
                    html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>"+head+"</h1><p>"+text+"</p></div></div>")
                    setTimeout(function() {
                       $('#ob_portal_pop_up').delay(1000).remove();
                    }, 1000);
                    $('.bill_add_edit_back').click();
                    $('#registration').load(window.location.href+' #registration');
                    }
                else {
                    var html = $('#wrapwrap').last()
                    var head = result.message
                    var text = result.message
                    html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>"+head+"</h1><p>"+text+"</p></div></div>")
                    setTimeout(function() {
                       $('#ob_portal_pop_up').delay(1000).remove();
                    }, 1000);
                }

            });
    },
    _onClickChangeShipping: function (ev) {
        var $old = $('.all_shipping').find('.card.border.border-primary');
        $old.find('.btn-ship').toggle();
        $old.addClass('js_change_shipping');
        $old.removeClass('border border-primary');

        var $new = $(ev.currentTarget).parent('div.one_kanban').find('.card');
        $new.find('.btn-ship').toggle();
        $new.removeClass('js_change_shipping');
        $new.addClass('border border-primary');

        var $form = $(ev.currentTarget).parent('div.one_kanban').find('form.d-none');
        $.post($form.attr('action'), $form.serialize()+'&xhr=1');

        setTimeout(function() {
            $('#registration').load(window.location.href+' #registration');
                }, 300);

    },
    _onClickAddAddressPublicUser: function(events){
        var parent_div_input = $(events.target).parents('.justify-content-between').prev().children('.form-group').children('input')
        var parent_div_select = $(events.target).parents('.justify-content-between').prev().children('.form-group').children('select')
        var value_dit = {}
        _.each(parent_div_input, function(value){
            if (value_dit[$(value).attr('name')] != 'partner_id'){
                value_dit[$(value).attr('name')] = $(value).val()}
        });
        _.each(parent_div_select, function(value){
            value_dit[$(value).attr('name')] = $(value).val()
        });
        value_dit['mode'] = ['new', 'billing']
        ajax.jsonRpc('/process/checkout/address', 'call', value_dit)
                .then(function (result) {
                if(result.status){
                    var html = $('#wrapwrap').last()
                    var head = result.message
                    var text = result.message
                    html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>"+head+"</h1><p>"+text+"</p></div></div>")
                    setTimeout(function() {
                       $('#ob_portal_pop_up').delay(1000).remove();
                    }, 1000);
                    $('.bill_add_edit_back').click();
                    $('.main_form_class').load(window.location.href+' .main_form_class');
                    }
                else {
                    var html = $('#wrapwrap').last()
                    var head = result.message
                    var text = result.message
                    html.append("<div id='ob_portal_pop_up' class='ob_portal_pop_up'><div class='ob_portal_pop_up-content'><span class='ob_portal_pop_up_close'><i class='fa fa-times d-block'/></span><h1>"+head+"</h1><p>"+text+"</p></div></div>")
                    setTimeout(function() {
                       $('#ob_portal_pop_up').delay(1000).remove();
                    }, 1000);
                }

                });
    },
    _onClickChangeShipping: function (ev) {
    var $old = $('.all_shipping').find('.card.border.border-primary');
    $old.find('.btn-ship').toggle();
    $old.addClass('js_change_shipping');
    $old.removeClass('border border-primary');

    var $new = $(ev.currentTarget).parent('div.one_kanban').find('.card');
    $new.find('.btn-ship').toggle();
    $new.removeClass('js_change_shipping');
    $new.addClass('border border-primary');

    var $form = $(ev.currentTarget).parent('div.one_kanban').find('form.d-none');
    $.post($form.attr('action'), $form.serialize()+'&xhr=1');

    setTimeout(function() {
        $('#registration').load(window.location.href+' #registration');
            }, 300);
    },
    _onClickCheckoutNextTab: function (ev) {
        var active = $('.wizard .nav-tabs li.active');
            if ($(".partner-id-class").val() != 4){
                active.next().removeClass('disabled');
                $(active).next().find('a[data-toggle="tab"]').click();
            }
            else{
                $(".next-step").effect( "bounce", {times:4}, 300 );
            }
    },
    _onClickCheckoutNextTabShipping: function (ev) {
        var active = $('.wizard .nav-tabs li.active');
            if ($(ev.target).parent('li').prev().children('label').children('input').is(':checked')){
                $('#shipping_method_name').text($(ev.target).parent('li').prev().children('label').next('label').text())
                active.next().removeClass('disabled');
                $(active).next().find('a[data-toggle="tab"]').click();
            }
            else{
                $(ev.target).effect( "bounce", {times:4}, 300 );
            }
    },
    _onClickCheckoutNextTabShipping_nb: function (ev) {
        var active = $('.wizard .nav-tabs li.active');
            if ($(ev.target).prev().prev().prev('label').prev('label').children('input').is(':checked')){
                $('#shipping_method_name').text($(ev.target).prev().prev().prev('label').prev('label').next('label').text())
                active.next().removeClass('disabled');
                $(active).next().find('a[data-toggle="tab"]').click();
            }
            else{
                $(ev.target).effect( "bounce", {times:4}, 300 );
            }
    },
    _onClickCheckoutNextTabPayment: function (ev) {
        var active = $('.wizard .nav-tabs li.active');
            var paymentCard = $(ev.target).parent('li').parent('ul').siblings('form').children('.card').children('.o_payment_option_card')
            var is_checked = false
            _.each(paymentCard, function(value){
                    if ($(value).children('label').children('input').is(':checked')){
                        $('#payment_acquire_name').text($(value).children('label').children('input').siblings('.payment_option_name').children('b').text());
                        is_checked = true
                    }
                });
            if (is_checked){
                const $submitButton = this.$('button[name="o_payment_submit_button"]');
                const iconClass = $submitButton.data('icon-class');
                active.next().removeClass('disabled');
                $(active).next().find('a[data-toggle="tab"]').click();
                $('#payment_div').children('form').children('.card').css('display', 'none');
                $submitButton.attr('disabled', false);
                $submitButton.find('i').addClass(iconClass);
                $submitButton.find('span.o_loader').remove();
                $('.checkout_layout_index').css('display', 'none')
                $('nav[data-name="Navbar"]').css('padding-bottom', '0px')
            }
            else{
                $(ev.target).effect( "bounce", {times:4}, 300 );
            }
    },
    _onClickCheckoutConfirmationButton: function (ev) {
        $("button[name='o_payment_submit_button']")[0].click()
    },
    _onClickCheckoutPrevTab: function (ev) {
        var active = $('.wizard .nav-tabs li.active');
            $(active).prev().find('a[data-toggle="tab"]').click();
    },

        start: function () {
        var self = this;
        var $carriers = $('#delivery_carrier input[name="delivery_type"]');
        var $payButton = $('button[name="o_payment_submit_button"]');

        if ($carriers.length > 0) {
            if ($carriers.filter(':checked').length === 0) {
                $payButton.prop('disabled', true);
                var disabledReasons = $payButton.data('disabled_reasons') || {};
                disabledReasons.carrier_selection = true;
                $payButton.data('disabled_reasons', disabledReasons);
            }
            $carriers.filter(':checked').click();
        }

        _.each($carriers, function (carrierInput, k) {
            self._showLoading($(carrierInput));
            self._rpc({
                route: '/shop/carrier_rate_shipment',
                params: {
                    'carrier_id': carrierInput.value,
                },
            }).then(self._handleCarrierUpdateResultBadge.bind(self));
        });

        return this._super.apply(this, arguments);
    },

    _showLoading: function ($carrierInput) {
        $carrierInput.siblings('.o_wsale_delivery_badge_price').empty();
        $carrierInput.siblings('.o_wsale_delivery_badge_price').append('<span class="fa fa-circle-o-notch fa-spin"/>');
    },

    _updateShippingCost: function(amount){
        core.bus.trigger('update_shipping_cost', amount);
    },

    _handleCarrierUpdateResult: function (result) {
        this._handleCarrierUpdateResultBadge(result);
        var $payButton = $('button[name="o_payment_submit_button"]');
        var $amountDelivery = $('#order_delivery .monetary_field');
        var $amountUntaxed = $('#order_total_untaxed .monetary_field');
        var $amountTax = $('#order_total_taxes .monetary_field');
        var $amountTotal = $('#order_total .monetary_field, #amount_total_summary.monetary_field');

        if (result.status === true) {
            $amountDelivery.html(result.new_amount_delivery);
            $amountUntaxed.html(result.new_amount_untaxed);
            $amountTax.html(result.new_amount_tax);
            $amountTotal.html(result.new_amount_total);
            var disabledReasons = $payButton.data('disabled_reasons') || {};
            disabledReasons.carrier_selection = false;
            $payButton.data('disabled_reasons', disabledReasons);
            $payButton.prop('disabled', _.contains($payButton.data('disabled_reasons'), true));
        } else {
            $amountDelivery.html(result.new_amount_delivery);
            $amountUntaxed.html(result.new_amount_untaxed);
            $amountTax.html(result.new_amount_tax);
            $amountTotal.html(result.new_amount_total);
        }
        if (result.new_amount_total_raw !== undefined) {
            this._updateShippingCost(result.new_amount_total_raw);
        }
    },

    _handleCarrierUpdateResultBadge: function (result) {
        var $carrierBadge = $('#delivery_carrier input[name="delivery_type"][value=' + result.carrier_id + '] ~ .o_wsale_delivery_badge_price');

        if (result.status === true) {
             if (result.is_free_delivery) {
                 $carrierBadge.text(_t('Free'));
             } else {
                 $carrierBadge.html(result.new_amount_delivery);
             }
             $carrierBadge.removeClass('o_wsale_delivery_carrier_error');
        } else {
            $carrierBadge.addClass('o_wsale_delivery_carrier_error');
            $carrierBadge.text(result.error_message);
        }
    },

    _onCarrierClick: function (ev) {
        var $radio = $(ev.currentTarget).find('input[type="radio"]');
        this._showLoading($radio);
        $radio.prop("checked", true);
        var $payButton = $('button[name="o_payment_submit_button"]');
        $payButton.prop('disabled', true);
        var disabledReasons = $payButton.data('disabled_reasons') || {};
        disabledReasons.carrier_selection = true;
        $payButton.data('disabled_reasons', disabledReasons);
        dp.add(this._rpc({
            route: '/shop/update_carrier',
            params: {
                carrier_id: $radio.val(),
            },
        })).then(this._handleCarrierUpdateResult.bind(this));
    },

    _onSetAddress: function (ev) {
        var value = $(ev.currentTarget).val();
        var $providerFree = $('select[name="country_id"]:not(.o_provider_restricted), select[name="state_id"]:not(.o_provider_restricted)');
        var $providerRestricted = $('select[name="country_id"].o_provider_restricted, select[name="state_id"].o_provider_restricted');
        if (value === 0) {
            $providerFree.hide().attr('disabled', true);
            $providerRestricted.show().attr('disabled', false).change();
        } else {
            $providerFree.show().attr('disabled', false).change();
            $providerRestricted.hide().attr('disabled', true);
        }
    },
    _onClickChangeShippingMethodModal: function (ev){
        $('#shipping_methods_id').modal('hide')
        _.each($(ev.target).parent('.modal-footer').prev().find('.o_delivery_carrier_select'), function(value){
            if ($(value).find('input[name="delivery_type"]').is(':checked')) {
                $('#shipping_method_name').text($(value).find('input[name="delivery_type"]:checked').parent('label').siblings('label').text())
            }
        });
    },
    _onClickEditPaymentMethod: function(ev){
        const payCard = $(ev.currentTarget).parent('.modal-footer').prev().children('.o_payment_form').children('.card')
        const RadioChecked = payCard.find('input[name="o_payment_radio"]:checked')[0]
        const provider = RadioChecked.dataset.provider
        const paymentOptionType = RadioChecked.dataset.paymentOptionType
        const paymentOptionId = RadioChecked.dataset.paymentOptionId
        var MainPayCard = $(".payment_method_select_div_cls").children('.o_payment_form').children('.card').children()
        _.each(MainPayCard, function(value){
            var PaymentRadio = $(value).find('input[name="o_payment_radio"]')[0]
            if (PaymentRadio){
                var PaymentRadioSelect = $(PaymentRadio)[0]
                if (PaymentRadioSelect.dataset.provider == provider && PaymentRadioSelect.dataset.paymentOptionId == paymentOptionId && PaymentRadioSelect.dataset.paymentOptionType == paymentOptionType)
                {
                    $(value).click()
                }
              }
        });
        var paymentCard = $('.payment_method_select_div_cls').children('.o_payment_form').children('.card').children('.o_payment_option_card')
        _.each(paymentCard, function(value){
            if ($(value).children('label').children('input').is(':checked')){
                $('#payment_acquire_name').text($(value).children('label').children('input').siblings('.payment_option_name').children('b').text());
            }
        });
        $('#payment_method_id').modal('hide')
    },

        _onChangeCountry: function (ev) {
        if (!$(ev.target).val()) {
            return;
        }
        this._rpc({
            route: "/shop/country_info/" + $(ev.target).val(),
            params: {
                mode:$(ev.target).attr('mode'),
            },
        }).then(function (data) {
            // populate states and display
            var selectStates = $(ev.target).parent('.div_country').siblings('.div_state').children("select[name='state_id']");
            // dont reload state at first loading (done in qweb)
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
