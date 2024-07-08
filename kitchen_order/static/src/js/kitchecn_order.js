odoo.define('kitchen_order.kitchecn_order', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PopupControllerMixin = require('point_of_sale.PopupControllerMixin')
    const Chrome = require('point_of_sale.Chrome');
    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');

    /* Loading Extra Fields */
    models.load_fields("res.users", ['kitchen_screen_user','pos_category_ids']);
    models.load_fields("pos.order.line", ['order_line_note','order_line_state']);
    models.load_fields("sale.order.line", ['order_line_note','order_line_state']);

    var utils = require('web.utils');

    const PosUsers = (Chrome) =>
        class Chromes extends Chrome {
/* User specific screens for Manager and cook*/
            get startScreen() {
                var self = this;

                if (this.state.uiState !== 'READY') {
                    console.warn(
                        `Accessing startScreen of Chrome component before 'state.uiState' to be 'READY' is not recommended.`
                    );
                }
//                var kitchen_screen = utils.get_cookie('kitchen_screen')
                if(self.env.pos.user.kitchen_screen_user === 'cook'){
                    $('.ticket-button').css("display", "none");
                    $('.pos-branding').css("display", "none");
//                    $('.orders_recall').css("display", "none");
                    return { name: 'kitchenScreenWidget' };
                }
                else if(self.env.pos.user.kitchen_screen_user === 'manager'){
                    $('.ticket-button').css("display", "none");
                    $('.pos-branding').css("display", "none");
//                    $('.orders_recall').css("display", "none");
                    return { name: 'kitchenScreenWidget' };
                }
                 else if(self.env.pos.user.kitchen_screen_user === 'admin'){
//                    if(kitchen_screen){
////                        $('.ticket-button').css("display", "none");
//                        $('.pos-branding').css("display", "none");
//                        return { name: 'kitchenScreenWidget' };
//                    }

                    if ((this.env.pos.config.iface_floorplan == true) && ((this.env.pos.config.floor_ids).length > 0)){
                        $('.pos-branding').css("display", "none");
                        return { name: 'FloorScreen'};
                    }
                    else{
                        $('.pos-branding').css("display", "none");
                        return{ name: 'ProductScreen'}
                    }

                }
                 else{
//                    if(kitchen_screen){
////                        $('.ticket-button').css("display", "none");
//                        $('.pos-branding').css("display", "none");
//                        return { name: 'kitchenScreenWidget' };
//                    }

                    if ((this.env.pos.config.iface_floorplan == true) && ((this.env.pos.config.floor_ids).length > 0)){
                        $('.pos-branding').css("display", "none");
                        return { name: 'FloorScreen'};
                    }
                    else{
                        $('.pos-branding').css("display", "none");
                        return{ name: 'ProductScreen'}
                    }

                }
            }
        }
        Registries.Component.extend(Chrome, PosUsers);

        return Chrome;

});
