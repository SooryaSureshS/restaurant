odoo.define('kitchen_order.chrome',function(require){
    "use strict"
    var models = require('point_of_sale.models');
    var chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');


//    models.load_fields('pos.payment.method', 'force_customer_selection');

     const chromeInherited = (chrome) =>
        class extends chrome {
            /**
             * @override
             */
        _onPlaySound({ detail: name }) {
            let src;
            if (name === 'error') {
                src = "/point_of_sale/static/src/sounds/error.wav";
            } else if (name === 'bell') {
                src = "/point_of_sale/static/src/sounds/bell.wav";
            } else if (name === 'order_up'){
                src = "/kitchen_order/static/src/wav/order_up.wav";
            }else if (name === 'notification_ring'){
                src = "/kitchen_order/static/src/wav/notification_ring.wav";
            }else if (name === 'marimba'){
                src = "/kitchen_order/static/src/wav/marimba.wav";
            }else if (name === 'sweet_message'){
                src = "/kitchen_order/static/src/wav/sweet_message_tone.wav";
            }else if (name === 'moto_e2'){
                src = "/kitchen_order/static/src/wav/moto_e2.wav";
            }else if (name === 'old_phone'){
                src = "/kitchen_order/static/src/wav/old_phone.wav";
            }else if (name === 'simple_ring'){
                src = "/kitchen_order/static/src/wav/simple_ring.wav";
            }else if (name === 'simple_ringtone1'){
                src = "/kitchen_order/static/src/wav/simple_ringtone1.wav";
            }else if (name === 'allison'){
                src = "/kitchen_order/static/src/wav/voice_male_female/Allison.wav";
            }else if (name === 'arnold'){
                src = "/kitchen_order/static/src/wav/voice_male_female/arnold.wav";
            }else if (name === 'obama'){
                src = "/kitchen_order/static/src/wav/voice_male_female/barack_obama.wav";
            }else if (name === 'bill-gates'){
                src = "/kitchen_order/static/src/wav/voice_male_female/bill_gates.wav";
            }else if (name === 'donald-trump'){
                src = "/kitchen_order/static/src/wav/voice_male_female/donald_trump.wav";
            }else if (name === 'lee'){
                src = "/kitchen_order/static/src/wav/voice_male_female/Lee.wav";
            }else if (name === 'leonard-nimoy'){
                src = "/kitchen_order/static/src/wav/voice_male_female/leonard_nimoy.wav";
            }else if (name === 'tom'){
                src = "/kitchen_order/static/src/wav/voice_male_female/Us_tom.wav";
            }else if (name === 'zoe'){
                src = "/kitchen_order/static/src/wav/voice_male_female/zoe.wav";
            }
            this.state.sound.src = src;
        }
        _actionAfterIdle() {
            console.log(" idle");
//            if (this.tempScreen.isShown) {
//                this.trigger('close-temp-screen');
//            }
//            const table = this.env.pos.table;
//            this.showScreen('FloorScreen', { floor: table ? table.floor : null });
        }

     }
    Registries.Component.extend(chrome, chromeInherited);

    return chrome;

});