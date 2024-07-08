odoo.define('website_loyalty_management.website_loyality_modal', function(require) {
    var ajax = require('web.ajax');
    const publicWidget = require('web.public.widget');



    publicWidget.registry.my_order_details_modal_confimation = publicWidget.Widget.extend({
        selector: '#o_cart_summary',
           events: {
        //        'scroll': '_movescroll',
        //        'mouseleave': '_onMouseLeave',_close_model_note
            'click ._o_btn_redeem_now': '_o_btn_redeem_now',

        },
        init: function () {

            this._super.apply(this, arguments);
            },
            _o_btn_redeem_now: function (ev){
            var self = this;

            var id_product = $('input[name="product_loyalty"]:checked').val();
            var selected_line = $('input[name="product_loyalty"]:checked').attr('id');
            var points_end = $('input[name="product_loyalty"]:checked').attr('points_end');

            if(selected_line && id_product){
             var $el = $(this);
            ajax.jsonRpc('/loyality/get_reward/', 'call', {'product_id':id_product,'selected_line':selected_line,'points_end':points_end})
            .then(function(response) {
               $('#modal_confimation').hide();
                window.location.reload();
            });
            }
            else{
                alert("Please select a product");
            }



        },
        /**
         * @override
         */

        });

    });