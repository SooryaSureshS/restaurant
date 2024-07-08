# -*- coding: utf-8 -*-
from odoo.exceptions import Warning
from odoo import models, fields, api, _
from datetime import datetime
from datetime import  date
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    current_contract_time = fields.Float(compute='computing_work_times')
    used_time = fields.Float(compute='computing_work_times')
    employee_id = fields.Many2one('hr.employee')
    employee_ids = fields.One2many('hr.employee', 'employee_id', string="Shift Schedule", help="Shift schedule")
    overdue = fields.Boolean(compute='computing_work_times')
    weekly_used_time = fields.Float(compute='computing_work_times')
    current_week_time = fields.Float(compute='computing_work_times')
    scheduling_manager = fields.Many2one('hr.employee', required=True)
    scheduling_manager_user_id = fields.Integer(compute='computing_work_times')
    current_user_id = fields.Integer(compute='computing_work_times')
    user_checking = fields.Boolean(compute='computing_work_times')



    @api.depends('name')
    def computing_work_times(self):
        for rec in self:
            rec_id = 0
            if type(rec.id) != int:
                try:
                    rec_d = rec.id
                    rec_id = int(str(rec.id).split('_')[1])
                except:
                    rec.used_time = 0
                    rec.current_contract_time = 0
                    rec.weekly_used_time = 0
                    pass
            else:
                rec_id = rec.id
            if rec_id != 0:
                current_contract_id = self.env['hr.contract'].search([('employee_id', '=', rec_id), ('state', '=', 'open')])
                if current_contract_id:
                    if current_contract_id.date_start:
                        start_date = datetime.strptime(str(current_contract_id.date_start), "%Y-%m-%d")
                        if current_contract_id.date_end:
                            end_date = datetime.strptime(str(current_contract_id.date_end), "%Y-%m-%d")
                            attendance = self.env['hr.attendance'].search([('employee_id', '=', rec_id), ('check_in', '<=', end_date), ('check_out', '>=', start_date)]).mapped('worked_hours')
                        else:
                            attendance = self.env['hr.attendance'].search([('employee_id', '=', rec_id),('check_out', '>=', start_date)]).mapped('worked_hours')
                        if attendance:
                            sum_attendance = sum(attendance)
                            rec.used_time = sum_attendance
                            rec.current_contract_time = current_contract_id.total_time_shift
                        else:
                            rec.used_time = 0
                            rec.current_contract_time = current_contract_id.total_time_shift
                    else:
                        rec.used_time = 0
                        rec.current_contract_time = 0

                else:
                    rec.used_time = 0
                    rec.current_contract_time = 0

                week_attendance = self.env['hr.attendance'].search(
                    [('employee_id', '=', rec_id), ('check_out', '>=' ,datetime.now() + relativedelta(days=-7)),
                                               ('check_out', '<=' ,datetime.now()),('check_in', '>=' ,datetime.now() + relativedelta(days=-7)),
                                               ('check_in', '<=' ,datetime.now())]).mapped('worked_hours')
                if week_attendance:
                    rec.weekly_used_time = sum(week_attendance)
                else:
                    rec.weekly_used_time = 0

            if rec.used_time > rec.current_contract_time:
                rec.overdue = True
            else:
                rec.overdue = False

            if rec.scheduling_manager:
               rec.scheduling_manager_user_id = rec.scheduling_manager.user_id.id
               rec.current_user_id = self.env.user.id
               if rec.scheduling_manager_user_id == rec.current_user_id:
                   rec.user_checking = True
               else:
                   rec.user_checking = False
            else:
               rec.scheduling_manager_user_id = 1
               rec.current_user_id = self.env.user.id
               if rec.scheduling_manager_user_id == rec.current_user_id:
                   rec.user_checking = True
               else:
                   rec.user_checking = False


