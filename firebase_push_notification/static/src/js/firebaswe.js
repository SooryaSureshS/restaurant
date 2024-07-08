odoo.define('firebase_push_notification.firebaswe', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var VariantMixin = require('sale.VariantMixin');
var ajax = require('web.ajax');

var rpc = require('web.rpc');

var QWeb = core.qweb;
//importScripts('https://www.gstatic.com/firebasejs/7.14.6/firebase-app.js');
//importScripts('https://www.gstatic.com/firebasejs/7.14.6/firebase-messaging.js');
publicWidget.registry.FirebasePortal = publicWidget.Widget.extend({
    selector: '#wrapwrap',
    events: {

    },
    template: null,
    jsLibs: [
//        '/mass_mailing/static/src/js/mass_mailing_link_dialog_fix.js',
//        '/mass_mailing/static/src/js/mass_mailing_snippets.js',
//         'https://www.gstatic.com/firebasejs/7.14.6/firebase-app.js',
//          'https://www.gstatic.com/firebasejs/7.14.6/firebase-messaging.js',
    ],
    assetLibs: null,
    /**
     * @constructor
     */
    init: function () {
        var self = this;

        ajax.jsonRpc('/notification/firebase/info', 'call', {'state': 'on'})
            .then(function (result) {
                if (result['enable'] == 'True') {
                    if (result['enable_user']) {
                        self._firbase_trigger(result);
                    }
                }
            });

        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    _firbase_trigger: function (result) {
        var self = this;
        try{
            if (window.location.protocol == "https:") {

                    ajax.loadJS('/firebase_push_notification/static/src/js/firebase_app.js').then(function () {
                         ajax.loadJS('/firebase_push_notification/static/src/js/firebase_messages.js').then(function () {
                             var firebaseConfig = {
                                apiKey: result['api_key'],
                                authDomain: result['authDomain'],
                                projectId: result['projectId'],
                                storageBucket: result['storage_bucket'],
                                messagingSenderId:  result['messaging_senderId'],
                                appId: result['app_id']
                            };

                                firebase.initializeApp(firebaseConfig);
                                const messaging=firebase.messaging();

                                function IntitalizeFireBaseMessaging() {
                                    messaging
                                        .requestPermission()
                                        .then(function () {
                                            console.log("Notification Permission",messaging.getToken());
                                            return messaging.getToken();
                                        })
                                        .then(function (token) {
                                             ajax.jsonRpc('/notification/firebase/user/save', 'call', {'token': token})
                                                    .then(function (result) {
                                                        console.log("info",result)
                                                    });
//                                            console.log("Token : "+token);
//                                            document.getElementById("token").innerHTML=token;
                                        })
                                        .catch(function (reason) {
                                            console.log("dfdfdfdfdfd",reason);
                                        });
                                }

                                messaging.onMessage(function (payload) {
                                    console.log(payload);
                                    const notificationOption={
                                        body:payload.notification.body,
                                        icon:payload.notification.icon
                                    };

                                    if(Notification.permission==="granted"){
                                        var notification=new Notification(payload.notification.title,notificationOption);

                                        notification.onclick=function (ev) {
                                            ev.preventDefault();
                                            window.open(payload.notification.click_action,'_blank');
                                            notification.close();
                                        }
                                    }

                                });
                                messaging.onTokenRefresh(function () {
                                    messaging.getToken()
                                        .then(function (newtoken) {
                                            console.log("New Token : "+ newtoken);
                                        })
                                        .catch(function (reason) {
                                            console.log(reason);
                                        })
                                })
                                IntitalizeFireBaseMessaging();






//                        firebase.initializeApp(firebaseConfig);
//                        const messaging = firebase.messaging();
//                        messaging
//                            .requestPermission()
//                            .then(function () {
//                //                MsgElem.innerHTML = "Notification permission granted."
//                                console.log("Notification permission granted.");
//                                console.log("Notification permission granted.",messaging.getToken());
////
////                                // get the token in the form of promise
//                                return messaging.getToken()
////                        });
//                        });
                        });
                });
//
                }
        }
        catch(e){
				errorHandler.error('element parse error: '+e);
		}
    },
    });
});

