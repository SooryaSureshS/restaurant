odoo.define('pos_mcd_bill.OrderBillButtonPreview', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class OrderBillButtonPreview extends PosComponent {
        constructor() {
            super(...arguments);

        }
        async BillPreviewButton() {
            var self = this;
            var order = self.env.pos.get_order();
            this.showScreen('BillScreens',{'order': order, 'widget': self});
        }
    }
    OrderBillButtonPreview.template = 'OrderBillButtonPreview';

    Registries.Component.add(OrderBillButtonPreview);

    return OrderBillButtonPreview;
});