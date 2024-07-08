# Company: giordano.ch AG
# Copyright by: giordano.ch AG
# https://giordano.ch/

import json
from odoo import http
from odoo.http import request
from datetime import date
from babel.dates import format_date
from odoo.tools.misc import get_lang
from odoo.addons.appointment.controllers.main import Appointment


class ObstAppointment(Appointment):

    @staticmethod
    def _formated_weekdays(locale):
        """
        Generates a list of formatted weekdays in the specified locale format.

        Args:
        locale (str): The locale for formatting the weekdays.

        Returns:
        list: A list of formatted weekdays.
        """
        formated_days = [
            format_date(date(2021, 3, day), 'EEE', locale=locale)
            for day in range(1, 8)]
        return formated_days

    @http.route(['/book-us',
                 '/book-us/<int:form_type_id>'], type='http', website=True,
                auth='public')
    def obst_book_us(self, form_type_id=None, **kwargs):
        """Route for booking appointments.

          This function fetches the calendar appointment type for the given form type id,
          retrieves the appointment slots for the selected appointment type, and returns
          a render response of the 'gio_obstgemuese_theme.obst_book_us_template' template.
          The render context includes appointment type, suggested employees, timezone,
          slots, state, filter appointment type ids, formatted days, and selected form id.

          Args:
              form_type_id (int): The id of the appointment form type.
              kwargs (dict): Additional keyword arguments.

          Returns:
              Render response of the 'gio_obstgemuese_theme.obst_book_us_template' template.
        """
        form_type_id = kwargs.get('form_id')
        appointment_type_obj = request.env['calendar.appointment.type']
        appointment_type = appointment_type_obj.sudo().search([('id', '=',
                                                                form_type_id)]) if form_type_id else appointment_type_obj.sudo().search(
            [('is_published', '=', True)], limit=1)
        timezone = None
        filter_employee_ids = None
        appointment_type = appointment_type.sudo()
        request.session[
            'timezone'] = timezone or appointment_type.appointment_tz
        try:
            filter_employee_ids = json.loads(
                filter_employee_ids) if filter_employee_ids else []
        except json.decoder.JSONDecodeError:
            raise ValueError()

        if appointment_type.assign_method == 'chosen' and not filter_employee_ids:
            suggested_employees = appointment_type.employee_ids
        else:
            suggested_employees = appointment_type.employee_ids.filtered(
                lambda emp: emp.id in filter_employee_ids)
        employee_id = None
        if not suggested_employees and employee_id and int(
                employee_id) in appointment_type.employee_ids.ids:
            suggested_employees = request.env['hr.employee'].sudo().browse(
                int(employee_id))

        default_employee = suggested_employees[0] if suggested_employees else \
            request.env['hr.employee']
        slots = appointment_type._get_appointment_slots(
            request.session['timezone'], default_employee)
        formated_days = self._formated_weekdays(get_lang(request.env).code)
        return request.render('gio_obstgemuese_theme.obst_book_us_template', {
            'appointment_type': appointment_type,
            'suggested_employees': suggested_employees,
            'main_object': appointment_type,
            'timezone': request.session['timezone'],
            'slots': slots,
            'state': None,
            'filter_appointment_type_ids': None,
            'formated_days': formated_days,
            'selected_form_id': form_type_id
        })
