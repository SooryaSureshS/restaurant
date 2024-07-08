odoo.define('gio_obstgemuese_theme.obst_live_chat_option', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var ajax = require("web.ajax");
var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var LivechatButton = require('im_livechat.legacy.im_livechat.im_livechat').LivechatButton;
var ObstAbstractThreadWindow = require('im_livechat.legacy.mail.AbstractThreadWindow');
var _t = core._t;
var obst_chat_box

publicWidget.registry.obst_live_chat_option = publicWidget.Widget.extend({
    /**
     * jQuery selector for the element.
     * @property {String} selector
     */
    selector: '#wrapwrap',
    /**
     * The events this widget listens to.
     * @property {Object} events
     */
    events:{
        'click .open-chat-box': '_onClickOpenChatBox',
        'click .chat-box-close': '_onClickCloseChatBox',
        'keydown .obst_o_composer_text_field': '_obstOnKeydown',
    },

    init: function (parent, thread, options) {
        this._super(parent);
        this._thread = thread || null;
    },

    /**
     * _onClickOpenChatBox is a jQuery function that opens the chat box container and hides the live chat popup.
     * It adds the 'toggle_active' class to the chat-box-container element, sets the overflow-y of the wrapwrap
     * element to 'hidden' and fades in the navbar and chat-box-ui-block elements. Depending on the width of the
     * window, the chat-box-container element will either animate to the left with a value of '0%' or '67%'.
     * Finally, it sets the display of the ObLiveChatPopUp element to 'none'.
     */
    _onClickOpenChatBox: function () {
        $('.navbar').fadeIn(250)
//        $('.o_thread_window.o_in_home_menu').css({'height': '100% !important'})
        $('.o_thread_window.o_in_home_menu ').fadeIn()
        obst_chat_box = true
        if ($('.openerp.o_livechat_button.d-print-none.o_bottom_fixed_element').css('display') == 'block'){
            $('.openerp.o_livechat_button.d-print-none.o_bottom_fixed_element').click()
        }else{
             $('.o_thread_window_title').click()
        }
    },
    /**
     * Function to handle the close event of the chat box.
     *
     * This function animates the `.chat-box-container` element to the left by 110%, removes the class
     * `toggle_active` from it and fades out the `.chat-box-ui-block` element. The `overflow-y` property
     * of the element with id `wrapwrap` is set to `scroll` and the display property of the element with
     * id `ObLiveChatPopUp` is set to `block`.
     *
     * @function
     * @memberof module:_onClickCloseChatBox
     */
    _onClickCloseChatBox: function () {
            $('.chat-box-container').animate({
                left: '110%'
            }, 250);
            $('.chat-box-container').removeClass('toggle_active');
            $('.chat-box-ui-block').fadeOut(250)
            $('#wrapwrap').css('overflow-y', 'scroll')
            $('.obst_Ellipse_has_notify').css({'background-color': 'white'})
            $('.obst-live-chat-icon').css({'color': 'black'})
            $('#ObLiveChatPopUp').css({'display': 'block'})
        },
    });


LivechatButton.include({
    selector: '#wrapwrap',
     events: _.extend({}, LivechatButton.prototype.events, {
        'keydown .obst_o_composer_text_field': '_obstOnKeydown',
        }),

    start: function () {
        this.$el.text(this.options.button_text);
        if (this.options.chat_request_session){
            if (! this.options.chat_request_session.folded){
                $('.chat-box-ui-block').fadeIn(250)
            }
        }
        $('.o_thread_window.o_in_home_menu').css({'height': '0px !important'})
        var html = $('#wrapwrap').last()
            html.append('<div id="ObLiveChatPopUp" class="ob_livechat_pop_up"><div class="obst_Ellipse_has_notify open-chat-box"><i class="fa-solid fa-message obst-live-chat-icon"></i></div></div>')
        return this._super();
    },

    _onNotification: function (notifications) {
        var self = this;
        _.each(notifications, function (notification) {
            if (notification.type == "mail.channel/new_message"){
                $('.obst_Ellipse_has_notify').css({'background-color': 'black'})
                $('.obst-live-chat-icon').css({'color': 'white'})
            }
            self._handleNotification(notification);
        });
    },
});


ObstAbstractThreadWindow.include({

    _onClickFold: function () {
        this._super.apply(this, arguments);
        if (obst_chat_box){
            $('.chat-box-ui-block').fadeIn(250)
            $('.o_thread_window.o_in_home_menu').height('100%')
        }
        else{
            $('.chat-box-ui-block').fadeOut(250)
            $('.o_thread_window.o_in_home_menu').fadeOut(250)
            $('.o_thread_window.o_in_home_menu').css({'height': '0px !important'})
        }
        obst_chat_box = false
        $('.obst_Ellipse_has_notify').css({'background-color': 'white'})
        $('.obst-live-chat-icon').css({'color': 'black'})
    },

});

});
