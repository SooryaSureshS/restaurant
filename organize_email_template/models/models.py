# -*- coding: utf-8 -*-
from ast import literal_eval
from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
import json
import logging
import pytz
import uuid
from math import ceil, modf
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import format_time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import format_date, format_datetime
import base64
from datetime import date, datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
from pytz import utc

_logger = logging.getLogger(__name__)


class OrganizeInherited(models.Model):
    _inherit = 'organize.slot'

    def _send_slot(self, employee_ids, start_datetime, end_datetime, include_unassigned=True, message=None):
        if not include_unassigned:
            self = self.filtered(lambda s: s.employee_id)
        if not self:
            return False

        employee_with_backend = employee_ids.filtered(
            lambda e: e.user_id and e.user_id.has_group('organize.group_organize_user'))
        employee_without_backend = employee_ids - employee_with_backend
        organize = False
        if len(self) > 1 or employee_without_backend:
            organize = self.env['organize.organize'].create({
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'include_unassigned': include_unassigned,
                'slot_ids': [(6, 0, self.ids)],
            })

        if len(self) > 1:
            return organize._send_organize(message=message, employees=employee_ids)

        self.ensure_one()
        attachements_files = self.send_with_attachment()
        template = self.env.ref('organize.email_template_single')
        employee_url_map = {**employee_without_backend.sudo()._organize_get_url(organize),
                            **employee_with_backend._slot_get_url()}

        view_context = dict(self._context)
        view_context.update({
            'open_shift_available': not self.employee_id,
            'mail_subject': _('Organize: new open shift available'),
        })
        if attachements_files:
            template.attachment_ids = [(6, 0, [attachements_files.id])]
        if self.employee_id:
            employee_ids = self.employee_id
            if self.allow_self_unassign:
                if employee_ids.filtered(lambda e: e.user_id and e.user_id.has_group('organize.group_organize_user')):
                    unavailable_link = '/organize/unassign/%s/%s' % (self.employee_id.sudo().employee_token, self.id)
                else:
                    unavailable_link = '/organize/%s/%s/unassign/%s?message=1' % (
                        organize.access_token, self.employee_id.sudo().employee_token, self.id)
                view_context.update({'unavailable_link': unavailable_link})
            view_context.update({'mail_subject': _('Organize: new shift')})

        mails_to_send_ids = []
        for employee in employee_ids.filtered(lambda e: e.work_email):
            if not self.employee_id and employee in employee_with_backend:
                view_context.update(
                    {'available_link': '/organize/assign/%s/%s' % (employee.sudo().employee_token, self.id)})
            elif not self.employee_id:
                view_context.update({'available_link': '/organize/%s/%s/assign/%s?message=1' % (
                    organize.access_token, employee.sudo().employee_token, self.id)})
            start_datetime, end_datetime = self._format_start_end_datetime(employee.env, tz=employee.tz,
                                                                           lang_code=employee.user_partner_id.lang)
            view_context.update({
                'link': employee_url_map[employee.id],
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'employee_name': employee.name,
                'work_email': employee.work_email,
            })
            mail_id = template.with_context(view_context).send_mail(self.id,
                                                                    notif_layout='mail.mail_notification_light')
            mails_to_send_ids.append(mail_id)

        mails_to_send = self.env['mail.mail'].sudo().browse(mails_to_send_ids)
        if mails_to_send:
            mails_to_send.send()

        self.write({
            'is_published': True,
            'publication_warning': False,
        })

    def send_with_attachment(self):
        import datetime
        context = {
            'company': self.company_id,
        }
        # organize = self.env['organize.slot'].sudo().search([('start_datetime', '>=',
        #                                                      datetime.datetime.now() + relativedelta(weeks=-1, days=1,
        #                                                                                              weekday=0) - datetime.timedelta(
        #                                                          hours=17, minutes=30)),
        #                                                     ('end_datetime', '<=', (
        #                                                             datetime.datetime.now() + relativedelta(
        #                                                         weekday=6)).strftime('%Y-%m-%d'))])
        # report_template_id = self.env.ref(
        #     'organize_email_template.organize_employee_print_badge')._render_qweb_pdf(organize.ids)
        # data_record = base64.b64encode(report_template_id[0])
        #
        # print(data_record, "data_record")

        # ir_values = {
        #     'name': "Weekly Slots Report",
        #     'type': 'binary',
        #     'datas': data_record,
        #     'store_fname': data_record,
        #     'mimetype': 'application/x-pdf',
        # }
        # data_id = self.env['ir.attachment'].sudo().create(ir_values)
        # return data_id


class OrganizeOrganizeInherited(models.Model):
    _inherit = 'organize.organize'

    def _send_organize(self, message=None, employees=False):
        email_from = self.env.user.email or self.env.user.company_id.email or ''
        sent_slots = self.env['organize.slot']
        for t in sent_slots:
            print(t.start_datetime, "lop")
        for organize in self:
            slots = organize.slot_ids
            slots_open = slots.filtered(lambda line: not line.employee_id) if organize.include_unassigned else 0
            employees = employees or slots.mapped('employee_id')
            employee_url_map = employees.sudo()._organize_get_url(organize)
            template = self.env.ref('organize.email_template_organize_organize', raise_if_not_found=False)
            template_context = {
                'slot_unassigned_count': slots_open and len(slots_open),
                'slot_total_count': slots and len(slots),
                'message': message,
            }

            if template:
                attachements_files = self.send_with_attachment()
                if attachements_files:
                    template.attachment_ids = [(6, 0, [attachements_files.id])]

                for employee in self.env['hr.employee.public'].browse(employees.ids):
                    if employee.work_email:
                        template_context['employee'] = employee
                        destination_tz = pytz.timezone(self.env.user.tz or 'UTC')
                        template_context['start_datetime'] = pytz.utc.localize(organize.start_datetime).astimezone(
                            destination_tz).replace(tzinfo=None)
                        template_context['end_datetime'] = pytz.utc.localize(organize.end_datetime).astimezone(
                            destination_tz).replace(tzinfo=None)
                        template_context['organize_url'] = employee_url_map[employee.id]
                        template_context['assigned_new_shift'] = bool(
                            slots.filtered(lambda line: line.employee_id.id == employee.id))
                        template.with_context(**template_context).send_mail(organize.id, email_values={
                            'email_to': employee.work_email, 'email_from': email_from},
                                                                            notif_layout='mail.mail_notification_light')
            sent_slots |= slots
        sent_slots.write({
            'is_published': True,
            'publication_warning': False
        })
        return True

    def send_with_attachment(self):
        from datetime import date
        # organize = self.env['organize.slot'].sudo().search([('start_datetime', '>=',
        #                                                      datetime.datetime.now() + relativedelta(weeks=-1, days=1,
        #                                                                                              weekday=0) - datetime.timedelta(
        #                                                          hours=17, minutes=30)),
        #                                                     ('end_datetime', '<=', (
        #                                                                 datetime.datetime.now() + relativedelta(
        #                                                             weekday=6)).strftime('%Y-%m-%d'))])

        # organize_search = self.env['organize.slot'].sudo().search(
        #     [])
        # start_end_dates = []
        # print(self.start_datetime, self.end_datetime, "the times")
        start_date = self.start_datetime
        end_date = self.end_datetime
        # destination_tz = pytz.timezone('Asia/Kolkata')
        # destination_tz = pytz.timezone(self.env.user.tz or 'Australia/Brisbane')
        #
        #
        #
        # s_date = pytz.utc.localize(self.start_datetime).astimezone(
        #     destination_tz).replace(tzinfo=None)
        # e_date = pytz.utc.localize(self.end_datetime).astimezone(
        #     destination_tz).replace(tzinfo=None)
        # print(s_date,e_date,"vere",start_date,end_date)

        data = {
            "start_date": start_date,
            "end_date": end_date
        }
        # print(s_date,"lopop")
        report_template_id = self.env.ref('organize_email_template.organize_employee_print_badge')._render_qweb_pdf(
            data=data
        )

        data_record = base64.b64encode(report_template_id[0])

        ir_values = {
            'name': "Weekly Slots Report",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/x-pdf',
        }
        data_id = self.env['ir.attachment'].sudo().create(ir_values)
        return data_id
