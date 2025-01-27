odoo.define('organize.calendar_frontend', function (require) {
"use strict";

const publicWidget = require('web.public.widget');

publicWidget.registry.OrganizeView = publicWidget.Widget.extend({
   selector: '#calendar_employee',
   jsLibs: [
       '/web/static/lib/fullcalendar/core/main.js',
       '/web/static/lib/fullcalendar/core/locales-all.js',
       '/web/static/lib/fullcalendar/interaction/main.js',
       '/web/static/lib/fullcalendar/moment/main.js',
       '/web/static/lib/fullcalendar/daygrid/main.js',
       '/web/static/lib/fullcalendar/timegrid/main.js',
       '/web/static/lib/fullcalendar/list/main.js'
   ],
   cssLibs: [
       '/web/static/lib/fullcalendar/core/main.css',
       '/web/static/lib/fullcalendar/daygrid/main.css',
       '/web/static/lib/fullcalendar/timegrid/main.css',
       '/web/static/lib/fullcalendar/list/main.css'
   ],

   init: function (parent, options) {
       this._super.apply(this, arguments);
   },
   start: function () {
      if ($('.message_slug').attr('value')) {
          $("#OrganizeToast").toast('show');
      }
      this._super.apply(this, arguments);
      this.calendarElement = this.$(".o_calendar_widget")[0];
      const employeeSlotsFcData = JSON.parse($('.employee_slots_fullcalendar_data').attr('value'));
      const openSlotsIds = $('.open_slots_ids').attr('value');
      const locale = $('.locale').attr('value');
      const defaultStart = moment($('.default_start').attr('value')).toDate();
      const defaultView = $('.default_view').attr('value');
      const minTime = $('.mintime').attr('value');
      const maxTime = $('.maxtime').attr('value');
      let calendarHeaders = {
          left: 'dayGridMonth,timeGridWeek,listMonth',
          center: 'title',
          right: 'today,prev,next'
      };
      if (employeeSlotsFcData.length === 0) {
          calendarHeaders = {
               left: false,
               center: 'title',
               right: false,
           };
      }
      let titleFormat = 'MMMM YYYY';
      if (defaultView && (employeeSlotsFcData || openSlotsIds)) {
          this.calendar = new FullCalendar.Calendar($("#calendar_employee")[0], {
               plugins: [
                   'moment',
                   'dayGrid',
                   'timeGrid',
                   'list',
                   'interraction'
               ],
               locale: locale,
               defaultView: defaultView,
               navLinks: true,
               eventLimit: true,
               titleFormat: titleFormat,
               defaultDate: defaultStart,
               timeFormat: 'LT',
               displayEventEnd: true,
               height: 'auto',
               eventTextColor: 'white',
               eventOverlap: true,
               eventTimeFormat: {
                   hour: 'numeric',
                   minute: '2-digit',
                   meridiem: 'long',
                   omitZeroMinute: true,
               },
               minTime: minTime,
               maxTime: maxTime,
               header: calendarHeaders,
               events: employeeSlotsFcData,
               eventClick: this.eventFunction,
               });
               this.calendar.setOption('locale', locale);
               this.calendar.render();
          }
   },
   eventFunction: function (calEvent) {
       const organizeToken = $('.organize_token').attr('value');
       const employeeToken = $('.employee_token').attr('value');
       $(".modal-title").text(calEvent.event.title);
       $(".modal-header").css("background-color", calEvent.event.backgroundColor);
       $("#start").text(moment(calEvent.event.start).format("YYYY-MM-DD hh:mm A"));
       $("#stop").text(moment(calEvent.event.end).format("YYYY-MM-DD hh:mm A"));
       $("#alloc_hours").text(calEvent.event.extendedProps.alloc_hours);
       $("#role").text(calEvent.event.extendedProps.role);
       if (calEvent.event.extendedProps.alloc_perc !== 100) {
           $("#alloc_perc_value").text(calEvent.event.extendedProps.alloc_perc);
           $("#alloc_perc").css("display", "");
       } else {
           $("#alloc_perc").css("display", "none");
       }

       if (calEvent.event.extendedProps.role) {
           $("#role").prev().css("display", "");
           $("#role").text(calEvent.event.extendedProps.role);
           $("#role").css("display", "");
       } else {
           $("#role").prev().css("display", "none");
           $("#role").css("display", "none");
       }
       if (calEvent.event.extendedProps.note) {
           $("#note").prev().css("display", "");
           $("#note").text(calEvent.event.extendedProps.note);
           $("#note").css("display", "");
       } else {
           $("#note").prev().css("display", "none");
           $("#note").css("display", "none");
       }
       $("#allow_self_unassign").text(calEvent.event.extendedProps.allow_self_unassign);
       if (calEvent.event.extendedProps.allow_self_unassign) {
           document.getElementById("dismiss_shift").style.display = "block";
       } else {
           document.getElementById("dismiss_shift").style.display = "none";
       }
       $("#modal_action_dismiss_shift").attr("action", "/organize/" + organizeToken + "/" + employeeToken + "/unassign/" + calEvent.event.extendedProps.slot_id);
       $("#fc-slot-onclick-modal").modal("show");
   },
});

return publicWidget.registry.OrganizeView;
});

