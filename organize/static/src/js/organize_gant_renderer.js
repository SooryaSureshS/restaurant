odoo.define('organize.GantRenderer', function (require) {
    'use strict';

    const GantRenderer = require('backend_gant.GanttRenderer');
    const OrganizeGantRow = require('employee_gantt.GanttRow');

//    const EmployeeGanttRenderer = GanttRenderer.extend({
//        config: Object.assign({}, GanttRenderer.prototype.config, {
//            GanttRow: EmployeeGanttRow
//        }),
//    });
    const EmployeeGanttRenderer = GanttRenderer.extend({
        config: Object.assign({}, GanttRenderer.prototype.config, {
            GanttRow: EmployeeGanttRow
        }),
    });

    return EmployeeGanttRenderer;
});
