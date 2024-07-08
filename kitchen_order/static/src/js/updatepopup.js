odoo.define('kitchen_order.updatepopup', function(require) {
    'use strict';

    const { useState } = owl;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    // formerly NumberPopupWidget
    class NumberPopupUpdateTime extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {Boolean} props.isPassword Show password popup.
         * @param {number|null} props.startingValue Starting value of the popup.
         *
         * Resolve to { confirmed, payload } when used with showPopup method.
         * @confirmed {Boolean}
         * @payload {String}
         */
        constructor() {
            super(...arguments);
            useListener('accept-input', this.confirm);
            useListener('close-this-popup', this.cancel);
            let startingBuffer = '';
            if (typeof this.props.startingValue === 'number' && this.props.startingValue > 0) {
                startingBuffer = this.props.startingValue.toString();
            }
            this.state = useState({ buffer: startingBuffer });
            this.employee = useState(this.props.employee);
            this.order_data = useState(this.props.order);
            this.line_data = useState(this.props.line);
            NumberBuffer.use({
                nonKeyboardInputEvent: 'numpad-click-input',
                triggerAtEnter: 'accept-input',
                triggerAtEscape: 'close-this-popup',
                state: this.state,
            });
        }
        get decimalSeparator() {
            return this.env._t.database.parameters.decimal_point;
        }
        get inputBuffer() {
            if (this.state.buffer === null) {
                return '';
            }
            if (this.props.isPassword) {
                return this.state.buffer.replace(/./g, '•');
            } else {
                return this.state.buffer;
            }
        }
        sendInput(key) {

            this.trigger('numpad-click-input', { key });
        }
        getPayload() {
            return NumberBuffer.get();
        }
        async confirm_return() {
            var self = this;
//            if (self.props.employee.pin === Sha1.hash(NumberBuffer.get())) {
//                self.env.pos.get_order().remove_orderline(self.props.line);
                self.confirm();
//            } else {
//                await self.showPopup('ErrorPopup', {
//                    title: this.env._t('Incorrect Password'),
//                });
                return true;
//            }
        }
    }
    NumberPopupUpdateTime.template = 'NumberPopupUpdate';
    NumberPopupUpdateTime.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Confirm ?',
        body: '',
        cheap: false,
        startingValue: null,
        isPassword: false,
    };

    Registries.Component.add(NumberPopupUpdateTime);

    return NumberPopupUpdateTime;
});
