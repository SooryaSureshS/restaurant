odoo.define('pos_delivery_card_color.kvs_design', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PopupControllerMixin = require('point_of_sale.PopupControllerMixin')
    const Chrome = require('point_of_sale.Chrome');
    const KitchenscreenTemplate = require('kitchen_order.kitchenscreen_template');
    var models = require('point_of_sale.models');

    const KitchenscreenTemplateNew = (KitchenscreenTemplate) =>
        class extends KitchenscreenTemplate {
               constructor() {
                    super(...arguments);
               }
              get screen_loading (){
                     var self = this;
                     var w = window.innerWidth;
                     var h = window.innerHeight;
//                     if (w >700){
//                        $('#kitchen-screen-new-data .subwindow-container .all-order-list-contents').height(h -300)
////                        $('#kitchen-screen-new-data .subwindow-container .all-order-list-contents').width(w -300)
//                        $('#kitchen-screen-new-data .subwindow-container .all-order-list-contents').width(1400)
//                     }
//                      $('#kitchen-screen-new-data ').show();

                }


        };
    Registries.Component.extend(KitchenscreenTemplate, KitchenscreenTemplateNew);

    return KitchenscreenTemplate;

});