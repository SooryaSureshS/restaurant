odoo.define('employee_gantt.GanttView', function (require) {
    'use strict';

    const viewRegistry = require('web.view_registry');
    const GanttView = require('backend_gant.GanttView');
    const EmployeeGanttRenderer = require('employee_gantt.GanttRenderer');

    const EmployeeGanttView = GanttView.extend({
        config: Object.assign({}, GanttView.prototype.config, {
            Renderer: EmployeeGanttRenderer,
        }),
    });

    viewRegistry.add('employee_gantt', EmployeeGanttView);
    return EmployeeGanttView;
});
