odoo.define('pos_order_type_inherit.pos_order_type', function(require) {
"use strict";
var models = require('point_of_sale.models');


const PaymentScreen = require('pos_order_type.pos_order_type');
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

           this.table_names = '';

          }
          }
          else{
          let order = this.env.pos.get_order();
          var table_name = order.table.floor.name;
          var name = order.table.name;
          this.table_names = table_name+'('+name+')';

          }
    }







}

Registries.Component.extend(PaymentScreen, PosOrderType);
return PaymentScreen;



});