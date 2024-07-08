# -*- coding: utf-8 -*-
from odoo.exceptions import Warning
from odoo import models, fields, api, _
from datetime import date
from datetime import timedelta, datetime
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import pytz


class HrLeaveInherit(models.Model):
    _inherit = "hr.leave"

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),  # YTI This state seems to be unused. To remove
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
    ], string='Status', store=True, tracking=True, copy=False, readonly=False,
        help="The status is set to 'To Submit', when a time off request is created." +
             "\nThe status is 'To Approve', when time off request is confirmed by user." +
             "\nThe status is 'Refused', when time off request is refused by manager." +
             "\nThe status is 'Approved', when time off request is approved by manager.")

    recurring_leave = fields.Boolean()
    request_hour_from = fields.Selection(selection='_get_valid_hours')
    request_hour_to = fields.Selection(selection='_get_valid_hours')

    @api.model
    def _get_valid_hours(self):
        selection = [
            ('11.00', '11:00 AM'), ('11.25', '11:15 AM'), ('11.50', '11:30 AM'), ('11.75', '11:45 AM'),
            ('12.00', '12:00 PM'), ('12.25', '12:15 PM'), ('12.50', '12:30 PM'), ('12.75', '12:45 PM'),
            ('13.00', '1:00 PM'), ('13.25', '1:15 PM'), ('13.50', '1:30 PM'), ('13.75', '1:45 PM'),
            ('14.00', '2:00 PM'), ('14.25', '2:15 PM'), ('14.50', '2:30 PM'), ('14.75', '2:45 PM'),
            ('15.00', '3:00 PM'), ('15.25', '3:15 PM'), ('15.50', '3:30 PM'), ('15.75', '3:45 PM'),
            ('16.00', '4:00 PM'), ('16.25', '4:15 PM'), ('16.50', '4:30 PM'), ('16.75', '4:45 PM'),
            ('17.00', '5:00 PM'), ('17.25', '5:15 PM'), ('17.50', '5:30 PM'), ('17.75', '5:45 PM'),
            ('18.00', '6:00 PM'), ('18.25', '6:15 PM'), ('18.50', '6:30 PM'), ('18.75', '6:45 PM'),
            ('19.00', '7:00 PM'), ('19.25', '7:15 PM'), ('19.50', '7:30 PM'), ('19.75', '7:45 PM'),
            ('20.00', '8:00 PM'), ('20.25', '8:15 PM'), ('20.50', '8:30 PM'), ('20.75', '8:45 PM'),
            ('21.00', '9:00 PM'), ('21.25', '9:15 PM'), ('21.50', '9:30 PM'), ('21.75', '9:45 PM'),
            ('22.00', '10:00 PM'), ('22.25', '10:15 PM'), ('22.50', '10:30 PM'), ('22.75', '10:45 PM'),
            ('23.00', '11:00 PM'), ('23.25', '11:15 PM'), ('23.50', '11:30 PM'),
        ]
        return selection

    @api.depends('number_of_days')
    def _compute_number_of_hours_display(self):
        res = super(HrLeaveInherit, self)._compute_number_of_hours_display()
        for holiday in self:
            if holiday.request_unit_hours:
                if holiday.request_hour_from and holiday.request_hour_to:
                    # raise ValidationError(_("From time should be greater than To Time !! "))
                    if holiday.date_to != 0 and holiday.date_from != 0:
                        number_of_hours_display = (((holiday.date_to - holiday.date_from).total_seconds()) / 60) / 60
                        if holiday.request_hour_from > holiday.request_hour_to:
                            number_of_hours_display = 24 + number_of_hours_display
                            holiday.number_of_hours_display = str(number_of_hours_display)
                        else:
                            if '-' in str(number_of_hours_display):
                                holiday.number_of_hours_display = str(number_of_hours_display).replace('-', '')
                            else:
                                holiday.number_of_hours_display = str(number_of_hours_display)
        return res



class RecurringLeave(models.Model):
    _name = 'recurring.leave'
    _description = 'Recurring leaves'

    holiday_status_id = fields.Many2one(
        "hr.leave.type", string="Time Off Type",
        domain=[('valid', '=', True), ('allocation_type', '!=', 'no')])

    @api.model
    def _default_leave_ids(self):
        leave_ids = []
        timings = ['11.00', '11.25', '11.50', '11.75', '12.00', '12.25', '12.50', '12.75', '13.00', '13.25', '13.50',
                   '13.75', '14.00', '14.25',
                   '14.50', '14.75', '15.00', '15.25', '15.50', '15.75', '16.00', '16.25', '16.50', '16.75',
                   '17.00', '17.25', '17.50', '17.75', '18.00', '18.25', '18.50', '18.75', '19.00', '19.25', '19.50',
                   '19.75', '20.00', '20.25',
                   '20.50', '20.75', '21.00', '21.25', '21.50', '21.75', '22.00', '22.25', '22.50', '22.75', '23.00',
                   ]
        for line in timings:
            leave_ids += [(0, 0, {
                'timings': line,
            })]
        return leave_ids

    name = fields.Char(compute='set_display_name')
    employee_id = fields.Many2one('hr.employee')
    mode_company_id = fields.Many2one(
        'res.company', compute='_compute_from_holiday_type', store=True, string='Company Mode',
        stages={'confirm': [('readonly', True)]})
    leave_ids = fields.One2many('recurring.leave.line', 'recurring_id', default=_default_leave_ids)
    stages = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('refuse', 'Refused'),
    ], string='Stages', default='draft')
    request_date_from = fields.Date('Start Date', required=True)
    request_date_to = fields.Date('End Date', required=True)

    holiday_type = fields.Selection([
        ('employee', 'By Employee'),
        ('company', 'By Company'),
        ('department', 'By Department'),
        ('category', 'By Employee Tag')],
        string='Allocation Mode', readonly=True, required=True, default='employee')

    category_id = fields.Many2one(
        'hr.employee.category', compute='_compute_from_holiday_type', store=True, string='Employee Tag',
        stages={'draft': [('readonly', False)], 'confirm': [('readonly', True)]}, help='Category of Employee')

    department_id = fields.Many2one(
        'hr.department', compute='_compute_department_id', store=True, string='Department', readonly=False,
        stages={'draft': [('readonly', False)], 'confirm': [('readonly', True)]}, )

    @api.onchange('employee_id')
    def set_display_name(self):
        if self.employee_id:
            self.name = self.employee_id.name + "'s recurring timeoff's "
        else:
            self.name = "Recurring timeoff's "

    def action_confirm(self):
        self.stages = 'confirmed'

    def action_approve(self):
        leaves = []
        current_employee = self.env.user.employee_id
        current_uid = self.env.user
        tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
        leave_count = []
        timing_dict = {'11.00': 11.00,
                       '11.25': 11.25,
                       '11.50': 11.50, '11.75': 11.75, '12.00': 12.00, '12.25': 12.25, '12.50': 12.50, '12.75': 12.75,
                       '13.00': 13.00,
                       '13.25': 13.25,
                       '13.50': 13.50, '13.75': 13.75, '14.00': 14.00, '14.25': 14.25,
                       '14.50': 14.50, '14.75': 14.75, '15.00': 15.00, '15.25': 15.25, '15.50': 15.50, '15.75': 15.75,
                       '16.00': 16.00,
                       '16.25': 16.25,
                       '16.50': 16.50, '16.75': 16.75,
                       '17.00': 17.00, '17.25': 17.25, '17.50': 17.50, '17.75': 17.75, '18.00': 18.00, '18.25': 18.25,
                       '18.50': 18.50,
                       '18.75': 18.75,
                       '19.00': 19.00, '19.25': 19.25, '19.50': 19.50, '19.75': 19.75, '20.00': 20.00, '20.25': 20.25,
                       '20.50': 20.50, '20.75': 20.75, '21.00': 21.00, '21.25': 21.25, '21.50': 21.50, '21.75': 21.75,
                       '22.00': 22.00,
                       '22.25': 22.25, '22.50': 22.50, '22.75': 22.75, '23.00': 23.00,

                       }
        leave_type_id = self.env['hr.leave.type'].search([('name', '=', "Recurring time off")], limit=1)
        if not leave_type_id:
            leave_type_id = self.env['hr.leave.type'].create({'name': "Recurring time off",
                                                              'request_unit': 'hour',
                                                              'allocation_type': 'no',
                                                              'leave_validation_type': 'manager',
                                                              })

        if self.request_date_from and self.request_date_to:
            delta = self.request_date_to - self.request_date_from
            days = [self.request_date_from + timedelta(days=i) for i in range(delta.days + 1)]
            mondays = [day for day in days if day.weekday() == 0]
            tuesdays = [day for day in days if day.weekday() == 1]
            wednesdays = [day for day in days if day.weekday() == 2]
            thursdays = [day for day in days if day.weekday() == 3]
            fridays = [day for day in days if day.weekday() == 4]
            saturdays = [day for day in days if day.weekday() == 5]
            sundays = [day for day in days if day.weekday() == 6]

        if self.leave_ids:
            for line in self.leave_ids:
                if line.have_true == True:
                    start_hours = timing_dict[str(line.timings)]
                    if start_hours > 22.30:
                        end_hours = 23.30
                    else:
                        end_hours = start_hours + 1
                        if str(round(end_hours, 2))[3] == '6':
                            end_hours = int(end_hours) + 1.00
                    line_weeks = []
                    if line.monday == True:
                        line_weeks += mondays
                    if line.tuesday == True:
                        line_weeks += tuesdays
                    if line.wednesday == True:
                        line_weeks += wednesdays
                    if line.thursday == True:
                        line_weeks += thursdays
                    if line.friday == True:
                        line_weeks += fridays
                    if line.saturday == True:
                        line_weeks += saturdays
                    if line.sunday == True:
                        line_weeks += sundays

                    for dte in line_weeks:
                        domain = [
                            ('date_from', '<', dte + relativedelta(hours=float(end_hours - 5),
                                                                   minutes=-30)),
                            ('date_to', '>', dte + relativedelta(
                                hours=float(start_hours - 5), minutes=-30)),
                            ('employee_id', '=', self.employee_id.id),
                            # ('id', '!=', holiday.id),
                            ('state', 'not in', ['cancel', 'refuse']),
                        ]
                        if self.env['hr.leave'].search_count(domain):
                            continue
                        hours = {
                            '25': 15,
                            '50': 30,
                            '75': 45,
                            '00': 00
                        }
                        start = str(round(start_hours, 2)).split('.')[1]
                        end = str(round(end_hours, 2)).split('.')[1]
                        if len(start) == 1:
                            start = start + '0'
                        if len(end) == 1:
                            end = end + '0'
                        start = hours[start]
                        end = hours[end]
                        date_from = dte + relativedelta(hours=int(start_hours), minutes=(int(start)))
                        date_to = dte + relativedelta(hours=int(end_hours), minutes=(int(end)))
                        leaves.append({'employee_id': self.employee_id.id,
                                       'request_date_from': datetime.strptime(str(dte), "%Y-%m-%d"),
                                       'request_unit_hours': True,
                                       'request_hour_from': "{:.2f}".format(start_hours),
                                       'request_hour_to': "{:.2f}".format(end_hours),
                                       'holiday_status_id': leave_type_id.id,
                                       'holiday_type': 'employee',
                                       'number_of_days': 1 / 8,
                                       'date_from': date_from - relativedelta(hours=5, minutes=30),
                                       'date_to': date_to - relativedelta(hours=5, minutes=30),
                                       'first_approver_id': current_employee.id,
                                       'state': 'validate',
                                       'recurring_leave': True
                                       })
            self.env['hr.leave'].with_context(
                tracking_disable=True,
                mail_activity_automation_skip=True,
                leave_fast_create=True,
                leave_skip_state_check=True
            ).create(leaves)
            self.env.cr.commit()
        else:
            raise ValidationError(_("There is no time off's !! "))
        self.stages = 'approved'

    def action_refuse(self):
        self.stages = 'refuse'

    @api.depends('holiday_type')
    def _compute_from_holiday_type(self):
        for allocation in self:
            if allocation.holiday_type == 'employee':
                if not allocation.employee_id:
                    allocation.employee_id = self.env.user.employee_id
                allocation.mode_company_id = False
                allocation.category_id = False
            if allocation.holiday_type == 'company':
                allocation.employee_id = False
                if not allocation.mode_company_id:
                    allocation.mode_company_id = self.env.company
                allocation.category_id = False
            elif allocation.holiday_type == 'department':
                allocation.employee_id = False
                allocation.mode_company_id = False
                allocation.category_id = False
            elif allocation.holiday_type == 'category':
                allocation.employee_id = False
                allocation.mode_company_id = False
            elif not allocation.employee_id and not allocation._origin.employee_id:
                allocation.employee_id = self.env.context.get('default_employee_id') or self.env.user.employee_id


class RecurringLeaveLine(models.Model):
    _name = "recurring.leave.line"

    have_true = fields.Boolean(compute='check_weeks')
    monday = fields.Boolean()
    tuesday = fields.Boolean()
    wednesday = fields.Boolean()
    thursday = fields.Boolean()
    friday = fields.Boolean()
    saturday = fields.Boolean()
    sunday = fields.Boolean()
    week_types = fields.Selection([('sunday', 'Sunday'),
                                   ('monday', 'Monday'),
                                   ('tuesday', 'Tuesday'),
                                   ('wednesday', 'Wednesday'),
                                   ('thursday', 'Thursday'),
                                   ('friday', 'Friday'),
                                   ('saturday', 'Saturday')
                                   ])
    recurring_id = fields.Many2one('recurring.leave')
    request_date_from = fields.Date('Request Start Date')
    request_date_to = fields.Date('Request End Date')
    timings = fields.Selection([
        ('11.00', '11:00 AM'), ('11.25', '11:15 AM'), ('11.50', '11:30 AM'), ('11.75', '11:45 AM'),
        ('12.00', '12:00 PM'), ('12.25', '12:15 PM'), ('12.50', '12:30 PM'), ('12.75', '12:45 PM'),
        ('13.00', '1:00 PM'), ('13.25', '1:15 PM'), ('13.50', '1:30 PM'), ('13.75', '1:45 PM'),
        ('14.00', '2:00 PM'), ('14.25', '2:15 PM'), ('14.50', '2:30 PM'), ('14.75', '2:45 PM'),
        ('15.00', '3:00 PM'), ('15.25', '3:15 PM'), ('15.50', '3:30 PM'), ('15.75', '3:45 PM'),
        ('16.00', '4:00 PM'), ('16.25', '4:15 PM'), ('16.50', '4:30 PM'), ('16.75', '4:45 PM'),
        ('17.00', '5:00 PM'), ('17.25', '5:15 PM'), ('17.50', '5:30 PM'), ('17.75', '5:45 PM'),
        ('18.00', '6:00 PM'), ('18.25', '6:15 PM'), ('18.50', '6:30 PM'), ('18.75', '6:45 PM'),
        ('19.00', '7:00 PM'), ('19.25', '7:15 PM'), ('19.50', '7:30 PM'), ('19.75', '7:45 PM'),
        ('20.00', '8:00 PM'), ('20.25', '8:15 PM'), ('20.50', '8:30 PM'), ('20.75', '8:45 PM'),
        ('21.00', '9:00 PM'), ('21.25', '9:15 PM'), ('21.50', '9:30 PM'), ('21.75', '9:45 PM'),
        ('22.00', '10:00 PM'), ('22.25', '10:15 PM'), ('22.50', '10:30 PM'), ('22.75', '10:45 PM'),
        ('23.00', '11:00 PM'),
    ])

    @api.depends('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
    def check_weeks(self):
        for line in self:
            if True in [line.monday, line.tuesday, line.wednesday, line.thursday, line.friday, line.saturday,
                        line.sunday]:
                line.have_true = True
            else:
                line.have_true = False
