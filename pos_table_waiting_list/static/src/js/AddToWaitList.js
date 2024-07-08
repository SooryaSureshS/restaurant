odoo.define('pos_table_waiting_list.AddToWaitList', function(require) {
    'use strict';

    const { useState } = owl;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class AddToWaitList extends PosComponent {
        constructor() {
            super(...arguments);
        }

        addToWaitingList() {
            this.showScreen('WaitList');
        }
    }
    AddToWaitList.template = 'AddToWaitList';
    Registries.Component.add(AddToWaitList);
    return AddToWaitList;
});
