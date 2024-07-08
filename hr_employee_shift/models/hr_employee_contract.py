# -*- coding: utf-8 -*-
from odoo.exceptions import Warning
from odoo import models, fields, api, _
from datetime import date
from datetime import timedelta
from datetime import datetime


class HrEmployeeContract(models.Model):
    _inherit = 'hr.contract'

    shift_schedule = fields.One2many('hr.shift.schedule', 'rel_hr_schedule', string="Shift Schedule",
                                     help="Shift schedule")
    working_hours = fields.Many2one('resource.calendar', string='Working Schedule', help="Working hours")
    department_id = fields.Many2one('hr.department', string="Department", help="Department",
                                    required=True)
    total_time_shift = fields.Float(string="Total", compute="grand_total_amount")
    responsible_employee_id =  fields.Many2one('hr.employee', string='Responsible Employee', tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")


class HrSchedule(models.Model):
    _name = 'hr.shift.schedule'

    start_date = fields.Date(string="Date From", required=True, help="Starting date for the shift")
    end_date = fields.Date(string="Date To", required=True, help="Ending date for the shift")
    rel_hr_schedule = fields.Many2one('hr.contract')
    hr_shift = fields.Many2one('resource.calendar', string="Shift", required=True, help="Shift", domain=[])
    company_id = fields.Many2one('res.company', string='Company', help="Company")
    total_monday_time = fields.Float("Total monday")
    total_tuesday_time = fields.Float("Total tuesday")
    total_wednesday_time = fields.Float("Total wednesday")
    total_thursday_time = fields.Float("Total thursday")
    total_friday_time = fields.Float("Total friday")
    total_saturday_time = fields.Float("Total saturday")
    total_sunday_time = fields.Float("Total sunday")
    total_time = fields.Float()

    @api.onchange('start_date', 'end_date')
    def get_department(self):
        """Adding domain to  the hr_shift field"""
        hr_department = None
        if self.start_date:
            hr_department = self.rel_hr_schedule.department_id.id
        return {
            'domain': {
                'hr_shift': [('hr_department', '=', hr_department)]
            }
        }

    def write(self, vals):
        self._check_overlap(vals)
        return super(HrSchedule, self).write(vals)

    @api.model
    def create(self, vals):
        self._check_overlap(vals)
        return super(HrSchedule, self).create(vals)

    def _check_overlap(self, vals):
        print("inside overlap")
        if vals.get('start_date', False) and vals.get('end_date', False):
            print("inside 12")
            shifts = self.env['hr.shift.schedule'].search([('rel_hr_schedule', '=', vals.get('rel_hr_schedule'))])
            print("inside overlap erhvfhdvb", shifts)
            for each in shifts:
                print("inside eacg", each)
                if each != shifts[-1]:
                    date_string = vals.get('start_date');
                    start_date = date.fromisoformat(date_string);
                    print("start_date", start_date)
                    print("each.end_date", each.end_date)
                    print("each.start_date", each.start_date)
                    if each.end_date >= start_date and each.start_date <= start_date:
                        raise Warning(_('The dates may not overlap with one another.'))
            if vals.get('start_date') > vals.get('end_date'):
                raise Warning(_('Start date should be less than end date.'))
        return True

    @api.onchange('hr_shift', 'start_date', 'end_date')
    def calculate_total_hours_shift(self):
        for line in self:
            if line.start_date and line.end_date:
                end_date = line.end_date + timedelta(days=1)
                if line.hr_shift:
                    for rec in line.hr_shift:

                        no_of_monday = len(
                            [d_ord for d_ord in range(line.start_date.toordinal(), end_date.toordinal()) if
                             date.fromordinal(d_ord).weekday() == 0])
                        line.total_monday_time = no_of_monday * line.hr_shift.monday_hours

                        no_of_tuesday = len(
                            [d_ord for d_ord in range(line.start_date.toordinal(), end_date.toordinal()) if
                             date.fromordinal(d_ord).weekday() == 1])
                        line.total_tuesday_time = no_of_tuesday * line.hr_shift.tuesday_hours

                        no_of_wednesday = len(
                            [d_ord for d_ord in range(line.start_date.toordinal(), end_date.toordinal()) if
                             date.fromordinal(d_ord).weekday() == 2])
                        line.total_wednesday_time = no_of_wednesday * line.hr_shift.wednesday_hours

                        no_of_thursday = len(
                            [d_ord for d_ord in range(line.start_date.toordinal(), end_date.toordinal()) if
                             date.fromordinal(d_ord).weekday() == 3])
                        line.total_thursday_time = no_of_thursday * line.hr_shift.thursday_hours

                        no_of_friday = len(
                            [d_ord for d_ord in range(line.start_date.toordinal(), end_date.toordinal()) if
                             date.fromordinal(d_ord).weekday() == 4])
                        line.total_friday_time = no_of_friday * line.hr_shift.friday_hours

                        no_of_saturday = len(
                            [d_ord for d_ord in range(line.start_date.toordinal(), end_date.toordinal()) if
                             date.fromordinal(d_ord).weekday() == 5])
                        line.total_saturday_time = no_of_saturday * line.hr_shift.saturday_hours

                        no_of_sunday = len(
                            [d_ord for d_ord in range(line.start_date.toordinal(), end_date.toordinal()) if
                             date.fromordinal(d_ord).weekday() == 6])
                        line.total_sunday_time = no_of_sunday * line.hr_shift.sunday_hours

                        line.total_time = line.total_monday_time + line.total_sunday_time + line.total_saturday_time + line.total_thursday_time + line.total_friday_time + line.total_tuesday_time + line.total_wednesday_time
