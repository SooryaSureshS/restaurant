
# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
import pytz
from werkzeug.utils import redirect
from odoo.tools.misc import get_lang
from odoo import tools


class ShiftController(http.Controller):

   @http.route(['/organize/<string:organize_token>/<string:employee_token>'], type='http', auth="public", website=True)
   def organize(self, organize_token, employee_token, message=False, **kwargs):
       organize_data = self._organize_get(organize_token, employee_token, message)
       if not organize_data:
           return request.not_found()
       return request.render('organize.period_report_template', organize_data)

   def _organize_get(self, organize_token, employee_token, message=False):
       employee_sudo = request.env['hr.employee'].sudo().search([('employee_token', '=', employee_token)], limit=1)
       if not employee_sudo:
           return

       organize_sudo = request.env['organize.organize'].sudo().search([('access_token', '=', organize_token)], limit=1)
       if not organize_sudo:
           return

       employee_tz = pytz.timezone(employee_sudo.tz or 'UTC')
       employee_fullcalendar_data = []
       open_slots = []

       if organize_sudo.include_unassigned:
           organize_slots = organize_sudo.slot_ids.filtered(lambda s: s.employee_id == employee_sudo or not s.employee_id)
       else:
           organize_slots = organize_sudo.slot_ids.filtered(lambda s: s.employee_id == employee_sudo)

       organize_slots = organize_slots._filter_slots_front_end(employee_sudo)

       slots_start_datetime = []
       slots_end_datetime = []

       checkin_min = 8
       checkout_max = 18
       organize_values = {
           'employee_slots_fullcalendar_data': employee_fullcalendar_data,
           'open_slots_ids': open_slots,
           'organize_organize_id': organize_sudo,
           'employee': employee_sudo,
           'employee_token': employee_token,
           'organize_token': organize_token,
           'no_data': True
       }
       for slot in organize_slots:
           if organize_sudo.start_datetime <= slot.start_datetime <= organize_sudo.end_datetime:
               if slot.employee_id:
                   employee_fullcalendar_data.append({
                       'title': '%s%s' % (slot.role_id.name or _("Shift"), u' \U0001F4AC' if slot.name else ''),
                       'start': str(pytz.utc.localize(slot.start_datetime).astimezone(employee_tz).replace(tzinfo=None)),
                       'end': str(pytz.utc.localize(slot.end_datetime).astimezone(employee_tz).replace(tzinfo=None)),
                       'color': self._format_organize_shifts(slot.role_id.color),
                       'alloc_hours': '%d:%02d' % (int(slot.allocated_hours), round(slot.allocated_hours % 1 * 60)),
                       'alloc_perc': slot.allocated_percentage,
                       'slot_id': slot.id,
                       'note': slot.name,
                       'allow_self_unassign': slot.allow_self_unassign,
                       'role': slot.role_id.name,
                   })
                   slots_start_datetime.append(pytz.utc.localize(slot.start_datetime).astimezone(employee_tz).replace(tzinfo=None))
                   slots_end_datetime.append(pytz.utc.localize(slot.end_datetime).astimezone(employee_tz).replace(tzinfo=None))
               elif not slot.is_past and (
                       not employee_sudo.organize_role_ids or not slot.role_id or slot.role_id in employee_sudo.organize_role_ids):
                   open_slots.append(slot)

       min_start_datetime = slots_start_datetime and min(slots_start_datetime) or organize_sudo.start_datetime
       max_end_datetime = slots_end_datetime and max(slots_end_datetime) or organize_sudo.end_datetime
       if min_start_datetime.isocalendar()[1] == max_end_datetime.isocalendar()[1]:
           default_view = 'timeGridWeek'
       else:
           default_view = 'dayGridMonth'

       attendances = employee_sudo.resource_calendar_id._work_intervals(
           pytz.utc.localize(organize_sudo.start_datetime),
           pytz.utc.localize(organize_sudo.end_datetime),
           resource=employee_sudo.resource_id, tz=employee_tz
       )
       if attendances and attendances._items:
           checkin_min = min(map(lambda a: a[0].hour, attendances._items))
           checkout_max = max(map(lambda a: a[1].hour, attendances._items))
       if slots_start_datetime and slots_end_datetime:
           event_hour_min = min(map(lambda s: s.hour, slots_start_datetime))
           event_hour_max = max(map(lambda s: s.hour, slots_end_datetime))
           mintime_weekview, maxtime_weekview = self._get_hours_intervals(checkin_min, checkout_max, event_hour_min,
                                                                          event_hour_max)
       else:
           mintime_weekview, maxtime_weekview = checkin_min, checkout_max
       defaut_start = pytz.utc.localize(organize_sudo.start_datetime).astimezone(employee_tz).replace(tzinfo=None)
       if employee_fullcalendar_data or open_slots:
           organize_values.update({
               'employee_slots_fullcalendar_data': employee_fullcalendar_data,
               'open_slots_ids': open_slots,
               'locale': get_lang(request.env).iso_code.split("_")[0],
               'format_datetime': lambda dt, dt_format: tools.format_datetime(request.env, dt, tz=employee_tz.zone, dt_format=dt_format),
               'notification_text': message in ['assign', 'unassign', 'already_assign'],
               'message_slug': message,
               'has_role': any([s.role_id.id for s in open_slots]),
               'has_note': any([s.name for s in open_slots]),
               'start_datetime': organize_sudo.start_datetime,
               'end_datetime': organize_sudo.end_datetime,
               'mintime': '%02d:00:00' % mintime_weekview,
               'maxtime': '%02d:00:00' % maxtime_weekview,
               'default_view': default_view,
               'default_start': defaut_start.date(),
               'no_data': False
           })
       return organize_values

   @http.route('/organize/<string:token_organize>/<string:token_employee>/assign/<int:slot_id>', type="http", auth="public", website=True)
   def organize_self_assign(self, token_organize, token_employee, slot_id, message=False, **kwargs):
       slot_sudo = request.env['organize.slot'].sudo().browse(slot_id)
       if not slot_sudo.exists():
           return request.not_found()

       employee_sudo = request.env['hr.employee'].sudo().search([('employee_token', '=', token_employee)], limit=1)
       if not employee_sudo:
           return request.not_found()

       organize_sudo = request.env['organize.organize'].sudo().search([('access_token', '=', token_organize)], limit=1)
       if not organize_sudo or slot_sudo.id not in organize_sudo.slot_ids._ids:
           return request.not_found()

       if slot_sudo.employee_id:
           return redirect('/organize/%s/%s?message=%s' % (token_organize, token_employee, 'already_assign'))

       slot_sudo.write({'employee_id': employee_sudo.id})
       if message:
           return redirect('/organize/%s/%s?message=%s' % (token_organize, token_employee, 'assign'))
       else:
           return redirect('/organize/%s/%s' % (token_organize, token_employee))

   @http.route('/organize/<string:token_organize>/<string:token_employee>/unassign/<int:shift_id>', type="http", auth="public", website=True)
   def organize_self_unassign(self, token_organize, token_employee, shift_id, message=False, **kwargs):
       slot_sudo = request.env['organize.slot'].sudo().search([('id', '=', shift_id)], limit=1)
       if not slot_sudo or not slot_sudo.allow_self_unassign:
           return request.not_found()

       employee_sudo = request.env['hr.employee'].sudo().search([('employee_token', '=', token_employee)], limit=1)
       if not employee_sudo or employee_sudo.id != slot_sudo.employee_id.id:
           return request.not_found()

       organize_sudo = request.env['organize.organize'].sudo().search([('access_token', '=', token_organize)], limit=1)
       if not organize_sudo or slot_sudo.id not in organize_sudo.slot_ids._ids:
           return request.not_found()

       slot_sudo.write({'employee_id': False})
       if message:
           return redirect('/organize/%s/%s?message=%s' % (token_organize, token_employee, 'unassign'))
       else:
           return redirect('/organize/%s/%s' % (token_organize, token_employee))

   @http.route('/organize/assign/<string:token_employee>/<int:shift_id>', type="http", auth="user", website=True)
   def organize_self_assign_with_user(self, token_employee, shift_id, **kwargs):
       slot_sudo = request.env['organize.slot'].sudo().search([('id', '=', shift_id)], limit=1)
       if not slot_sudo:
           return request.not_found()

       employee = request.env.user.employee_id
       if not employee:
           return request.not_found()

       if not slot_sudo.employee_id:
           slot_sudo.write({'employee_id': employee})

       return redirect('/web?#action=organize.organize_action_open_shift')

   @http.route('/organize/unassign/<string:token_employee>/<int:shift_id>', type="http", auth="user", website=True)
   def organize_self_unassign_with_user(self, token_employee, shift_id, **kwargs):
       slot_sudo = request.env['organize.slot'].sudo().search([('id', '=', shift_id)], limit=1)
       if not slot_sudo or not slot_sudo.allow_self_unassign:
           return request.not_found()

       employee = request.env['hr.employee'].sudo().search([('employee_token', '=', token_employee)], limit=1)
       if not employee:
           employee = request.env.user.employee_id
       if not employee or employee != slot_sudo.employee_id:
           return request.not_found()

       slot_sudo.write({'employee_id': False})

       if request.env.user:
           return redirect('/web?#action=organize.organize_action_open_shift')
       return request.env['ir.ui.view']._render_template('organize.slot_unassign')

   @staticmethod
   def _format_organize_shifts(color_code):

       switch_color = {
           0: '#008784',
           1: '#EE4B39',
           2: '#F29648',
           3: '#F4C609',
           4: '#55B7EA',
           5: '#71405B',
           6: '#E86869',
           7: '#008784',
           8: '#267283',
           9: '#BF1255',
           10: '#2BAF73',
           11: '#8754B0'
       }

       return switch_color[color_code]

   @staticmethod
   def _get_hours_intervals(checkin_min, checkout_max, event_hour_min, event_hour_max):
       if event_hour_min is not None and checkin_min > event_hour_min:
           mintime = max(event_hour_min - 2, 0)
       else:
           mintime = checkin_min
       if event_hour_max and checkout_max < event_hour_max:
           maxtime = min(event_hour_max + 2, 24)
       else:
           maxtime = checkout_max
       return mintime, maxtime


