odoo.define('website_delivery_type.feedback', function (require) {
    "use strict";
    var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var session = require('web.session');
var utils = require('web.utils');
var timeout;
var ajax = require('web.ajax');
var ServicesMixin = require('web.ServicesMixin');


    publicWidget.registry.website_feedback = publicWidget.Widget.extend({
    selector: '#feedback_image',
    events: {
        'click .option_good': '_option_good',
        'click .option_bad': '_option_bad',
        'click #feedback_confirm_button': '_feedback_confirm_button',
    },

    init: function () {
        var self = this;
        this._super.apply(this, arguments);
    },
    _option_good: function (ev){
        var self = this;
        var $target = $(ev.currentTarget);
          var order_id = document.getElementById("feedback_order_id").value;
          $("#tell_as_more").show();
          $("#feedback_face").val("good");
          var feedback_message = document.getElementById("feedback_text_update").value;
          var feedback_face = document.getElementById("feedback_face").value;
          if (order_id){
          ajax.jsonRpc('/order/feedback/update', 'call', {"ready": 1,"order_id":order_id,'feedback_message':feedback_message,'feedback_face':feedback_face}).then(function(res) {
          if (res){

          }
            });
          }

    },

    _feedback_confirm_button: function (ev){
    var self = this;
        var $target = $(ev.currentTarget);
          var order_id = document.getElementById("feedback_order_id").value;
          var feedback_message = document.getElementById("feedback_text_update").value;
          var feedback_face = document.getElementById("feedback_face").value;
          if (order_id && feedback_message){
          ajax.jsonRpc('/order/feedback/update', 'call', {"ready": 1,"order_id":order_id,'feedback_message':feedback_message,'feedback_face':feedback_face}).then(function(res) {
          if (res){
           $("#tell_as_more").hide();
          alert("THANK YOU!!!! It goes a long way in helping us to improve the ordering experience for you!!!!")


          }

          });
//          $("#tell_as_more").show();

          }
    },



    _option_bad: function (ev){
        var self = this;
        var $target = $(ev.currentTarget);
          var order_id = document.getElementById("feedback_order_id").value;
          $("#tell_as_more").show();
          $("#feedback_face").val("sad");
          var feedback_message = document.getElementById("feedback_text_update").value;
          var feedback_face = document.getElementById("feedback_face").value;
          if (order_id){
          ajax.jsonRpc('/order/feedback/update', 'call', {"ready": 1,"order_id":order_id,'feedback_message':feedback_message,'feedback_face':feedback_face}).then(function(res) {
          if (res){
          }
          });

        }
        },
   });
   });