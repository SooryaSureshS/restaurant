# -*- coding: utf-8 -*-

from odoo import _, api, models
from lxml import etree
from lxml.builder import E
from odoo.exceptions import UserError

GANTT_VALID_AT = set(['date_start','date_stop','default_scale','class','js_class','form_view_id','progress','consolidation',
   'consolidation_max','consolidation_exclude','string','create','on_create','cell_create','edit','delete','plan','default_group_by',
   'dynamic_range','display_unavailability','total_row','collapse_first_level','offset','scales','thumbnails','precision','color',
   'decoration-secondary','decoration-success','decoration-info','decoration-warning','decoration-danger','sample'])

class IrUiView(models.Model):
   _inherit = 'ir.ui.view'

   def _postprocess_access_rights(self, model, node):
       super(IrUiView, self)._postprocess_access_rights(model, node)

       Model = self.env[model].sudo(False)
       is_base_model = self.env.context.get('base_model_name', model) == model

       if node.tag in ('gantt'):
           for action, operation in (('create', 'create'), ('delete', 'unlink'), ('edit', 'write')):
               if (not node.get(action) and
                       not Model.check_access_rights(operation, raise_exception=False) or
                       not self._context.get(action, True) and is_base_model):
                   node.set(action, 'false')


   def _validate_gant(self, node, name_manager, node_info):
       templates_count = 0
       for line in node.iterchildren(tag=etree.Element):
           if line.tag == 'templates':
               if not templates_count:
                   templates_count += 1
               else:
                   message = _('This view can contain only one templates')
                   self.handle_view_error(message)
           elif line.tag != 'field':
               message = _('Line can only be field or template, got %s')
               self.handle_view_error(message % line.tag)

       default_scale = node.get('default_scale')
       if default_scale:
           if default_scale not in ('day', 'week', 'month', 'year'):
               self.handle_view_error(_("Invalid default_scale '%s' in view", default_scale))
       attrs = set(node.attrib)
       if not 'date_start' in attrs:
           message = _("Must have a 'date_start' attribute")
           self.handle_view_error(message)

       if not 'date_stop' in attrs:
           message = _("Must have a 'date_stop' attribute")
           self.handle_view_error(message)

       remaining = attrs - GANTT_VALID_AT
       if remaining:
           message = _("Invalid attribute%s (%s) in view. Attributes must be in (%s)")
           self.handle_view_error(message % ('s' if len(remaining) > 1 else '', ','.join(remaining), ','.join(GANTT_VALID_AT)))


class Base(models.AbstractModel):
    _inherit = 'base'

    _start_name = 'date_start'
    _stop_name = 'date_stop'

    @api.model
    def _get_default_gantt_view(self):
        view = E.gantt(string=self._description)
        gantt_field_names = {
            '_start_name': ['date_start', 'start_date', 'x_date_start', 'x_start_date'],
            '_stop_name': ['date_stop', 'stop_date', 'date_end', 'end_date', 'x_date_stop', 'x_stop_date', 'x_date_end', 'x_end_date'],
        }
        for name in gantt_field_names.keys():
            if getattr(self, name) not in self._fields:
                for dt in gantt_field_names[name]:
                    if dt in self._fields:
                        setattr(self, name, dt)
                        break
                else:
                    raise UserError(_("Insufficient fields"))
        view.set('date_start', self._start_name)
        view.set('date_stop', self._stop_name)
        return view

    @api.model
    def gantt_availability_check(self, start_date, end_date, scale, group_bys=None, rows=None):
        return rows