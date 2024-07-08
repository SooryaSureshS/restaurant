odoo.define('pos_order_type.pos_order_type', function(require) {
"use strict";
var models = require('point_of_sale.models');


const PaymentScreen = require('point_of_sale.PaymentScreen');
const Registries = require('point_of_sale.Registries');
    const PosOrderType = (PaymentScreen) =>
    class  extends PaymentScreen {

    constructor() {
            super(...arguments);
            this.TypeSetting();
        }
    async TypeSetting(){
          $("#pos_order_type").val("nothing");
          var table =  this.env.pos.changed.selectedOrder;
          if (table){
          if (table.table){
          var table_name = table.table.floor.name;
          var name = table.table.name;
          this.table_names = table_name+'('+name+')';

          }
           else{
          this.table_names =''
          }
          }
          else{
          this.table_names =''
          }
    }


    async validateOrderKitchen() {
       var select_order_type = $('#pos_order_type').val();
       var current_order = this.currentOrder;
       var pos_order_note_payment = $('#pos_order_note_payment').val();
       console.log("opppop", pos_order_note_payment)
        current_order.pos_order_note_payment=pos_order_note_payment;
       console.log(select_order_type);
        if (select_order_type=='dine_in'){
        var table_no=$('#table_no').val();
        if (!table_no){
         const { confirmed } = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Please select the Table Number'),
                    body: this.env._t(
                        'You need to add the Table Number For Dine in.'
                    ),
                });
              return {'status':'not'};
        }
        else  {
        var order = this.currentOrder;
        order.delivery_type='dine_in';
        order.table_name=table_no;
        var pos_order_note_payment = $('#pos_order_note_payment').val();
        order.pos_order_note_payment=pos_order_note_payment;;
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
            }
            else{
               var order = this.currentOrder;
        order.delivery_type='takeway';
        var pos_order_note_payment = $('#pos_order_note_payment').val();
        order.pos_order_note_payment=pos_order_note_payment;;

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
                        var pos_order_note_payment = $('#pos_order_note_payment').val();
                        order.pos_order_note_payment=pos_order_note_payment;;

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
                        var pos_order_note_payment = $('#pos_order_note_payment').val();
                        order.pos_order_note_payment=pos_order_note_payment;;

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
                    var pos_order_note_payment = $('#pos_order_note_payment').val();
                    order.pos_order_note_payment=pos_order_note_payment;;

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
                    var pos_order_note_payment = $('#pos_order_note_payment').val();
                    order.pos_order_note_payment=pos_order_note_payment;;

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
                    var pos_order_note_payment = $('#pos_order_note_payment').val();
                    order.pos_order_note_payment=pos_order_note_payment;;

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
        else{
        this.showPopup('ErrorPopup', {
                        title: this.env._t('Order Type Not Selected'),
                        body: this.env._t("Please Choose Order Type."),
                    });
                  return {'status':'not'};
        }

    }

    async Delivery(){
        $('#table_no').hide();
        $("#pos_order_type").val("delivery");
        $('.delivery-button').show();
        $( ".delivery" ).css('background', 'rgb(110,200,155)');
        $( ".take-way" ).css('background', '#e2e0e0bf');
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

             $( ".custom_select_btn1" ).css('background', '#e2e0e0bf');
             $( ".custom_select_btn2" ).css('background', '#e2e0e0bf');
             $( ".custom_select_btn3" ).css('background', '#e2e0e0bf');
             $( ".custom_select_btn4" ).css('background', '#e2e0e0bf');
             $( ".custom_select_btn5" ).css('background', '#e2e0e0bf');

    }
    async custom_select_btn1(){
     $("#pos_order_type_delivery").val("woosh");
     $( ".custom_select_btn1" ).css('background', 'rgb(110,200,155)');
     $( ".custom_select_btn2" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn3" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn4" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn5" ).css('background', '#e2e0e0bf');
     $('#notes_delivery').show();
    }
    async custom_select_btn2(){
    $('#notes_delivery').show();
     $("#pos_order_type_delivery").val("uber");
     $( ".custom_select_btn1" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn2" ).css('background', 'rgb(110,200,155)');
     $( ".custom_select_btn3" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn4" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn5" ).css('background', '#e2e0e0bf');

    }
    async custom_select_btn3(){
    $('#notes_delivery').show();
         $("#pos_order_type_delivery").val("door");

    $( ".custom_select_btn1" ).css('background', '#e2e0e0bf');
    $( ".custom_select_btn2" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn3" ).css('background', 'rgb(110,200,155)');
     $( ".custom_select_btn4" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn5" ).css('background', '#e2e0e0bf');
    }
    async custom_select_btn4(){
    $('#notes_delivery').show();
    $("#pos_order_type_delivery").val("menulog");

     $( ".custom_select_btn1" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn2" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn3" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn4" ).css('background', 'rgb(110,200,155)');
     $( ".custom_select_btn5" ).css('background', '#e2e0e0bf');
    }
    async custom_select_btn5(){
    $('#notes_delivery').show();
    $("#pos_order_type_delivery").val("deliveroo");
    $( ".custom_select_btn1" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn2" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn3" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn4" ).css('background', '#e2e0e0bf');
     $( ".custom_select_btn5" ).css('background', 'rgb(110,200,155)');
    }


    async TakeWay(){
        $('#table_no').hide();
        $('#notes_delivery').hide();
        $( ".dine-in" ).css('background', '#e2e0e0bf');
        $( ".take-way" ).css('background', 'rgb(110,200,155)');
        $("#pos_order_type").val("takeway");

        $('.delivery-button').hide();
        $( ".delivery" ).css('background', '#e2e0e0bf');

        $( ".custom_select_btn1" ).css('background', '#e2e0e0bf');
         $( ".custom_select_btn2" ).css('background', '#e2e0e0bf');
         $( ".custom_select_btn3" ).css('background', '#e2e0e0bf');
         $( ".custom_select_btn4" ).css('background', '#e2e0e0bf');
         $( ".custom_select_btn5" ).css('background', '#e2e0e0bf');
    }
}
Registries.Component.extend(PaymentScreen, PosOrderType);
return PaymentScreen;



});