odoo.define('pos_public_holiday.surchargeHoliday', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const PaymentScreenStatus = require('point_of_sale.PaymentScreenStatus');

    const PaymentScreenStatusInherit = (PaymentScreenStatus) =>
    class  extends PaymentScreenStatus {

//    class PaymentPublicHoliday extends PosComponent {
        get get_surcharges() {
            return this.env.pos.get_order().get_surcharge();
        }
        get checkSurcharge() {
        var self = this;
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

                    if (this.env.pos.config.start_date && self.env.pos.config.end_date && self.env.pos.config.pricing_method && this.env.pos.config.amount){
                        if (today >= self.env.pos.config.start_date && today <= self.env.pos.config.end_date){
                            if (this.env.pos.config.pricing_method == 'percentage'){
                                   if(this.env.pos.get_order().get_total_without_tax()){

                                        var amount_percentage = self.env.pos.get_order().get_total_without_tax()*self.env.pos.config.amount/100;
                                        this.env.pos.get_order().add_product(surcharge, {
                                                  quantity: 1,
                                        });
                                        order.get_orderlines().forEach(function (orderline) {
                                                var product = orderline.product;
                                                if(product.id == surcharge.id){
                                                    orderline.set_unit_price(amount_percentage);
                                                }
                                        });
                                        order.set_surcharge(amount_percentage);
                                        return true

                                   }
                            }
                            if (this.env.pos.config.pricing_method == 'amount'){
                                    if(self.env.pos.get_order().get_total_without_tax()){
                                                                    console.log("hhhhhhhhhhhhhhhhhhhhh");

                                            var amount_percentage = self.env.pos.get_order().get_total_without_tax()*self.env.pos.config.amount/100;
                                            this.env.pos.get_order().add_product(surcharge, {
                                                      quantity: 1,
                                            });
                                            order.get_orderlines().forEach(function (orderline) {
                                                        var product = orderline.product;
                                                        if(product.id == surcharge.id){
                                                            orderline.set_unit_price(self.env.pos.config.amount);
                                                        }
                                            });
                                            order.set_surcharge(self.env.pos.config.amount);
                                                                            console.log("YYYYDBHSLJBLS**************");

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
        get surchargeAmount() {
            var self = this;
            console.log("surchargeeeeee",this.env.pos.get_order())
        }
        get currentOrder() {
            return this.env.pos.get_order();
        }
    }
//    PaymentPublicHoliday.template = 'PaymentPublicHoliday';

    Registries.Component.extend(PaymentScreenStatus, PaymentScreenStatusInherit);
    return PaymentScreenStatus;
});
