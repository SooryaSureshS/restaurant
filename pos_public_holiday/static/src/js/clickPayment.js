odoo.define('pos_public_holiday.clickPayment', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const PaymentScreenStatus = require('point_of_sale.PaymentScreenStatus');
    const ProductScreen = require('point_of_sale.ProductScreen');

    const clickPayment = (ProductScreen) =>
    class  extends ProductScreen {

//    class PaymentPublicHoliday extends PosComponent {

     async _onClickPay() {
        console.log("addedss pro");
             if (this.env.pos.config.iface_holiday){
                if(this.env.pos.config.surcharge_product){
                    var surcharge = this.env.pos.db.get_product_by_id(this.env.pos.config.surcharge_product[0]);
                    var order = this.env.pos.get_order()
                    if (order) {
                        order.get_orderlines().forEach(function (orderline) {
                            var product = orderline.product;
                            if(product.id == surcharge.id){
                                orderline.set_quantity(0);
                            }
                        });
                    }

                    const d = new Date();
                    var date = new Date(d),
                        month = '' + (date.getMonth() + 1),
                        day = '' + date.getDate(),
                        year = date.getFullYear();
                    if (month.length < 2)
                        month = '0' + month;
                    if (day.length < 2)
                        day = '0' + day;
                    var today = [year, month, day].join('-')

                    order.date_order = today
                    if (this.env.pos.config.start_date && this.env.pos.config.end_date && this.env.pos.config.pricing_method && this.env.pos.config.amount){
                        if (order.date_order >= this.env.pos.config.start_date && order.date_order <= this.env.pos.config.end_date){
                            if (this.env.pos.config.pricing_method == 'percentage'){
                                   if(this.env.pos.get_order().get_total_without_tax()){

                                        var amount_percentage = this.env.pos.get_order().get_total_without_tax()*this.env.pos.config.amount/100;
                                        this.env.pos.get_order().add_product(surcharge, {
                                                  quantity: 1,
                                        });
                                        order.get_orderlines().forEach(function (orderline) {
                                                var product = orderline.product;
                                                if(product.id == surcharge.id){
                                                    orderline.set_unit_price(amount_percentage);
                                                }
                                        });
                                   }
                            }
                            if (this.env.pos.config.pricing_method == 'amount'){
                                    if(this.env.pos.get_order().get_total_without_tax()){
                                            var amount_percentage = this.env.pos.get_order().get_total_without_tax()*this.env.pos.config.amount/100;
                                            this.env.pos.get_order().add_product(surcharge, {
                                                      quantity: 1,
                                            });
                                            order.get_orderlines().forEach(function (orderline) {
                                                        var product = orderline.product;
                                                        if(product.id == surcharge.id){
                                                            orderline.set_unit_price(this.env.pos.config.amount);
                                                        }
                                            });
                                    }
                            }
                        }

                    }

                }
            }
            this.showScreen('PaymentScreen');
      }

     get checkSurcharge() {
            if (this.env.pos.config.iface_holiday){
                if(this.env.pos.config.surcharge_product){
                    var surcharge = this.env.pos.db.get_product_by_id(this.env.pos.config.surcharge_product[0]);
                    var order = this.env.pos.get_order()
                    if (order) {
                        order.get_orderlines().forEach(function (orderline) {
                            var product = orderline.product;
                            if(product.id == surcharge.id){
                                orderline.set_quantity(0);
                            }
                        });
                    }

                    const d = new Date();
                    var date = new Date(d),
                        month = '' + (date.getMonth() + 1),
                        day = '' + date.getDate(),
                        year = date.getFullYear();
                    if (month.length < 2)
                        month = '0' + month;
                    if (day.length < 2)
                        day = '0' + day;
                    var today = [year, month, day].join('-')
                    order.date_order = today
                    if (this.env.pos.config.start_date && this.env.pos.config.end_date && this.env.pos.config.pricing_method && this.env.pos.config.amount){
                        if (order.date_order >= this.env.pos.config.start_date && order.date_order <= this.env.pos.config.end_date){
                            if (this.env.pos.config.pricing_method == 'percentage'){
                                   if(this.env.pos.get_order().get_total_without_tax()){

                                        var amount_percentage = this.env.pos.get_order().get_total_without_tax()*this.env.pos.config.amount/100;
                                        this.env.pos.get_order().add_product(surcharge, {
                                                  quantity: 1,
                                        });
                                        order.get_orderlines().forEach(function (orderline) {
                                                var product = orderline.product;
                                                if(product.id == surcharge.id){
                                                    orderline.set_unit_price(amount_percentage);
                                                }
                                        });
                                        return true

                                   }
                            }
                            if (this.env.pos.config.pricing_method == 'amount'){
                                    if(this.env.pos.get_order().get_total_without_tax()){
                                            var amount_percentage = this.env.pos.get_order().get_total_without_tax()*this.env.pos.config.amount/100;
                                            this.env.pos.get_order().add_product(surcharge, {
                                                      quantity: 1,
                                            });
                                            order.get_orderlines().forEach(function (orderline) {
                                                        var product = orderline.product;
                                                        if(product.id == surcharge.id){
                                                            orderline.set_unit_price(this.env.pos.config.amount);
                                                        }
                                            });
                                            return true

                                    }
                            }
                        }

                    }

                }
            }else{
                return false
            }
        }

    }

    Registries.Component.extend(ProductScreen, clickPayment);
    return ProductScreen;
});
