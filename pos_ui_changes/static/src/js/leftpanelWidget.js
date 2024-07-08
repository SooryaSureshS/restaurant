odoo.define('pos_ui_changes.leftpanelWidget', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PopupControllerMixin = require('point_of_sale.PopupControllerMixin')
    const Chrome = require('point_of_sale.Chrome');
    var models = require('point_of_sale.models');
      const { posbus } = require('point_of_sale.utils');

    /* Return Order button for view the kitchen screen for managers */
    class LeftPanelWidget extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        mounted() {
            posbus.on('table-set', this, this.render);
        }
        willUnmount() {
            posbus.on('table-set', this);
        }
        get table() {
            return (this.env.pos && this.env.pos.table) || null;
        }
        get floor() {
            const table = this.table;
            return table ? table.floor : null;
        }
        get hasTable() {
            return this.table !== null;
        }
        async onClick() {
//            this.showScreen('OrderTable');
            console.log("hide and collapse",this);
//            $('.product-screen .screen-full-width .leftpane .order-container').hide('swing');
//            $('.product-screen .screen-full-width .leftpane .pads').hide('swing');
//            $('.product-screen .screen-full-width:first-child').addClass('hide_comp');
        }
        backToFloorScreen() {
            var $target = $('.product-screen .screen-full-width .leftpane')[0]
            if ($($target).hasClass('left_pane_css')){
                $($target).css('max-width', '500px;');
               $($target).animate({width: "500px"}, 1000, function() {
                    $($target).removeClass('left_pane_css');
               });
//               $($target).show('swing');
//
               $('#fa_left_collapse').show();
               $('#fa_right_collapse').hide();
            }else{
                $($target).addClass('left_pane_css');
                $($target).animate({width: "0px"},1000);

////                $($target).hide('swing');
//                $($target).toggle("slide");
//                $($target).addClass('hide_comp');
                $('#fa_left_collapse').hide();
                $('#fa_right_collapse').show();
            }

        }
    }

    LeftPanelWidget.template = 'LeftPanelWidget';

    Registries.Component.add(LeftPanelWidget);

    return LeftPanelWidget;


});