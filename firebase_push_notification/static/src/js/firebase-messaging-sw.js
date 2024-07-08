importScripts('https://www.gstatic.com/firebasejs/7.14.6/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.14.6/firebase-messaging.js');

var firebaseConfig = {
      apiKey: "AIzaSyDIBiK_BLA0qdMfG9shW4v0UwDSaLCZLBM",
        authDomain: "skyprodev-cc02b.firebaseapp.com",
        projectId: "skyprodev-cc02b",
        storageBucket: "skyprodev-cc02b.appspot.com",
        messagingSenderId: "321898949292",
        appId: "1:321898949292:web:f36dc47fdf74d1ccf20d09",
};

firebase.initializeApp(firebaseConfig);
const messaging=firebase.messaging();

messaging.setBackgroundMessageHandler(function (payload) {
    console.log(payload);
    const notification=JSON.parse(payload);
    const notificationOption={
        body:notification.body,
        icon:notification.icon
    };
    return self.registration.showNotification(payload.notification.title,notificationOption);
});