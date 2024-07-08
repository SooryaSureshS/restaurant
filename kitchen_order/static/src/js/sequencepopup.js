odoo.define('kitchen_order.sequencepopup', function(require) {
    'use strict';

    const { useState } = owl;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    // formerly NumberPopupWidget
    class NumberPopupSequencePopup extends AbstractAwaitablePopup {
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
            useListener('prepend', this.prepend);
            useListener('sub_div_button', this.sub_div_button);
            let startingBuffer = '';
            if (typeof this.props.startingValue === 'number' && this.props.startingValue > 0) {
                startingBuffer = this.props.startingValue.toString();
            }
            this.state = useState({ buffer: startingBuffer });
            this.employee = useState(this.props.employee);
            this.order_data = useState(this.props.order);
            this.order_id = useState(this.props.order_id);
            this.type = useState(this.props.type);
            this.position = false;
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
        prepend (){
            console.log("prepend",this)
            var input = $('.quantity').val();
            if(input > 1 ){
                $('.quantity').val(parseInt(input) - 1);
            }
        }
        append (){
            console.log("append",this)
            var input = $('.quantity').val();
            $('.quantity').val(parseInt(input) + 1);

        }
        sub_div_button(event) {

            const { mode } = event.detail;
            this.position = $(event.target).text();
//            $('.sub_div').each(function(){
//                $(this).find('span').css('color','red !important;');
//            });
//            $(event.target).css('color','red');
            $('#selected_position').text($(event.target).text());
        }
        sendInput(key) {

            this.trigger('numpad-click-input', { key });
        }
        getPayload() {
            return NumberBuffer.get();
        }

        async confirm_position() {
            var self = this;
            var all_order = this.env.pos.orderListallNew;
            var all_order_new = [];
            var change_value = {};
             for (var i=0;i<all_order.length; i++){

                       var order_id_order=0;
                       if (all_order[i].type=='sale'){
                       order_id_order = all_order[i].order_id[1];
                       }
                       else{
                       order_id_order = all_order[i].order_id;
                       }
                      if (order_id_order== self.order_id){
                      if (all_order[i].type=='sale'){
                       change_value["id"]=all_order[i].order_id;
                       }
                       else{
                       change_value["id"]=all_order[i].order_id;
                       }

                      change_value["type"]=all_order[i].type;
                      }
                      else{
                        all_order_new.push({"id":all_order[i].order_id,"type":all_order[i].type})
                      }
             }
             all_order_new.splice($('.quantity').val()-1,0,change_value);

             for (var i=0;i<all_order_new.length; i++){
                all_order_new[i]["sequence"]=i+1

             }
//             all_order_new.slice(self.position, {"id": self.order_id,"type":self.type});

            var ipaddress = this.env.pos.config.ipaddress;
            var send_sms = this.env.pos.config.send_sms;
            var  order_id = self.order_id;
            var dataToLog = {
                'order_id': order_id,
                'position': self.position,
                'type': self.type,
                'move_to': $('.quantity').val(),
                'all_order_new':all_order_new

                }
            $.ajax({
                type: 'POST',
                url: ipaddress+'/upadate/order/position',
                async: true,
                processData: true,
                contentType: "application/json; charset=ytf-8",
                beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
            });


                self.confirm();

//                await self.showPopup('ErrorPopup', {
//                    title: this.env._t('Incorrect Password'),
//                });
                return true;
        }
    }
    NumberPopupSequencePopup.template = 'SequencePopup';
    NumberPopupSequencePopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Confirm ?',
        body: '',
        cheap: false,
        startingValue: null,
        isPassword: false,
    };

    Registries.Component.add(NumberPopupSequencePopup);

    return NumberPopupSequencePopup;
});
