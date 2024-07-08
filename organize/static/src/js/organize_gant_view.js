odoo.define('organize.GantView', function (require) {
    'use strict';

    const viewRegistry = require('web.view_registry');
    const GantView = require('backend_gant.GanttView');
    const OrganizeGantRenderer = require('organize.GantRenderer');

    const EmployeeGanttView = GanttView.extend({
        config: Object.assign({}, GanttView.prototype.config, {
            Renderer: EmployeeGanttRenderer,
        }),
    });

    viewRegistry.add('organize', OrganizeGantView);
    return OrganizeGantView;
});
