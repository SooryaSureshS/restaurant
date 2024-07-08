odoo.define('organize.Calendar', function (require) {
"use strict";

   var core = require('web.core');
   var CalendarPopover = require('web.CalendarPopover');
   var CalendarRenderer = require('web.CalendarRenderer');
   var CalendarModel = require('web.CalendarModel');
   var CalendarView = require('web.CalendarView');
   var view_registry = require('web.view_registry');
   var QWeb = core.qweb;

   var OrganizeCalendarPopover = CalendarPopover.extend({
       willStart: function() {
           const self = this;
           const check_group = this.getSession().user_has_group('organize.group_organize_manager').then(function(has_group) {
               self.is_manager = has_group;
           });
           return Promise.all([this._super.apply(this, arguments), check_group]);
       },

       renderElement: function () {
           let render = $(QWeb.render(this.template, { widget: this }));
           if(!this.is_manager) {
               render.find('.card-footer').remove();
           }

           this._replaceElement(render);
       },

       _processFields: function () {
           var self = this;

           if (!CalendarPopover.prototype.origDisplayFields) {
               CalendarPopover.prototype.origDisplayFields = _.extend({}, this.displayFields);
           } else {
               this.displayFields = _.extend({}, CalendarPopover.prototype.origDisplayFields);
           }

           _.each(this.displayFields, function(def, field) {
               if (self.event.extendedProps && self.event.extendedProps.record && !self.event.extendedProps.record[field]) {
                   delete self.displayFields[field];
               }
           });

           return this._super.apply(this, arguments);
       }
   });

   var OrganizeCalendarModel = CalendarModel.extend({
       _loadCalendar: function () {
           var filter = this.data.filters['employee_id'].filters || {};
           const filteredCount = filter.reduce((n, value) => n + value.active, 0);
           this.data.context['organize_calendar_view'] = true;
           this.data.context['organize_hide_employee'] = filteredCount === 1;
           return this._super.apply(this, arguments);
       }
   });

   var OrganizeCalendarRenderer = CalendarRenderer.extend({
       config: _.extend({}, CalendarRenderer.prototype.config, {
           CalendarPopover: OrganizeCalendarPopover,
       }),
   });

   var OrganizeCalendarView = CalendarView.extend({
       config: _.extend({}, CalendarView.prototype.config, {
           Renderer: OrganizeCalendarRenderer,
           Model: OrganizeCalendarModel,
       }),
   });

   view_registry.add('organize_calendar', OrganizeCalendarView);
});

