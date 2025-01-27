odoo.define('organize.OrganizeGanttController', function (require) {
'use strict';

var GanttController = require('backend_gant.GanttController');
var core = require('web.core');
var _t = core._t;
var Dialog = require('web.Dialog');
var dialogs = require('web.view_dialogs');

var QWeb = core.qweb;
var OrganizeGanttController = GanttController.extend({
   events: _.extend({}, GanttController.prototype.events, {
       'click .o_gantt_button_copy_previous_week': '_onCopyWeekClicked',
       'click .o_gantt_button_send_all': '_onSendAllClicked',
       'click .o_gantt_button_delete': '_ActionDelete',
       'click .o_gantt_button_print': '_ActionPrint',
       'click .o_gantt_button_duplicate': '_ActionDuplicate',
   }),
   _convertToUserTime: function (date) {
            return date.clone().local();
         },


   renderButtons: function ($node) {
       var state = this.model.get();
       this.$buttons = $(QWeb.render('OrganizeGanttView.buttons', {
           groupedBy: state.groupedBy,
           widget: this,
           SCALES: this.SCALES,
           activateScale: state.scale,
           allowedScales: this.allowedScales,
           activeActions: this.activeActions,
       }));
       if ($node) {
           this.$buttons.appendTo($node);
       }
   },

   _openDialog: function (resID, context) {
       var self = this;
       var record = resID ? _.findWhere(this.model.get().records, {id: resID,}) : {};
       var title = resID ? record.display_name : _t("Open");

       var dialog = new dialogs.FormViewDialog(this, {
           title: _.str.sprintf(title),
           res_model: this.modelName,
           view_id: this.dialogViews[0][0],
           res_id: resID,
           readonly: !this.is_action_enabled('edit'),
           deletable: this.is_action_enabled('edit') && resID,
           context: _.extend({}, this.context, context),
           on_saved: this.reload.bind(this, {}),
           on_remove: this._onDialogRemove.bind(this, resID),
       });
       dialog.on('closed', this, function(ev){
           self.reload();
       });
       dialog.on('execute_action', this, function(e) {
           const action_name = e.data.action_data.name || e.data.action_data.special;
           const event_data = _.clone(e.data);
           let message;

           if (action_name === "unlink") {
               e.stopPropagation();
               message = _('Are you sure that you want to do delete this shift?');

               Dialog.confirm(self, message, {
                   confirm_callback: function(evt) {
                       self.trigger_up('execute_action', event_data);
                       _.delay(function() { self.dialog.destroy() }, 100);
                   },
                   cancel_callback: function(evt) {
                       self.dialog.$footer.find('button').removeAttr('disabled');
                   }
               });
           }
       });

       self.dialog = dialog.open();
       return self.dialog;
   },

   _ActionDelete: function (ev) {

        var state = this.model.get();
        var self = this;
        var start_date = self.model.convertToServerTime(state.startDate);
        var end_date = start_date
            var context={
            'default_start_datetime':start_date,
             'default_action': 'delete',
            }
            return self.do_action('organize.organize_organize_action', {
            additional_context : context,
           on_close: function () {
               self.reload();
           }

       });
   },
   _ActionPrint: function (ev) {
        var state = this.model.get();
        var self = this;
        var start_date = self.model.convertToServerTime(state.startDate);
        var end_date = start_date;
        var context={
            'default_from_date': start_date,
            }
        return self.do_action('organize.action_organize_report', {
             additional_context : context,


       });
   },


   _ActionDuplicate: function (ev) {

      var state = this.model.get();
      var self = this;
      var start_date = self.model.convertToServerTime(state.startDate);
      var end_date = start_date;
      var context={
            'default_start_datetime':start_date,
            'default_action_duplicate': 'duplicate',
            }
      return self.do_action('organize.organize_organize_action_duplicate', {
            additional_context : context,
           on_close: function () {
               self.reload();
           }

       });
   },
   _onCopyWeekClicked: function (ev) {
       ev.preventDefault();
       var state = this.model.get();
       var self = this;
       self._rpc({
           model: self.modelName,
           method: 'action_copy_previous_week',
           args: [
               self.model.convertToServerTime(state.startDate),
               this.model._getDomain(),
           ],
           context: _.extend({}, self.context || {}),
       }).then(function(result){
            var context={
            'default_start_datetime':result['start_date'],
            'default_end_datetime':result['end_date'],
            }
            return self.do_action('organize.organize_week_copy_action', {
            additional_context : context,
            on_close: function () {
               self.reload();
           }

       });
       });
   },

//   _onPublishedClicked: function (ev) {
//       ev.preventDefault();
//       var state = this.model.get();
//       var self = this;
//        return this.do_action('organize.organize_action_published', {
//           on_close: function () {
//               self.reload();
//           }
//       });
//   },

   _onSendAllClicked: function (ev) {
       ev.preventDefault();
       var self = this;
       var state = this.model.get();
       var additional_context = _.extend({}, this.context, {
          'default_start_datetime': this.model.convertToServerTime(state.startDate),
          'default_end_datetime': this.model.convertToServerTime(state.stopDate),
          'default_slot_ids': _.pluck(this.model.get().records, 'id'),
          'scale': state.scale,
          'active_domain': this.model.domain,
          'active_ids': this.model.get().records,
          'default_employee_ids': _.filter(_.pluck(self.initialState.rows, 'resId'), Boolean),
       });
       return this.do_action('organize.organize_send_action', {
           additional_context: additional_context,
           on_close: function () {
               self.reload();
           }
       });
   },
   _onScaleClicked: function (ev) {
       this._super.apply(this, arguments);
       var $button = $(ev.currentTarget);
       var scale = $button.data('value');
       if (scale !== 'week') {
           this.$('.o_gantt_button_copy_previous_week').hide();
           this.$('.o_gantt_button_action').hide();
       } else {
           this.$('.o_gantt_button_copy_previous_week').show();
           this.$('.o_gantt_button_action').show();
       }
   },
});

return OrganizeGanttController;

});

