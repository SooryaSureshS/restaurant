odoo.define('employee_gantt.GanttRenderer', function (require) {
    'use strict';

    const GanttRenderer = require('backend_gant.GanttRenderer');
    const EmployeeGanttRow = require('employee_gantt.GanttRow');

    const EmployeeGanttRenderer = GanttRenderer.extend({
        config: Object.assign({}, GanttRenderer.prototype.config, {
            GanttRow: EmployeeGanttRow
        }),
    });

    return EmployeeGanttRenderer;
});
