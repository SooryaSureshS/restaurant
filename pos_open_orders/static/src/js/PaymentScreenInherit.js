odoo.define('pos_open_orders.PaymentScreenInherit', function(require) {
"use strict";
var models = require('point_of_sale.models');


const PaymentScreen = require('point_of_sale.PaymentScreen');
const Registries = require('point_of_sale.Registries');
    const PaymentScreenInherit = (PaymentScreen) =>
    class  extends PaymentScreen {

    constructor() {
            super(...arguments);
//            this.TypeSetting();
        }
        get pos_order_type (){
            $('#hide_div_collapse').hide(); 
            var self = this;
            var order = self.env.pos.get_order();
            order.set_to_invoice(false);
            var pos_order_type = order.get_delivery_type();
            console.log("orderorder",order.get_open_order_ref())
            if (pos_order_type){
                if (pos_order_type == 'phone'){
                     $( ".phone" ).css('background', 'rgb(110,200,155)');
                }
                if (pos_order_type == 'dine_in'){
                     $( ".dine-in" ).css('background', 'rgb(110,200,155)');
                }
                if (pos_order_type == 'takeway'){
                     $( ".take-way" ).css('background', 'rgb(110,200,155)');
                }
                if (pos_order_type == 'delivery'){
                     $( ".delivery" ).css('background', 'rgb(110,200,155)');
                }

                $('#pos_order_type').val(pos_order_type);
            }
            return true
        }
       async Phone(){
            $('#table_no').hide();
            $("#pos_order_type").val("phone");
            $('.delivery-button').hide();
            $( ".phone" ).css('background', 'rgb(110,200,155)');
            $( ".take-way" ).css('background', '#e2e0e0bf');
            $( ".delivery" ).css('background', '#e2e0e0bf');
            $( ".dine-in" ).css('background', '#e2e0e0bf');
       }


       async DineIn(){
            $('#notes_delivery').hide();
            $( ".dine-in" ).css('background', 'rgb(110,200,155)');
            $( ".take-way" ).css('background', '#e2e0e0bf');
            $('#table_no').show();
            $("#pos_order_type").val("dine_in");

            $('.delivery-button').hide();
            $( ".delivery" ).css('background', '#e2e0e0bf');
            $( ".phone" ).css('background', '#e2e0e0bf');

             $( ".custom_select_btn1" ).css('background', '#e2e0e0bf');
             $( ".custom_select_btn2" ).css('background', '#e2e0e0bf');
             $( ".custom_select_btn3" ).css('background', '#e2e0e0bf');
             $( ".custom_select_btn4" ).css('background', '#e2e0e0bf');
             $( ".custom_select_btn5" ).css('background', '#e2e0e0bf');

        }
       async TakeWay(){
            $('#table_no').hide();
            $('#notes_delivery').hide();
            $( ".dine-in" ).css('background', '#e2e0e0bf');
            $( ".take-way" ).css('background', 'rgb(110,200,155)');
            $("#pos_order_type").val("takeway");

            $('.delivery-button').hide();
            $( ".delivery" ).css('background', '#e2e0e0bf');
             $( ".phone" ).css('background', '#e2e0e0bf');

            $( ".custom_select_btn1" ).css('background', '#e2e0e0bf');
             $( ".custom_select_btn2" ).css('background', '#e2e0e0bf');
             $( ".custom_select_btn3" ).css('background', '#e2e0e0bf');
             $( ".custom_select_btn4" ).css('background', '#e2e0e0bf');
             $( ".custom_select_btn5" ).css('background', '#e2e0e0bf');
        }
       async Delivery(){
            $('#table_no').hide();
            $("#pos_order_type").val("delivery");
            $('.delivery-button').show();
            $( ".delivery" ).css('background', 'rgb(110,200,155)');
            $( ".take-way" ).css('background', '#e2e0e0bf');
            $( ".dine-in" ).css('background', '#e2e0e0bf');
             $( ".phone" ).css('background', '#e2e0e0bf');
        }

       async validateOrderKitchen() {
           var select_order_type = $('#pos_order_type').val();
           console.log("phonnnnnnn",select_order_type);
           if (select_order_type=='dine_in'){
               var table_no=$('#table_no').val();
               if (!table_no){
                    if(this.env.pos.get_order().get_open_order_ref()){
                        return {'status':'ok'}
                    }else{
                         const { confirmed } = await this.showPopup('ConfirmPopup', {
                                title: this.env._t('Please select the Table Number'),
                                body: this.env._t(
                                    'You need to add the Table Number For Dine in.'
                                ),
                            });
                          return {'status':'not'};
                    }

               }
               else{
                    var order = this.currentOrder;
                    order.delivery_type='dine_in';
                    order.table_name=table_no;
                    return {'status':'ok'}
               }
           }
           else if (select_order_type=='takeway'){
                if (!this.currentOrder.get_client()) {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Please select the Customer'),
                        body: this.env._t(
                            'You need to select the customer For TakeWay order.'
                        ),
                    });
                    if (confirmed) {
                        this.selectClient();
                    }
                   return {'status':'not'};
                }else{
                    var order = this.currentOrder;
                    order.delivery_type='takeway';
                       return {'status':'ok'}
            //        $('#customer_name').hide();
                }
           }
           else if (select_order_type=='delivery'){
                var order = this.currentOrder;
                var select_order_delivery = $('#pos_order_type_delivery').val();
                var notes_delivery = $('#notes_delivery').val();
                if (select_order_delivery=='woosh'){
                    if(!notes_delivery){
                         const { confirmed } = await this.showPopup('ConfirmPopup', {
                                    title: this.env._t('Note is Missing'),
                                    body: this.env._t(
                                        'You need to add the Note.'
                                    ),
                                });
                         return {'status':'not'};
                        }
                        else{
                          order.delivery_type='woosh';
                          order.delivery_note=notes_delivery;
                          return {'status':'ok'}
                        }
                }
                   else if(select_order_delivery=='uber'){
                        if(!notes_delivery){
                            const { confirmed } = await this.showPopup('ConfirmPopup', {
                                    title: this.env._t('Note is Missing'),
                                    body: this.env._t(
                                        'You need to add the Note.'
                                    ),
                            });
                            return {'status':'not'};
                        }
                        else{
                            order.delivery_type='uber';
                            order.delivery_note=notes_delivery;
                            return {'status':'ok'}
                        }

                   }
                   else if(select_order_delivery=='door'){
                        if(!notes_delivery){
                         const { confirmed } = await this.showPopup('ConfirmPopup', {
                                    title: this.env._t('Note is Missing'),
                                    body: this.env._t(
                                        'You need to add the Note.'
                                    ),
                                });
                                 return {'status':'not'};
                        }

                        else{
                        order.delivery_type='door';
                        order.delivery_note=notes_delivery;
                        return {'status':'ok'}
                        }

                   }
                    else if(select_order_delivery=='menulog'){
                        if(!notes_delivery){
                         const { confirmed } = await this.showPopup('ConfirmPopup', {
                                    title: this.env._t('Note is Missing'),
                                    body: this.env._t(
                                        'You need to add the Note.'
                                    ),
                                });
                                 return {'status':'not'};
                        }

                        else{

                         order.delivery_type='menulog';
                         order.delivery_note=notes_delivery;
                         return {'status':'ok'}
                        }

                    }
                    else if (select_order_delivery=='deliveroo'){
                        if(!notes_delivery){
                         const { confirmed } = await this.showPopup('ConfirmPopup', {
                                    title: this.env._t('Note is Missing'),
                                    body: this.env._t(
                                        'You need to add the Note.'
                                    ),
                                });
                                 return {'status':'not'};
                        }
                        else{
                        order.delivery_type='deliveroo';
                        order.delivery_note=notes_delivery;
                        return {'status':'ok'}

                        }
                    }
                    else{
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                                title: this.env._t('Delivery Method Missing'),
                                body: this.env._t(
                                    'Please select the Delivery method.'
                                ),
                            });
                             return {'status':'not'};

                    }

           }
           else if (select_order_type=='phone'){
                if (!this.currentOrder.get_client()) {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Please select the Customer'),
                        body: this.env._t(
                            'You need to select the customer For Phone order.'
                        ),
                    });
                    if (confirmed) {
                        this.selectClient();
                    }
                   return {'status':'not'};
                }else{
                    var self = this;
                    var order = self.currentOrder;
                    order.delivery_type='phone';


                       return {'status':'ok'}
            //        $('#customer_name').hide();
                }
           }

           else{
                this.showPopup('ErrorPopup', {
                                title: this.env._t('Order Type Not Selected'),
                                body: this.env._t("Please Choose Order Type."),
                            });
                          return {'status':'not'};
                }

           }
    }

    Registries.Component.extend(PaymentScreen, PaymentScreenInherit);
    return PaymentScreen;

});