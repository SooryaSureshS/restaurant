odoo.define('knk_sale_return.returnPopup', function(require) {
    'use strict';

    const publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc')

    var _t = core._t
    var timeout;

    publicWidget.registry.returnPopup = publicWidget.Widget.extend({
        selector: '#wrap',
        events: {
            'click #confirmReturn': 'confirmReturn',
        },
        confirmReturn: function(event){
            var self = this;
            var order_id = event.currentTarget.getAttribute('data-order_id');
            var lines = {}
            $('.returnProductQty').each(function(){
                var qty = $(this).val();
//                var pid = this.getAttribute('data-pid');
                var lid = this.getAttribute('data-lid');
                lines[lid] = qty
            });
            ajax.jsonRpc('/my/order/return', 'call', {
                'order_id': order_id,
                'lines': lines,
            }).then(function (data) {
                // Handle the response from the server
                $('#returnMessage').text(data['message']);
                $('#returnMessage').css('padding', '20px');
                $('#returnMessage').css('background', '#E2E8E9');
                if (data['success']) {$('#returnMessage').css('color', 'green');}
                else{$('#returnMessage').css('color', 'red');}
                setTimeout(function(){
                    $('#returnModal').modal('hide');
                }, 2000);
            });
        },
    });
});