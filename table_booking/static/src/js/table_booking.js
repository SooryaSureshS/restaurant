odoo.define('table_booking.table_booking', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;
var ajax = require('web.ajax');
var qweb = core.qweb;

publicWidget.registry.table_booking = publicWidget.Widget.extend({

    selector: '#booking_table',
    xmlDependencies: ['/table_booking/static/src/xml/booking.xml'],
    events: {
        'click .find_table': '_find_table',
        'click .floor_button': '_floor_button',
        'click .confirm_button': '_confirm_button',
        'change #booking_date': 'pickup',
//        'mouseover #booking_date': 'pickup_date_picker',

    },
//    /**
//     * @constructor
//     */
    init: function () {
        var self = this;
        self.selected_floor= false;
        self.selected_time= false;
        self.booking_date= false;
        self.select_person= false;

        $('#select_person').niceSelect();
        $('.reservation_container').show();

        this._super.apply(this, arguments);

    },

    pickup: function () {

            $('#select_time').empty();
            var pickup_date = '';
            try{
                pickup_date = document.getElementById("booking_date").value;
            }
            catch(err){
                console.log();
            }
            if (pickup_date==''){
            pickup_date = "Today";
                          }
            ajax.jsonRpc('/get/time/booking', 'call', {"ready": 1,"picking_date":pickup_date}).then(function(res) {
            var cooking_time = 0;
            cooking_time = res;
                try{
            var pickup_date = res.picking_date;
            var after_date = res.after_date;
            var output = res.today_date;
            var strtDt  = new Date(pickup_date);
            var endDt  = new Date(output);


            console.log(pickup_date, "==", after_date)
            console.log(strtDt, "< >", endDt)
            if((pickup_date==after_date)|| (strtDt>endDt)){
                console.log("klajsdlkajdkl")
                var from_time_2 =res.from_time_2;
                var now_time = res.time_now;
                var time30 = res.from_time_1;
                var time15 = time30;
                if(time30>from_time_2)
                {
                    end_time = '2359';
                    from_time_2 = '23:59';
                }
                if((pickup_date==output)&&(now_time>time30))
                {
                    if (now_time<from_time_2){
                        time30=now_time;
                    }
                }
                var start_time = time30.replace(":","");
                var end_time = from_time_2.replace(":","");
                var start_hour = start_time.slice(0, -2);
                var start_minutes = start_time.slice(-2);
                var end_hour = end_time.slice(0, -2);
                var end_minutes = end_time.slice(-2);
                var startDate = new Date(0,0,0, start_hour, start_minutes);
                var endDate = new Date(0,0,0, end_hour, end_minutes);
                var millis = endDate - startDate;
                var minutes = millis/1000/60;
                var loop_no=minutes/30;
                console.log("WRETYUIOHGFDHJ")
                if (loop_no>0){

                console.log(now_time, "< >", from_time_2)
                console.log(pickup_date, "< >", output)

                if((now_time<from_time_2)||(pickup_date!=output))
                {
                    console.log("DFGHJKLKJHGFD")
                    for(var i=1;i<=loop_no;i++)
                        {
                             if(pickup_date==output)
                               {
                                    console.log("YTYTYTYTTYYT")
                                    if(time30<=from_time_2)
                                        {
                                        console.log("VVVVVVVVVV")
                                        var tm = moment.utc(time30,'HH:mm').add(30,'minutes').format('HH:mm');
                                        $('#select_time').append('<option value='+tm+'>'+tm+'</option>');
                                        time30 = tm;
                                        }
                                }
                            else
                                {
                                    console.log("WWWWWWWWW")
                                    var tm = moment(time15,'HH:mm').add(30,'minutes').format('HH:mm');
                                    $('#select_time').append('<option value='+tm+'>'+tm+'</option>');
                                    time15 = tm;
                                }
                        }
                    }
                }

                }
                else{
                    $('#select_time').empty();
                }

                }
                catch(err){
                console.log(err)
                }
                });

        },

        _find_table: function(ev){
        var self = this;
        var select_person = $('#select_person option:selected').val();
        var booking_date = $('#booking_date').val();
        var select_time = $('#select_time').val();

        if (booking_date &&	select_time &&select_person){
            ajax.jsonRpc('/get/table/booking', 'call', {"ready": 1,"select_person":select_person,'booking_date':booking_date,'select_time':select_time}).then(function(res) {
                    if(res){
                    $('.reservation_container').hide();
                    self.selected_time= select_time;
                    self.booking_date= booking_date;
                    self.select_person= select_person;
                    $('#booking_table').html(qweb.render("booking_table", {widget: res}));
                    }
                    else{
                        alert("Tables are not available in this time slot.")
                    }
                });
        }
        else{
        alert("Please Select Options!!")
        }


        },

        _floor_button: function(ev){
            var self = this;
            var $target = $(ev.currentTarget);
            var floor_id = $target.attr('data-id');
            var table_id = $target.attr('data-table');
            if (floor_id){
                self.selected_floor= floor_id;
                self.available_table= table_id;
                $('#booking_table').empty();
                $('#booking_table').html(qweb.render("booking_details", {widget: self}));
                var count = 120;
                var interval = setInterval(function(){
                  document.getElementById('count').innerHTML=count;
                  count--;
                  if (count === 0){
                    clearInterval(interval);
                    document.getElementById('count').innerHTML='';
                    alert("You're out of time!");
                    window.location.href = 'booking';
                  }
                }, 1000);

            }

        },

        _confirm_button: function(ev){

        var self = this;
        var first_name = $('#first_name').val();
        var last_name = $('#last_name').val();
        var phone = $('#phone').val();
        var email = $('#email').val();
        var occasion = $(".occasion option:selected").val();
        var request = $('#request').val();

        var phone_regex =   /^\d+$/;
        var phone_valid =  phone_regex.test(phone);
        var email_regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
        var email_valid =  email_regex.test(email);
        var update_reminder = $('#update_reminder').val();
        var email_from = $('#email_from').val();
        var email_open_table = $('#email_open_table').val();
        var floor_id = self.selected_floor;
        var table_id = self.available_table;

        if (phone_valid === false || email_valid === false){
            alert("Email and Phone should be in correct format!!!")
        }
        else{
            if (first_name && last_name && phone && email && email_valid && phone_valid){
                    $('.rowpp .confirm_button').hide()
                     ajax.jsonRpc('/create/user', 'call', {"ready": 1,'first_name':first_name,'last_name':last_name,'phone':phone,'email':email,'floor_id':floor_id,'table_id':table_id,'selected_time':self.selected_time,'booking_date': self.booking_date,'select_person':self.select_person, 'occasion':occasion, 'request':request}).then(function(res) {
                        if(res){
                        alert("You are successfully Booked");
                        window.location.reload();

                        }
                    });
            }
            else{
                alert("Please Fill All the Details!!!")}
            }

        }


});

});