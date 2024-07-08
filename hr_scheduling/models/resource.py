# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date
from datetime import timedelta


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    total_hours = fields.Float("Total hours", compute="calculate_total_hours")
    monday_hours = fields.Float(compute="calculate_total_hours")
    tuesday_hours = fields.Float(compute="calculate_total_hours")
    wednesday_hours = fields.Float(compute="calculate_total_hours")
    thursday_hours = fields.Float(compute="calculate_total_hours")
    friday_hours = fields.Float(compute="calculate_total_hours")
    saturday_hours = fields.Float(compute="calculate_total_hours")
    sunday_hours = fields.Float(compute="calculate_total_hours")

    @api.onchange('hours_per_day')
    def calculate_total_hours(self):
        if self.attendance_ids:
            self.total_hours = sum([line.hour_to - line.hour_from for line in self.attendance_ids])
            self.monday_hours = sum(
                [line.hour_to - line.hour_from for line in self.attendance_ids if line.dayofweek == '0'])
            self.tuesday_hours = sum(
                [line.hour_to - line.hour_from for line in self.attendance_ids if line.dayofweek == '1'])
            self.wednesday_hours = sum(
                [line.hour_to - line.hour_from for line in self.attendance_ids if line.dayofweek == '2'])
            self.thursday_hours = sum(
                [line.hour_to - line.hour_from for line in self.attendance_ids if line.dayofweek == '3'])
            self.friday_hours = sum(
                [line.hour_to - line.hour_from for line in self.attendance_ids if line.dayofweek == '4'])
            self.saturday_hours = sum(
                [line.hour_to - line.hour_from for line in self.attendance_ids if line.dayofweek == '5'])
            self.sunday_hours = sum(
                [line.hour_to - line.hour_from for line in self.attendance_ids if line.dayofweek == '6'])
