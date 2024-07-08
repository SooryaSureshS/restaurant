odoo.define('pos_booking.EditTablePopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    // formerly TextInputPopupWidget
    class EditTablePopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
//            this.state = useState({ inputValue: this.props.startingValue });
            this.state = useState({ inputValue: this.props.startingValue });
            this.seat = useState({ seatValue: this.props.seatValue });
            this.inputRef = useRef('input');
            this.seatRef = useRef('seats');
        }
        mounted() {
            this.inputRef.el.focus();
        }
        getPayload() {
            return {
               'table_name': this.state.inputValue,
               'seats': this.seat.seatValue
            }
        }
    }
    EditTablePopup.template = 'EditTablePopup';
    EditTablePopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',
        startingValue: '',
    };

    Registries.Component.add(EditTablePopup);

    return EditTablePopup;
});
