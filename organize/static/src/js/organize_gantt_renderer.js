odoo.define('organize.OrganizeGanttRenderer', function (require) {
   'use strict';

   const EmployeeGanttRenderer = require('employee_gantt.GanttRenderer');
   const OrganizeGanttRow = require('organize.OrganizeGanttRow');

   const OrganizeGanttRenderer = EmployeeGanttRenderer.extend({
       config: Object.assign({}, EmployeeGanttRenderer.prototype.config, {
           GanttRow: OrganizeGanttRow
       }),

       sampleDataTargets: [
           '.o_gantt_row:not([data-group-id=empty])',
       ],
       async _renderView() {
           await this._super(...arguments);
           this.el.classList.add('o_organize_gantt');
       },

       _render: function () {
           var self = this;
           return this._super.apply(this, arguments).then(function () {
               self.$el.addClass('o_organize_gantt');
           });
       },

       _renderRows: function (rows, groupedBy) {
           const rowWidgets = this._super(rows, groupedBy);

           rowWidgets.forEach(rowWidget => {
               this._generatePillLabels(rowWidget.pills, rowWidget.state.scale);
           });

           return rowWidgets;
       },
       _convertToUserTime: function (date) {
            return date.clone().local();
         },

       _generatePillLabels: function (pills, scale) {

           const dateFormat = moment.localeData().longDateFormat('l');
           const yearlessDateFormat = dateFormat.replace(/Y/gi, '').replace(/(\W)\1+/g, '$1').replace(/^\W|\W$/, '');

           pills.filter(pill => !pill.consolidated).forEach(pill => {

               const localStartDateTime = (pill.start_datetime || pill.startDate).clone().local();
               const localEndDateTime = (pill.end_datetime || pill.stopDate).clone().local();

               const spanAccrossDays = localStartDateTime.clone().startOf('day')
                   .diff(localEndDateTime.clone().startOf('day'), 'days') != 0;

               const spanAccrossWeeks = localStartDateTime.clone().startOf('week')
                   .diff(localEndDateTime.clone().startOf('week'), 'weeks') != 0;

               const spanAccrossMonths = localStartDateTime.clone().startOf('month')
                   .diff(localEndDateTime.clone().startOf('month'), 'months') != 0;

               const labelElements = [];

               if (scale === 'year' && !spanAccrossDays) {
                   labelElements.push(localStartDateTime.format(yearlessDateFormat));
               } else if (
                   (scale === 'day' && spanAccrossDays) ||
                   (scale === 'week' && spanAccrossWeeks) ||
                   (scale === 'month' && spanAccrossMonths) ||
                   (scale === 'year' && spanAccrossDays)
               ) {
                   labelElements.push(localStartDateTime.format(yearlessDateFormat));
                   labelElements.push(localEndDateTime.format(yearlessDateFormat));
               }

               if (!spanAccrossDays && ['week', 'month'].includes(scale)) {
                   labelElements.push(
                       localStartDateTime.format('LT'),
                       localEndDateTime.format('LT')
                   );
               }

               if (scale !== 'month' || spanAccrossDays) {
                   labelElements.push(pill.display_name);
               }
               if (pill) {
                   if (pill.start_datetime) {
                    pill.start_datetimes = this._convertToUserTime(pill.start_datetime);
                   }
                   if (pill.end_datetime) {
                    pill.end_datetimes = this._convertToUserTime(pill.end_datetime);
                   }
               }


               pill.label = labelElements.filter(el => !!el).join(' - ');

           });

       },
   });

   return OrganizeGanttRenderer;
});

