odoo.define('organize.OrganizeGanttModel', function (require) {
   "use strict";

   var GanttModel = require('backend_gant.GanttModel');
   var _t = require('web.core')._t;

   var OrganizeGanttModel = GanttModel.extend({
       __reload: function (handle, params) {
           if ('context' in params && params.context.organize_groupby_role && !params.groupBy.length) {
               params.groupBy.unshift('employee_id');
               params.groupBy.unshift('role_id');
           }

           return this._super(handle, params);
       },
       _generateRows: function (params) {
           var rows = this._super(params);
           if (params.groupedBy && params.groupedBy.length && rows.length > 1 && rows[0].resId) {
               this._reorderEmptyRow(rows)
           }
           this._renameOpenShifts(rows);
           if (!this.context.hide_open_shift && !params.parentPath && params.groupedBy && params.groupedBy.includes('employee_id')) {
               this._prependEmptyRow(rows, params.groupedBy);
           }
           if (!this.context.hide_open_shift && !params.parentPath && params.groupedBy && this._allowedEmptyGroups(params.groupedBy)) {
               this._startGenerateEmptyRows(rows, params.groupedBy);
           }
           return rows;
       },
       _generateEmptyRows: function (row, groupedBy, level = 0, parentValues = {}, prependUndefined = false) {
           var levelMax = groupedBy.length - 1;
           var emptyRowId = row.id + '-empty';
           var emptyGroupId = row.id + '-empty';
           var undefinedGroupBy = groupedBy[level + 1];
           parentValues[row.groupedByField] = row.resId ? [row.resId, row.name] : false;

           if (prependUndefined) {
               if (!row.rows || !row.rows.length || row.rows[0].resId) {
                   row.rows.unshift(this._createEmptyRow(emptyRowId, emptyGroupId, groupedBy.slice(level + 1), row.path, level < levelMax - 1));
                   row.childrenRowIds.unshift(emptyRowId);

                   if (level === levelMax - 1) {
                       this._addGanttEmptyGroup(emptyGroupId, parentValues, undefinedGroupBy);
                   }
               }
               if (level < levelMax - 1) {
                   this._generateEmptyRows(row.rows[0], groupedBy, level + 1, parentValues, prependUndefined);
               }
           } else if (level < levelMax - 1 && row.rows && row.rows.length) {
               row.rows.forEach((childRow) => this._generateEmptyRows(childRow, groupedBy, level + 1, parentValues));
           } else if (level === levelMax - 1 && row.rows && row.rows.length && row.rows[0].resId) {
               row.rows.unshift(this._createEmptyRow(emptyRowId, emptyGroupId, groupedBy.slice(level + 1), row.path));
               row.childrenRowIds.unshift(emptyRowId);
               this._addGanttEmptyGroup(emptyGroupId, parentValues, undefinedGroupBy);
           }
           if (row.rows) {
               for (const subRow of row.rows) {
                   row.childrenRowIds = row.childrenRowIds.concat(subRow.childrenRowIds || []);
               }
               row.childrenRowIds = [...new Set(row.childrenRowIds)];
           }
       },
       _createEmptyRow: function (rowId, groupId, groupedBy, parentPath = null, isGroup = false) {
           const groupedByField = groupedBy[0];
           const row = {
               name: ['employee_id', 'department_id'].includes(groupedByField) ? _t('Open Shifts') : this._getFieldFormattedValue(false, this.ganttData.fields[groupedByField]),
               groupId: groupId,
               groupedBy,
               groupedByField,
               id: rowId,
               resId: false,
               isGroup: isGroup,
               isOpen: true,
               path: parentPath ? parentPath + '/false' : 'false',
               records: [],
               unavailabilities: [],
               rows: isGroup ? [] : null,
               childrenRowIds: isGroup ? [] : null
           };
           this.allRows[rowId] = row;
           return row;
       },
       _addGanttEmptyGroup: function (groupId, parentValues, emptyKey) {
           var group = {id: groupId};
           Object.keys(parentValues).forEach((key) => group[key] = parentValues[key]);
           group[emptyKey] = false;
           this.ganttData.groups.push(group);
       },

       _renameOpenShifts: function (rows) {
           rows.filter(row => ['employee_id', 'department_id'].includes(row.groupedByField) && !row.resId)
               .forEach(row => row.name = _t('Open Shifts'));
       },
       _reorderEmptyRow: function (rows) {
           let emptyIndex = null;
           for (let i = 0; i < rows.length; ++i) {
               if (!rows[i].resId) {
                   emptyIndex = i;
                   break;
               }
           }
           if (emptyIndex) {
               const emptyRow = rows.splice(emptyIndex, 1)[0];
               rows.unshift(emptyRow);
           }
       },
       _prependEmptyRow: function (rows, groupedBy) {
           const prependEmptyRow = (rows.length === 1 && !rows[0].id) || rows[0].resId;
           if (prependEmptyRow) {
               if (!rows[0].id) {
                   rows.splice(0, 1);
               }
               rows.unshift(this._createEmptyRow('empty', 'empty', groupedBy, null, groupedBy.length > 1));
               if (groupedBy.length === 1) {
                   this._addGanttEmptyGroup('empty', {[groupedBy[0]]: false}, groupedBy[0]);
               }
           }
           if (groupedBy.length > 1) {
               this._generateEmptyRows(rows[0], groupedBy, 0, {}, true);
           }
       },
       _startGenerateEmptyRows: function (rows, groupedBy) {
           if (groupedBy.length === 1 && rows.length > 0 && rows[0].resId) {
               rows.unshift(this._createEmptyRow('empty', 'empty', groupedBy));
               this._addGanttEmptyGroup('empty', {}, groupedBy[0]);
           } else if (groupedBy.length > 1) {
               rows.forEach((row) => this._generateEmptyRows(row, groupedBy));
           }
       },

       _allowedEmptyGroups: function (groupedBy) {
           return -1 < this._getEmptyGroupsToDisplay().indexOf(groupedBy.join(','));
       },

       _getEmptyGroupsToDisplay: function () {
           return [
               'role_id',
               'role_id,employee_id',
               'role_id,department_id',
               'department_id',
               'department_id,role_id',
               'project_id',
               'project_id,department_id',
               'project_id,employee_id',
               'project_id,role_id',
               'project_id,task_id,employee_id',
               'project_id,task_id,role_id',
               'task_id',
               'task_id,department_id',
               'task_id,employee_id',
               'task_id,role_id',
           ];
       },
   });

   return OrganizeGanttModel;
});


