odoo.define('pos_table_waiting_list.EditWaitListPopup', function(require) {
    'use strict';

    const { useState } = owl;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class EditWaitListPopup extends PosComponent {
        constructor() {
            super(...arguments);
        }

        editWaitingList() {
            console.log("ssssssssssssss", this.env.pos.EditWaitList)
            return this.env.pos.EditWaitList;
        }
        addToWaitingList() {
            this.showScreen('WaitList');
        }
    }
    EditWaitListPopup.template = 'EditWaitListPopup';
    Registries.Component.add(EditWaitListPopup);
    return EditWaitListPopup;
});
