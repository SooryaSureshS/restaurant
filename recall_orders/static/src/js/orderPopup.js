odoo.define('recall_orders.orderPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    var models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
      const { useExternalListener } = owl.hooks;
    // formerly TextAreaPopupWidget
    // IMPROVEMENT: This code is very similar to TextInputPopup.
    //      Combining them would reduce the code.
    class RecallPopupsWidget extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        constructor() {
            super(...arguments);
//            useExternalListener(window, 'keyup', this._jsBarcode);
//               this.partner_id = useState({ partner_id: this.props.partner_id.id });
//               this.partner_name = useState({ partner_id: this.props.partner_id.name });
               this.ref = useState(this.props.ref);
               this.client = useState(this.props.client);
               this.result = useState(this.props.result);
        }

     }

    RecallPopupsWidget.template = 'RecallPopupsWidget';
    RecallPopupsWidget.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',

    };

    Registries.Component.add(RecallPopupsWidget);

    return RecallPopupsWidget;






});
