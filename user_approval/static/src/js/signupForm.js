odoo.define('user_approval.signupForm', function (require) {
'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc')
    publicWidget.registry.signupForm = publicWidget.Widget.extend({
        selector: '#signupForm',
        events: {
            'change #country': 'countryChange'
        },
        countryChange: function () {
            rpc.query({
                route: "/country/change",
                params: {'country':$('#country').val()},
            }).then(function (data) {
                $('#state option').each(function() {
                    $(this).remove();
                });
                data.forEach(function(el) {
                    $('#state').append('<option value="' + el["id"] + '">' + el["name"] + '</option>');
                });
            });
        },
    });
});
