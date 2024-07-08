odoo.define('pos_open_orders.openWidget', function(require) {
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
    class OpenWidgetButton extends PosComponent {
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
            console.log("hide and collapse",this);
        }
        FloorPlane_back () {
            var self = this;
            if (self.env.pos.config.iface_floorplan){
                $('#hide_div_collapse').hide();
                this.showScreen('FloorScreen');
            }else{
                const { confirmed: confirmedPopup } = this.showPopup('ConfirmPopup', {
                    title: 'Sorry Floor Plan Is Not available',
                    body: 'Please Configure Floor Plan',
                });
            }

        }

    }

    OpenWidgetButton.template = 'OpenWidgetButton';

    Registries.Component.add(OpenWidgetButton);

    return OpenWidgetButton;


});