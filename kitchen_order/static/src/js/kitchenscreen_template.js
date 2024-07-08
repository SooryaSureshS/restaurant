odoo.define('kitchen_order.kitchenscreen_template', function (require) {
    'use strict';

    const { parse } = require('web.field_utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const { useErrorHandlers } = require('point_of_sale.custom_hooks');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { onChangeOrder } = require('point_of_sale.custom_hooks');
    const { Gui } = require('point_of_sale.Gui');
    var models = require('point_of_sale.models');
    var core = require('web.core');

    var _t = core._t;


    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;
    const ajax = require('web.ajax');
    var utils = require('web.utils');
    var session = require('web.session');
    var utils = require('web.utils');

    // load model for get the values for dropdown
    models.load_models({ //loaded model
        model: 'pos.session',
        fields: [],
        loaded: function(self, pos_order_line) {
//            self.pos_order_line = pos_order_line;
            ajax.rpc("/longpolling/pollings", {'session_id': self.env.pos.pos_session.id}).then(function (result) {
                    self.env.pos.pos_order_line = null;
                    self.env.pos.pos_order_line = result[0];
                    self.env.pos.sale_order_line = null;
                    self.env.pos.sale_order_line = result[1];
                    self.env.pos.uhc_product = result[5];

                });
        }
    });


    /*Kitchen Order Screen For Cook*/
    class kitchenScreenWidget extends PosComponent {
        constructor() {
                        super(...arguments);
                        useListener('close-screen', this.close);
                        useListener('line_select_pos', this.line_select_pos);
                        useListener('line_select_sale', this.line_select_sale);
                        useListener('line_deselect_pos', this.line_deselect_pos);
                        useListener('line_deselect_sale', this.line_deselect_sale);
                        this.order_print = false;
                        this.order_print_info = null;
                        this.pool_count = 0;
                        this.state_poll = [];
                        var currentdate = new Date();
                        this.pos_order_new = this.env.pos.pos_order_line;
                        this.sale_order_new = this.env.pos.sale_order_line;
                        this.orderListall = this.env.pos.orderListall;
                        this.curb_popup = this.env.pos.curb_popup;
                        this.uhc_product = this.env.pos.uhc_product;
                        this.collection_list_pre = [];
                        this.collection_list_new = [];
                        this.kitchen_screen_name = true;
                        this.count_print_refresh =0;
                        this.print_lock =false;
        }
        close() {
            $('#hide_div_collapse').show();
            this.showScreen('ProductScreen');
        }
        async sequence_popup(order_id,pos){
            const { confirmed, payload: inputPin } = await Gui.showPopup('NumberPopupSequencePopup', {
                                isPassword: false,
                                title: 'Bump Order Position:',
                                startingValue: null,
                                order_id: order_id,
                                type: pos,

                 });
                 if (confirmed){
                            console.log("updated")
                 }
        }
        async Shownote(order){
            var $targetUl = $('#all_if_sale'+order);
            if ($targetUl.hasClass('displayed')){
                $targetUl.removeClass('displayed');
                $targetUl.hide('swing')
            }else{
                $targetUl.addClass('displayed');
                $targetUl.show('swing')
            }
        }
        async Shownote_else(order){
            var $targetUl = $('#all_else_sale'+order);
            if ($targetUl.hasClass('displayed')){
                $targetUl.removeClass('displayed');
                $targetUl.hide('swing')
            }else{
                $targetUl.addClass('displayed');
                $targetUl.show('swing')
            }
        }
        async Shownote_sale_if(order){
            var $targetUl = $('#sale_if_sale'+order);
            if ($targetUl.hasClass('displayed')){
                $targetUl.removeClass('displayed');
                $targetUl.hide('swing')
            }else{
                $targetUl.addClass('displayed');
                $targetUl.show('swing')
            }
        }
        async Shownote_sale_else(order){
            var $targetUl = $('#sale_else_sale'+order);
            if ($targetUl.hasClass('displayed')){
                $targetUl.removeClass('displayed');
                $targetUl.hide('swing')
            }else{
                $targetUl.addClass('displayed');
                $targetUl.show('swing')
            }
        }
        async Shownote_all_if_pos(order){
            var $targetUl = $('#all_if_pos'+order);
            if ($targetUl.hasClass('displayed')){
                $targetUl.removeClass('displayed');
                $targetUl.hide('swing')
            }else{
                $targetUl.addClass('displayed');
                $targetUl.show('swing')
            }
        }
        async Shownote_all_else_pos(order){
            var $targetUl = $('#all_else_pos'+order);
            if ($targetUl.hasClass('displayed')){
                $targetUl.removeClass('displayed');
                $targetUl.hide('swing')
            }else{
                $targetUl.addClass('displayed');
                $targetUl.show('swing')
            }
        }
        async Shownote_pos_if(order){
            var $targetUl = $('#pos_if_pos'+order);
            if ($targetUl.hasClass('displayed')){
                $targetUl.removeClass('displayed');
                $targetUl.hide('swing')
            }else{
                $targetUl.addClass('displayed');
                $targetUl.show('swing')
            }
        }
        async Shownote_pos_else(order){
            var $targetUl = $('#pos_else_pos'+order);
            if ($targetUl.hasClass('displayed')){
                $targetUl.removeClass('displayed');
                $targetUl.hide('swing')
            }else{
                $targetUl.addClass('displayed');
                $targetUl.show('swing')
            }
        }
        async line_select_pos(order){
//            var $target = $(event.currentTarget)
//            var pro_line = $(event.detail.target).attr('data-line-id')

            var $target = $(event.currentTarget)
            if (order){
                var ipaddress = this.env.pos.config.ipaddress;
                var send_sms = this.env.pos.config.send_sms;
                var dataToLog = {'pro_line': order,}
                $(event.currentTarget).closest('div').css({'background':'yellow', 'padding':'10px'});
                $(event.currentTarget).closest('div').addClass("pos-mark");
                $.ajax({
                    type: 'POST',
                    url: ipaddress + '/upadate/pos/mark',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }

        }
        async line_deselect_pos(order){
//            var $target = $(event.currentTarget)
//            var pro_line = $(event.detail.target).attr('data-line-id')

            var $target = $(event.currentTarget)
            if (order){
                var ipaddress = this.env.pos.config.ipaddress;
                var send_sms = this.env.pos.config.send_sms;
                var dataToLog = {'pro_line': order,}
                if($(event.currentTarget).closest('div').hasClass("pos-mark")){
                    $(event.currentTarget).closest('div').css({'background':'white'});
                    $(event.currentTarget).closest('div').removeClass("pos-mark");
                }

                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/upadate/pos/unmark',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }

        }
        async line_select_sale(order){
//            var $target = $(event.currentTarget)
//            var pro_line = $(event.detail.target).attr('data-line-id')
            if (order){
                var ipaddress = this.env.pos.config.ipaddress;
                var send_sms = this.env.pos.config.send_sms;
                var dataToLog = {'pro_line': order,}
                $(event.currentTarget).closest('div').css({'background':'yellow', 'padding':'10px'});
                $(event.currentTarget).closest('div').addClass("pos-mark");
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/upadate/sale/mark',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }

        }
        async line_deselect_sale(order){
//            var $target = $(event.currentTarget)
//            var pro_line = $(event.detail.target).attr('data-line-id')
            if (order){
                var ipaddress = this.env.pos.config.ipaddress;
                var send_sms = this.env.pos.config.send_sms;
                var dataToLog = {'pro_line': order,}
                if($(event.currentTarget).closest('div').hasClass("pos-mark")){
                    $(event.currentTarget).closest('div').css({'background':'white'});
                    $(event.currentTarget).closest('div').removeClass("pos-mark");
                }
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/upadate/sale/unmark',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }

        }
        back_click (){
            this.kitchen_screen_name = false;
            $('#hide_div_collapse').show();
            this.showScreen('ProductScreen');
        }
        hello(){
            $("<article> Hi Roshni </article>").articulate('rate',.8).articulate('speak');
        }
        sale_count(){
            $("<article> Current sale order count is 10</article>").articulate('rate',.8).articulate('speak');
        }
        mounted() {
            var self = this;
            self.ajax_long_pooling()
            var idleTime = 0;
            $(document).ready(function () {
                // Increment the idle time counter every minute.
                var idleInterval = setInterval(timerIncrement, 25000); // 1 minute

                // Zero the idle timer on mouse movement.
                $(this).mousemove(function (e) {
                    idleTime = 0;
                });
                $(this).keypress(function (e) {
                    idleTime = 0;
                });
            });

            function timerIncrement() {
                idleTime = idleTime + 1;

                console.log("inddddd",idleTime);
                if (idleTime > 19) { // 20 minutes
//                    window.location.reload();
//                    self.ajax_long_pooling();
//                    self.mounted();
                    idleTime = 0
                    self.render();
                }
            }
//            var self = this;
//                var commands = {
//                      'alexa': function() {self.hello(); },
//                      'alexa sale': function() {self.sale_count(); }
//                    };
//
//                // OPTIONAL: activate debug mode for detailed logging in the console
//                annyang.debug();
//
//                // Initialize annyang
//                annyang.init(commands);
//
//                // OPTIONAL: Set a language for speech recognition (defaults to English)
//                annyang.setLanguage('en');
//                annyang.addCallback('resultNoMatch', function() {
//                    self.hello();
//                });
//                // Start listening. You can call this here, or attach this call to an event, button, etc.
//                annyang.start();
        }
        async refresh_screen () {
           var self= this;


            if (self.env.pos.config.kitchen_order_receipt== true){
                       self.count_print_refresh=self.count_print_refresh+1;
                       if (self.count_print_refresh>10){

                       var order = self.orderListall;

                       _.each(self.orderListall,function(order) {
                        var print_session = self.env.pos.pos_session.id;
                        if (order.printed==false){
                         var includes = false;
                        }
                        else{
                       var includes = order.printed.includes(print_session);
                        }
//                        console.log("YYYYYYY hhhhhhhhhhhhhhhhhhhhhhhhh",self.count_print_refresh,order.printed);
                                if (!includes  && self.count_print_refresh>10){
                                   const printResult = self.PrintKVSReceipt(order);
//                                   console.log("YYYYYYY oRDRRRR",order,printResult);
                                   self.count_print_refresh=0;

                               }
                        });

                       }
                       }
            this.showScreen('kitchenScreenWidget');
            clearInterval(this.interval);
            this.render();

        }
        async PrintKvs2(order){
        var self= this;

            var receipt = QWeb.render('OrderReceiptKitchenScreenSale',{'printObj': order, 'widget': this});

                const printResult = await this.env.pos.proxy.printer.print_receipt(receipt);
                if (printResult.successful) {
                 this.bankEndSavePrintedInfo(order);
                    return true;
                } else {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: printResult.message.title,
                        body: 'Do you want to print using the web printer?',
                    });
                    if (confirmed) {
                        this.bankEndSavePrintedInfo(order);
                        // We want to call the _printWeb when the popup is fully gone
                        // from the screen which happens after the next animation frame.
                        return await this.receiptPrintWeb(receipt);
                    }
                    return await false;
                }
        }
        async PrintKVSReceipt(order){
            if (order.type=='pos'){
                var pos_order_line = order.lines;
                var req_print = 0;
                for(var i=0; i<pos_order_line.length;i++){
                    if (pos_order_line[i]['disable_print'] === false){
                        req_print = req_print + 1;
                    }
                }
                console.log(req_print)
                if (req_print > 0){
                    if (this.env.pos.proxy.printer) {
                        var receipt = QWeb.render('OrderReceiptKitchenScreenPOS',{'printObj': order, 'widget': this});
                        const printResult = await this.env.pos.proxy.printer.print_receipt(receipt);
                        if (printResult.successful) {
                         this.bankEndSavePrintedInfo(order);
                            return true;
                        } else {
                            const { confirmed } = await this.showPopup('ConfirmPopup', {
                                title: printResult.message.title,
                                body: 'Do you want to print using the web printer?',
                            });
                            if (confirmed) {
                                this.bankEndSavePrintedInfo(order);
                                // We want to call the _printWeb when the popup is fully gone
                                // from the screen which happens after the next animation frame.
                                return await this.receiptPrintWeb(receipt);
                            }
                            return await false;
                        }
                    }
                    else {
                        return await this.receiptPrintWeb();
                    }
                }
                else{
                    console.log("No Products For Print")
                }
            }
            if (order.type=='sale'){
                var sale_order_line = order.lines;
                var req_print = 0;
                for(var i=0; i<sale_order_line.length;i++){
                    if (sale_order_line[i]['disable_print'] === false){
                        req_print = req_print + 1;
                    }
                }
                console.log(req_print)
                if (req_print > 0){
                    if (this.env.pos.proxy.printer) {
                        var receipt = QWeb.render('OrderReceiptKitchenScreenSale',{'printObj': order, 'widget': this});
                        const printResult = await this.env.pos.proxy.printer.print_receipt(receipt);
                        if (printResult.successful) {
                         this.bankEndSavePrintedInfo(order);
                            return true;
                        } else {
                            const { confirmed } = await this.showPopup('ConfirmPopup', {
                                title: printResult.message.title,
                                body: 'Do you want to print using the web printer?',
                            });
                            if (confirmed) {
                                this.bankEndSavePrintedInfo(order);
                                // We want to call the _printWeb when the popup is fully gone
                                // from the screen which happens after the next animation frame.
                                return await this.receiptPrintWeb(receipt);
                            }
                            return await false;
                        }
                    }
                    else {
                        return await this.receiptPrintWeb();
                    }
                }
                else{
                    console.log("No Products For Print")
                }
            }


        }

        async bankEndSavePrintedInfo(order){
                            var self = this;
                            self.print_lock= false;
                            var print_session = self.env.pos.pos_session.id;
                             var ipaddress = self.env.pos.config.ipaddress;
                               if (order.type == 'pos'){
                                var dataToLog = {'order': order.order_id, 'print_session':print_session, 'order_type': 'pos'};
                                $.ajax({
                                    type: 'POST',
                                    url: ipaddress+'/order/print',
                                    async: true,
                                    processData: true,
                                    contentType: "application/json; charset=ytf-8",
                                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                                    success: function(data) {

                                    }
                                });
                            }
                            if (order.type == 'sale'){
                                var dataToLog = {'order':order.order_id[0], 'print_session':print_session, 'order_type': 'sale'};
                                $.ajax({
                                    type: 'POST',
                                    url: ipaddress+'/order/print',
                                    async: true,
                                    processData: true,
                                    contentType: "application/json; charset=ytf-8",
                                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),

                                    success: function(data) {

                                    },

                                });

                            }
        }

        async PrintOrderReceipt(type,id,status, order, printed){
            var self = this;
//            setTimeout(async () => {
                if (self.env.pos.config.kitchen_order_receipt== true){
                    var ipaddress = self.env.pos.config.ipaddress;
                    self.order_print_info = order;
                    var print_session = self.env.pos.pos_session.id

//                    if (self.order_print_info){
//                        if (printed==false){

//                        }
//                        else{
//                            var includes = printed.includes(print_session)
//                            console.log("tyuio", includes)
//                            if (includes==false){
//                                if (type == 'pos'){
//                                    var dataToLog = {'order': id, 'print_session':print_session, 'order_type': 'pos'};
//                                    $.ajax({
//                                        type: 'POST',
//                                        url: ipaddress+'/order/print',
//                                        async: true,
//                                        processData: true,
//                                        contentType: "application/json; charset=ytf-8",
//                                        beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
//                                        data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
//                                        success: function(data) {
//                                            if (data.result==true) {


//                                        },
//
//                                    });
//                                }
//                                if (type == 'sale'){
//                                    var dataToLog = {'order': id, 'print_session':print_session, 'order_type': 'sale'};
//                                    $.ajax({
//                                        type: 'POST',
//                                        url: ipaddress+'/order/print',
//                                        async: true,
//                                        processData: true,
//                                        contentType: "application/json; charset=ytf-8",
//                                        beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
//                                        data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
//                                        success: function(data) {
//                                            if (data.result==true) {
//                                                setTimeout(async () => {
//                                                   await self._printReceipt(order);
//                                                }, 10* 1000);
//                                            }
//                                        },
//
//                                    });
//
//                                }
//                            }
//                        }
//                    }
                }
//            }, 10* 1000);
        }

        flipRender(flip_id,preparation_estimation,type,id,status,kitchen_screen, order, printed) {
            try {
                var self = this;
                console.log('flip_id>>>>>>>>>>>>>>>>>>>>');
                console.log(flip_id);
//                self.PrintOrderReceipt(type,id,status, order, printed)
                var startDate = new Date();
                var endDate = new Date(preparation_estimation);
                var diff = endDate - startDate
                var minutes = Math.floor(diff/1000);

                $(document).ready(function() {
                    if (minutes >=0){
                        var clock;
                        if (status === 'preparing' || status === 'waiting'){
                             clock = $('#'+flip_id).FlipClock({
                                    clockFace: 'MinuteCounter',
                                    autoStart: false,
                                    callbacks: {
                                        stop: function() {

                                        }
                                    }
                                });
                                clock.setTime(minutes);
                                clock.setCountdown(true);
                                clock.start();

                        }
                        else{
                             var clock;

                            clock = $('#'+flip_id).FlipClock({
                                clockFace: 'MinuteCounter',
                                autoStart: false,
                                callbacks: {
                                    stop: function() {
                                        $('.message').html('The clock has stopped!')
                                    }
                                }
                            });
                        }
                    }else{
                        var clock;
                        clock = $('#'+flip_id).FlipClock({
                            clockFace: 'MinuteCounter',
                            autoStart: false,
                            callbacks: {
                                stop: function() {
                                    $('.message').html('The clock has stopped!')
                                }
                            }
                        });
                        var startDate1 = new Date();
                        var endDate1 = new Date(preparation_estimation);
                        var diff1 = endDate1 - startDate1
                        var minutes1 = Math.floor(diff1/1000);

                        if (minutes1 <0){
                            if (kitchen_screen==true){
                                if (type == 'pos'){
                                    var ipaddress = self.env.pos.config.ipaddress;
                                    var dataToLog = {'order': id,'type': 'pos'};
                                    $.ajax({
                                        type: 'POST',
                                        url: ipaddress+'/upadate/timeout',
                                        async: true,
                                        processData: true,
                                        contentType: "application/json; charset=ytf-8",
                                        beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                                        data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                                    });
                                }
                                if (type == 'sale'){
                                    var ipaddress = self.env.pos.config.ipaddress;
                                        var dataToLog = {'order': id,'type': 'sale'};
                                        $.ajax({
                                            type: 'POST',
                                            url: ipaddress+'/upadate/timeout',
                                            async: true,
                                            processData: true,
                                            contentType: "application/json; charset=ytf-8",
                                            beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                                            data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                                        });
                                }

                            }
                            var startDate2 = new Date();
                            var endDate2 = new Date(preparation_estimation);
                            var diff2 = startDate2 - endDate2
                            var minutes2 = Math.floor(diff2/1000);
                            clock.setTime(minutes2);
                            clock.start();
                        }
                    }
                });
            }
            catch (err){
                console.log(err)
            }
        }
        get orderList() {
            var self = this;
            var order = this.env.pos.get_order();
            var time_out = this.env.pos.config.time_out_screens;

            return this.pos_order_new;
        }
        get orderListAllrecord() {
//            var self = this;
//            var order = this.env.pos.get_order();
//            var time_out = this.env.pos.config.time_out_screens;

            return this.orderListall;
        }

        ajax_long_pooling() {
            var self = this;
            self.pool_count = self.pool_count + 1;
            var limit_reload = this.env.pos.config.limit_reload;
            var time_out = this.env.pos.config.time_out_screens;
            var long_pooling_port = this.env.pos.config.long_pooling_port;
            var ipaddress = this.env.pos.config.ipaddress;
            var order = this.env.pos.get_order();
//            if (order.get_screen_data().name == 'kitchenScreenWidget') {
            if (this.kitchen_screen_name) {

                var dataToLog = {'session_id':this.env.pos.pos_session.id};
                 $.ajax({
                        type: 'POST',
                        url: ipaddress+'/longpolling/pollings',
                        async: true,
                        processData: true,
                        contentType: "application/json; charset=ytf-8",
                        beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                        data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),

                        success: function(data) {
                            if (data.result) {
                                self.env.pos.pos_order_line = null;
                                self.env.pos.sale_order_line = null;
                                self.pos_order_new = data.result[0];
                                self.sale_order_new = data.result[1];
                                self.uhc_product = data.result[5];
                                self.orderListall = data.result[6];
                                self.curb_popup = data.result[7];
                                self.env.pos.orderListallNew = data.result[6];
                                self.refresh_screen();
                                self.render();
                                if (data.result[4]){
                                    setTimeout(function(){
//                                              self.showPopup('ConfirmPopup', {
//                                                title: self.env._t('You Have New Message'),
//                                                body: self.env._t(data.result[4]),
//                                            });
                                             const { confirmed: confirmedPopup } = self.showPopup('ConfirmPopup', {
                                                    title: 'You Have New Message',
                                                    body: data.result[4],
                                                });
//                                            $("<article>"+data.result[4]+ "</article>").articulate('rate',.8).articulate('speak');
                                           }, 10000);
                                }

                                var sale_order = data.result[1];
                                var total_sale = [];
                                var current_sale = [];
                                var new_sale = false;
                                var var1;

                                for (var i=0;i<sale_order.length; i++){
                                    current_sale.push(sale_order[i].id)
                                }
                                var previous_sale = self.sale_order_records

                                if (previous_sale !== undefined){
                                    if (current_sale.length > previous_sale.length){
                                        new_sale = false
                                    }
                                    else{
                                        new_sale = true
                                    }

                                }

//                              POS
                                var pos_order = data.result[0];
                                var total_pos = [];
                                var current_pos = [];
                                var new_pos = false;

                                for (var i=0;i<pos_order.length; i++){
                                    current_pos.push(pos_order[i].order_id)
                                }
                                var previous_pos = self.pos_order_records

                                if (previous_pos !== undefined){
                                    if (current_pos.length > previous_pos.length){
                                        new_pos = false
                                    }
                                    else{
                                        new_pos = true
                                    }
                                }

//                              SALE AND POS
                                var bell = false;
                                var collection = false;

                                self.collection_list_new = [];
                                _.each(self.orderListall, function (pos_data) {
                                    _.each(pos_data.lines, function (pos_line) {
                                       if (pos_line.order_line_state === 'waiting'){
                                            bell = true
                                       }
                                       if (pos_line.order_line_state === 'ready'){
                                            self.collection_list_new.push(pos_line);
                                       }
                                    });
                                });
                                _.each(self.pos_order_new, function (pos_data) {
                                    _.each(pos_data.lines, function (pos_line) {
                                       if (pos_line.order_line_state === 'waiting'){
                                            bell = true
                                       }
                                       if (pos_line.order_line_state === 'ready'){
                                            self.collection_list_new.push(pos_line);
                                       }
                                    });
                                });
                                _.each(self.sale_order_new, function (sale_data) {
                                     _.each(sale_data.lines, function (sale_line) {
                                        if (sale_line.order_line_state === 'waiting'){
                                            bell = true
                                        }
                                         if (sale_line.order_line_state === 'ready'){
                                            self.collection_list_new.push(sale_line);
                                       }
                                     });
                                });
                                 if (self.curb_popup){
                                    _.each(self.sale_order_new, function (sale_data_location) {
                                        if (sale_data_location['state'] === 'sale'){
                                            if (sale_data_location['updated_location']){
                                                if(self.env.pos.config.kerbside_pickup_sound){
                                                    if(self.env.pos.config.kerbside_pickup_tune){
                                                        Gui.playSound(self.env.pos.config.kerbside_pickup_tune)
                                                    }
                                                }
                                                self.showPopup('ConfirmPopup', {
                                                        title: 'Location Updated',
                                                        body: "Order Number:" + sale_data_location['order_id'][1],
                                                });
                                                var1 = sale_data_location['order_id'][0]
                                                self.rpc(
                                                    {
                                                        model: 'sale.order',
                                                        method: 'action_location_update',
                                                        args: [var1],
                                                    },
                                                )
                                            }
                                        }
                                    });
                                 }else{
                                      _.each(self.sale_order_new, function (sale_data_location) {
                                            if (sale_data_location['state'] === 'sale'){
                                                if (sale_data_location['updated_location']){
                                                    var1 = sale_data_location['order_id'][0]
                                                    self.rpc(
                                                        {
                                                            model: 'sale.order',
                                                            method: 'action_location_update',
                                                            args: [var1],
                                                        },
                                                    )
                                                }
                                            }
                                      });
                                }

                                if (_.isEqual(self.collection_list_new, self.collection_list_pre) == false){
                                    self.collection_list_pre = self.collection_list_new;
                                    collection = true
                                }else{
                                    self.collection_list_pre = self.collection_list_new;
                                }
                                if(collection){
                                    if(self.env.pos.config.collection_sound){
                                        if(self.env.pos.config.collection_tune){
                                            bell = false;
                                            Gui.playSound(self.env.pos.config.collection_tune)
                                               setTimeout(function(){
                                                        Gui.playSound('sweet_message')
                                                        setTimeout(function(){
                                                            Gui.playSound('sweet_message')
                                                        }, 5000);
                                              }, 5000);
                                        }
                                    }
                                }

                                if(bell){
                                     if(self.env.pos.config.waiting_sound){
                                         if(self.env.pos.config.waiting_tune){
                                             Gui.playSound(self.env.pos.config.waiting_tune)
                                               setTimeout(function(){
                                                        Gui.playSound('notification_ring2')
                                                        setTimeout(function(){
                                                            Gui.playSound('notification_ring2')
                                                        }, 5000);
                                              }, 5000);
                                         }
                                     }
                                }

                                if ((new_sale === false) || (new_pos === false)){
                                     if(self.env.pos.config.new_order_sound){
                                        if(self.env.pos.config.new_order_tune){
                                            Gui.playSound(self.env.pos.config.new_order_tune)
                                        }
                                     }
                                }


//                              SALE
                                for (var i=0;i<sale_order.length; i++){
                                    total_sale.push(sale_order[i].id)
                                }
                                self.sale_order_records = total_sale

//                              POS
                                for (var i=0;i<pos_order.length; i++){
                                    total_pos.push(pos_order[i].order_id)
                                }
                                self.pos_order_records = total_pos

                            }
                             setTimeout(function(){
                                   self.ajax_long_pooling();
                                }, time_out * 1000);

                        },

                        error: function (jqXHR, status, err) {
                            if (status == 'error'){
                                self.render();
                            }
                            setTimeout(function(){
                               self.ajax_long_pooling();
                            }, 10000);
                        },

                        timeout: 40000,
                    })
                }

        }

        get saleorderList() {
            return this.sale_order_new;
        }
        PrintSaleOrder(order){
            var self = this;

            if (order) {
                this.rpc({
                        model: 'pos.order',
                        method: 'load_sale_order_details',
                        args: [order],
                    }).then(function (lines) {
                        if(lines){
                            self.env.print_lines = lines;
                            self.showScreen('ReceiptScreenCustom',{
                                'widget':self,
                                'order': lines
                            });

	            	    }
                    });
            }
        }
        PrintOrder(order){
            var self = this;

            if (order) {
                this.rpc({
                        model: 'pos.order',
                        method: 'load_order_details',
                        args: [order],
                    }).then(function (lines) {
                        if(lines){

                            self.env.print_lines = lines;

                            self.showScreen('ReceiptScreenCustom',{
                                'widget':self,
                                'order': lines
                            });
	            	    }
                    });
            }
        }

        async receiptPrint(order){
            var self = this;
            self.order_print = true
            self.order_print_info = order;
            if (self.env.pos.config.kitchen_order_receipt== true){
            setTimeout(async () => {
            var k = $(self.el).find('.pos-receipt-container').html();
            var element = document.getElementById('container_id');
            printJS({
                printable: 'container_id',
                type: 'html',
                css:'/kitchen_order/static/src/css/pos_receipts.css'
              });}, 1* 1000);
            self.refresh_screen();
            }

        }



        get printObj(){
            return this.order_print_info
        }

        get UhcProduct(){
            return this.uhc_product
        }

        async updateTime(order,info){
            var self = this;

            if (order.type == "pos"){
                var $targetUl = $('#'+info+order.order_id)
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                const { confirmed, payload: inputPin } = await Gui.showPopup('NumberPopupUpdateTime', {
                                isPassword: false,
                                title: 'Preparation In Time In MIN',
                                startingValue: null,

                 });
                 if (confirmed){
//                    ajax.rpc("/upadate/time", {'order': order,'inputPin': inputPin, 'type': 'pos', 'product_info': product_info})
                    var kitchen_screen = false;
                    var ipaddress = self.env.pos.config.ipaddress;
                    var send_sms = self.env.pos.config.send_sms;


                    var startDate = new Date();
                    var endDate = new Date(order.preparation_estimation);
                    var diff = endDate - startDate
                    var minutes = Math.floor(diff/1000);
                    if (minutes >=0){
                    kitchen_screen =true;
                    }


                    var dataToLog = {'order': order,'inputPin': inputPin, 'type': 'pos','product_info': product_info,'send_sms':send_sms,'kitchen_screen':kitchen_screen}

                    $.ajax({
                        type: 'POST',
                        url: ipaddress+'/upadate/time',
                        async: true,
                        processData: true,
                        contentType: "application/json; charset=ytf-8",
                        beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                        data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                    });

                 }
                 }


            if (order.type == "sale"){
                  var $targetUl = $('#'+info+order.order_id[0])
                    var product_info = []
                    $targetUl.each(function() {
                        $(this).find('li').each(function(){
                          if($(this).attr('data-id')){
                            product_info.push($(this).attr('data-id'))
                          }
                        });
                    });
                const { confirmed, payload: inputPin } = await Gui.showPopup('NumberPopupUpdateTime', {
                                isPassword: false,
                                title: 'Preparation In Time In MIN',
                                startingValue: null,

                 });
                 if (confirmed){
//                    ajax.rpc("/upadate/time", {'order': order,'inputPin': inputPin, 'type': 'sale', 'product_info': product_info})
                    var ipaddress = self.env.pos.config.ipaddress;
                     var send_sms = self.env.pos.config.send_sms;
                      var kitchen_screen = false;

                     var startDate = new Date();
                    var endDate = new Date(order.preparation_estimation);
                    var diff = endDate - startDate
                    var minutes = Math.floor(diff/1000);
                    if (minutes >=0){
                    kitchen_screen =true;
                    }



                    var dataToLog = {'order': order,'inputPin': inputPin,'type': 'sale', 'product_info': product_info,'send_sms':send_sms,'kitchen_screen':kitchen_screen}
                    $.ajax({
                        type: 'POST',
                        url: ipaddress+'/upadate/time',
                        async: true,
                        processData: true,
                        contentType: "application/json; charset=ytf-8",
                        beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                        data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                    });
                 }}
//
            }

        async startUhc(order,info){
            var self = this;
            self.order_print = true
            self.order_print_info = order;

            if (order.type == 'pos'){
                var $targetUl = $('#'+info+order.order_id)
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.pos_reference).style.display = "none";
                    var ipaddress = self.env.pos.config.ipaddress;
                    var dataToLog = {'order': order, 'type': 'pos', 'product_info': product_info}
                    $.ajax({
                        type: 'POST',
                        url: ipaddress+'/upadate/start/uhc',
                        async: true,
                        processData: true,
                        contentType: "application/json; charset=ytf-8",
                        beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                        data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                    });

            }
            if (order.type == 'sale'){
                var $targetUl = $('#'+info+order.order_id[0])
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.order_id).style.display = "none";
                var ipaddress = self.env.pos.config.ipaddress;
                var dataToLog = {'order': order, 'type': 'sale','product_info': product_info}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/upadate/start/uhc',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });

            }
        }

        async startOperation(order,info){
            var self = this;
            self.order_print = true
            self.order_print_info = order;

            if (order.type == 'pos'){
                var $targetUl = $('#'+info+order.order_id)
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.pos_reference).style.display = "none";
                    var ipaddress = self.env.pos.config.ipaddress;
                    var dataToLog = {'order': order, 'type': 'pos', 'product_info': product_info}
                    $.ajax({
                        type: 'POST',
                        url: ipaddress+'/upadate/start',
                        async: true,
                        processData: true,
                        contentType: "application/json; charset=ytf-8",
                        beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                        data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                    });

            }
            if (order.type == 'sale'){
                var $targetUl = $('#'+info+order.order_id[0])
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.order_id).style.display = "none";

                var ipaddress = self.env.pos.config.ipaddress;
                var dataToLog = {'order': order, 'type': 'sale','product_info': product_info}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/upadate/start',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });

            }
        }

        async prepareFried(order,info){
            var self = this;
            if (order.type == 'pos'){
                var $targetUl = $('#'+info+order.order_id)
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.pos_reference).style.display = "none";
                var ipaddress = self.env.pos.config.ipaddress;
                var dataToLog = {'order': order, 'type': 'pos', 'product_info': product_info}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/update/preparing/fried',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }
            if (order.type == 'sale'){
                var $targetUl = $('#'+info+order.order_id)
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.pos_reference).style.display = "none";
                var ipaddress = self.env.pos.config.ipaddress;
                var dataToLog = {'order': order, 'type': 'sale','product_info': product_info}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/update/preparing/fried',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }


        }

        async doneFried(order,info){
            var self = this;
            if (order.type == 'pos'){
                var $targetUl = $('#'+info+order.order_id)
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.pos_reference).style.display = "none";
                var ipaddress = self.env.pos.config.ipaddress;
                var dataToLog = {'order': order, 'type': 'pos', 'product_info': product_info}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/update/done/fried',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }
            if (order.type == 'sale'){
                var $targetUl = $('#'+info+order.order_id)
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.pos_reference).style.display = "none";
                var ipaddress = self.env.pos.config.ipaddress;
                var dataToLog = {'order': order, 'type': 'sale','product_info': product_info}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/update/done/fried',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }


        }

        async finishFried(order,info){
            var self = this;
            if (order.type == 'pos'){
                var $targetUl = $('#'+info+order.order_id)
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.pos_reference).style.display = "none";
                var ipaddress = self.env.pos.config.ipaddress;
                var dataToLog = {'order': order, 'type': 'pos', 'product_info': product_info}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/update/finish/fried',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }
            if (order.type == 'sale'){
                var $targetUl = $('#'+info+order.order_id)
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.pos_reference).style.display = "none";
                var ipaddress = self.env.pos.config.ipaddress;
                var dataToLog = {'order': order, 'type': 'sale','product_info': product_info}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/update/finish/fried',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }


        }

        async finishUhc(order,info){
            var self = this;
            if (order.type == 'pos'){
                var $targetUl = $('#'+info+order.order_id)
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.pos_reference).style.display = "none";
                var ipaddress = self.env.pos.config.ipaddress;
                var send_sms = self.env.pos.config.send_sms;
                var dataToLog = {'order': order, 'type': 'pos', 'product_info': product_info, 'send_sms': send_sms}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/update/finish/fried',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }
            if (order.type == 'sale'){
                var $targetUl = $('#'+info+order.order_id[0])
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.order_id).style.display = "none";
                var ipaddress = self.env.pos.config.ipaddress;
                var send_sms = self.env.pos.config.send_sms;
                var dataToLog = {'order': order, 'type': 'sale','product_info': product_info, 'send_sms': send_sms}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/upadate/finish/uhc',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }


        }

        async finishOperation(order,info){
            var self = this;
            if (order.type == 'pos'){
                var $targetUl = $('#'+info+order.order_id)
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.pos_reference).style.display = "none";
                var ipaddress = self.env.pos.config.ipaddress;
                var send_sms = self.env.pos.config.send_sms;
                var dataToLog = {'order': order, 'type': 'pos', 'product_info': product_info, 'send_sms': send_sms}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/upadate/finish',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }
            if (order.type == 'sale'){
                var $targetUl = $('#'+info+order.order_id[0])
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.order_id).style.display = "none";
                var ipaddress = self.env.pos.config.ipaddress;
                var send_sms = self.env.pos.config.send_sms;
                var dataToLog = {'order': order, 'type': 'sale','product_info': product_info, 'send_sms': send_sms}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/upadate/finish',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }
        }

        async deliveryOperation(order,info){
            var self = this;
            self.order_print = true
            self.order_print_info = order;
            if (order.type == 'pos'){
                var $targetUl = $('#'+info+order.order_id)
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.pos_reference).style.display = "none";
//                ajax.rpc("/upadate/delivery", {'order': order, 'type': 'pos', 'product_info': product_info})
                var ipaddress = self.env.pos.config.ipaddress;
                var send_sms = self.env.pos.config.send_sms;
                var dataToLog = {'order': order, 'type': 'pos', 'product_info': product_info, 'send_sms': send_sms}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/upadate/delivery',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }
            if (order.type == 'sale'){
                var $targetUl = $('#'+info+order.order_id[0])
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.order_id).style.display = "none";
//                ajax.rpc("/upadate/delivery", {'order': order, 'type': 'sale','product_info': product_info})
                var ipaddress = self.env.pos.config.ipaddress;
                var send_sms = self.env.pos.config.send_sms;
                var dataToLog = {'order': order, 'type': 'sale','product_info': product_info, 'send_sms': send_sms}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/upadate/delivery',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });
            }
        }

        async doneOperation(order,info){
            var self = this;

            if (order.type == 'pos'){
                var $targetUl = $('#'+info+order.order_id)
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.pos_reference).style.display = "none";
//                ajax.rpc("/upadate/done", {'order': order, 'type': 'pos', 'product_info': product_info})
                var ipaddress = self.env.pos.config.ipaddress;
                var dataToLog = {'order': order, 'type': 'pos', 'product_info': product_info}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/upadate/done',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });

            }
            if (order.type == 'sale'){
                 var $targetUl = $('#'+info+order.order_id[0])
                var product_info = []
                $targetUl.each(function() {
                    $(this).find('li').each(function(){
                      if($(this).attr('data-id')){
                        product_info.push($(this).attr('data-id'))
                      }
                    });
                });
                var doc = document.getElementById(order.order_id).style.display = "none";
//                ajax.rpc("/upadate/done", {'order': order, 'type': 'sale','product_info': product_info})
                var ipaddress = self.env.pos.config.ipaddress;
                var dataToLog = {'order': order, 'type': 'sale','product_info': product_info}
                $.ajax({
                    type: 'POST',
                    url: ipaddress+'/upadate/done',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                });

            }


        }

        async RecallPreviousOrder(){
                var dataToLog = {}
                var self = this;
                $.ajax({
                    type: 'POST',
                    url: window.location.origin+'/recall/order/kitchen',
                    async: true,
                    processData: true,
                    contentType: "application/json; charset=ytf-8",
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({'params': dataToLog, jsonrpc: '2.0'}),
                    success: function(data) {
                            if (data.result) {
                                if (data.result.status=='fail'){
                                self.showPopup('ErrorPopup', {
                                        title: self.env._t('Error'),
                                        body: self.env._t("You can not recall more than 10 Orders"),
                                    });

                                }
                                else if(data.result.status=='no_order'){
                                    const { confirmed: confirmedPopup } = self.showPopup('ConfirmPopup', {
                                    title: 'Order Recalled',
                                    body: 'No Previous Order To add',
                                });
                                }
                                else{
                                 const { confirmed: confirmedPopup } = self.showPopup('ConfirmPopup', {
                                    title: 'Order Recalled',
                                    body: 'Last order added',
                                });
                                }
                            }
                            },

                });

        }

        all_category(){
            $('.all-order-list-contents').css("display", "-webkit-box");
            $('.pos-order-list').css("display", "none");
            $('.sale-order-list').css("display", "none");
            $('.uber-order-list').css("display", "none");
            $('.deliveroo-order-list').css("display", "none");
            this.refresh_screen();
        }
        pos_category(){
            $('.all-order-list-contents').css("display", "none");
            $('.pos-order-list').css("display", "block");
            $('.sale-order-list').css("display", "none");
            $('.uber-order-list').css("display", "none");
            $('.deliveroo-order-list').css("display", "none");
        }
        web_store_category(){
            $('.all-order-list-contents').css("display", "none");
            $('.pos-order-list').css("display", "none");
            $('.sale-order-list').css("display", "block");
            $('.uber-order-list').css("display", "none");
            $('.deliveroo-order-list').css("display", "none");
        }
        uber_category(){
            $('.all-order-list-contents').css("display", "none");
            $('.pos-order-list').css("display", "none");
            $('.sale-order-list').css("display", "none");
            $('.uber-order-list').css("display", "block");
            $('.deliveroo-order-list').css("display", "none");
        }
        deliveroo_category(){
            $('.all-order-list-contents').css("display", "none");
            $('.pos-order-list').css("display", "none");
            $('.sale-order-list').css("display", "none");
            $('.uber-order-list').css("display", "none");
            $('.deliveroo-order-list').css("display", "block");
        }
       async _printReceipt(order) {
            if (this.env.pos.proxy.printer) {
                var receipt = QWeb.render('OrderReceiptKitchenScreen',{'printObj': order, 'widget': this});
                const printResult = await this.env.pos.proxy.printer.print_receipt(receipt);
                if (printResult.successful) {
                    return true;
                } else {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: printResult.message.title,
                        body: 'Do you want to print using the web printer?',
                    });
                    if (confirmed) {
                        // We want to call the _printWeb when the popup is fully gone
                        // from the screen which happens after the next animation frame.
                        return await this.receiptPrintWeb(receipt);
                    }
                    return await false;
                }
            } else {
                return await this.receiptPrintWeb();
            }
        }

       async receiptPrintWeb(receipt){
            var self = this;
            if (self.env.pos.config.kitchen_order_receipt== true){
                $(self.el).find('.pos-receipt-container').empty();
                $(self.el).find('.pos-receipt-container').html(receipt)
                setTimeout(async () => {
                var k = $(self.el).find('.pos-receipt-container').html();
                printJS({
                    printable: 'container_id',
                    type: 'html',
                    css:'/kitchen_order/static/src/css/pos_receipts.css'
                  });}, 1* 1000);
                self.refresh_screen();
            }

       }

        async _printWeb() {
        var self = this;
            try {
                var k = $(this.el).find('.pos-receipt-container').html();
                var element = document.getElementById('container_id');
                    printJS({
                        printable: 'container_id',
                        type: 'html',
                        style: '.blueText {color:blue;}'
                      })

                return true;
            } catch (err) {
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Printing is not supported on some browsers'),
                    body: this.env._t(
                        'Printing is not supported on some browsers due to no default printing protocol ' +
                            'is available. It is possible to print your tickets by making use of an IoT Box.'
                    ),
                });
                return false;
            }
        }


    }




    kitchenScreenWidget.template = 'kitchenScreenWidget';

    Registries.Component.add(kitchenScreenWidget);

    return kitchenScreenWidget;

});
