odoo.define('pos_user_pin_validation.PaymentUserValidation', function(require) {
    'use strict';

    const { Gui } = require('point_of_sale.Gui');
    const { Component } = owl;
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    var pos_model = require('point_of_sale.models');
    pos_model.load_fields('hr.employee', 'employee_pin');
    const current = Component.current;

    const CustomButtonPopupScreen = (ProductScreen) =>
        class extends ProductScreen {
        constructor() {
            super(...arguments);
            }
            async _onClickPay() {
            var self = this;
            const {confirmed, payload} = await this.showPopup("NumberPopup", {
                title: this.env._t("Enter PIN"),
                startingValue: 0,
            });
            if (confirmed) {
                var val = parseFloat(payload);

                var records = self.rpc({
                    model: 'hr.employee',
                    method: 'get_barcodes_and_pin_hashed',
                    args: [self.env.pos.user],

                })
                .then(function (data) {
                    window.data = data;
                        if (val == window.data){
                            self.showScreen('PaymentScreen')
                        } else {
                            Gui.showPopup("ErrorPopup", {
                                'title': self.env._t("PIN Error"),
                                'body':  self.env._t('Invalid PIN'),
                            });
                        }

                   });
            }
            if (self.env.pos.config.iface_holiday){
                if(self.env.pos.config.surcharge_product){
                    

                    var surcharge = self.env.pos.db.get_product_by_id(self.env.pos.config.surcharge_product[0]);
                    
                    var order = self.env.pos.get_order()
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

                    var given_val = parseFloat(self.env.pos.config.amount);

                    if (self.env.pos.config.start_date && self.env.pos.config.end_date && self.env.pos.config.pricing_method && parseFloat(self.env.pos.config.amount)){
                        if (today >= self.env.pos.config.start_date && today <= self.env.pos.config.end_date){
                            if (self.env.pos.config.pricing_method == 'percentage'){
                                   if(self.env.pos.get_order().get_total_without_tax()){

                                        var amount_percentage = self.env.pos.get_order().get_total_without_tax()*self.env.pos.config.amount/100;
                                        self.env.pos.get_order().add_product(surcharge, {
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
                            if (self.env.pos.config.pricing_method == 'amount'){
                                    if(self.env.pos.get_order().get_total_without_tax()){
                                            var amount_percentage = self.env.pos.get_order().get_total_without_tax()*this.env.pos.config.amount/100;
                                            self.env.pos.get_order().add_product(surcharge, {
                                                      quantity: 1,
                                            });
                                            order.get_orderlines().forEach(function (orderline) {
                                                        var product = orderline.product;
                                                        if(product.id == surcharge.id){
                                                            orderline.set_unit_price(given_val);
                                                        }
                                            });
                                    }
                            }
                        }

                    }

                }
            }

            }
             async _clickDiscount() {
                    var self = this;
                    let selectedLine = this.env.pos.get_order().get_selected_orderline();
                    if (selectedLine){
                        const { confirmed, payload: inputPin } = await Gui.showPopup('NumberPopupUpdateTime', {
                                isPassword: false,
                                title: 'Discount ',
                                startingValue: null,

                         });
                         if (confirmed){
                                
                                if (inputPin){
                                        selectedLine.set_discount(inputPin);
                                }

                     }
                    }else{
                         await this.showPopup('ErrorPopup', {
                                title: 'Order Not Defined ',
                                body: 'Please select order line'
                         });
                    }

                }
        };

    Registries.Component.extend(ProductScreen, CustomButtonPopupScreen);
    return CustomButtonPopupScreen;
    });
