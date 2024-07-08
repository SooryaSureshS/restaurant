odoo.define('organize.OrganizeGanttRow', function (require) {
   'use strict';
   const EmployeeGanttRow = require('employee_gantt.GanttRow');

   const OrganizeGanttRow = EmployeeGanttRow.extend({
       template: 'OrganizeGanttView.Row'
   });

   return OrganizeGanttRow;
});


