odoo.define('organize.OrganizeGanttView', function (require) {
   'use strict';

   const EmployeeGanttView = require('employee_gantt.GanttView');
   const OrganizeGanttController = require('organize.OrganizeGanttController');
   const OrganizeGanttModel = require('organize.OrganizeGanttModel');
   const OrganizeGanttRenderer = require('organize.OrganizeGanttRenderer');

   const view_registry = require('web.view_registry');

   const OrganizeGanttView = EmployeeGanttView.extend({
       config: Object.assign({}, EmployeeGanttView.prototype.config, {
           Renderer: OrganizeGanttRenderer,
           Controller: OrganizeGanttController,
           Model: OrganizeGanttModel,
       }),
   });

   view_registry.add('organize_gantt', OrganizeGanttView);
   return OrganizeGanttView;

});


