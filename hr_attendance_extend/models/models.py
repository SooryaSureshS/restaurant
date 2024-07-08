from xml import etree

from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from datetime import datetime
from datetime import date
from datetime import timedelta


class HrAttendanceInherit(models.Model):
    _inherit = 'hr.attendance'

    attendance_state = fields.Selection([('draft', 'Draft'),
                                         ('approve', 'Approve'),
                                         ('un_approve', 'Unapprove')],
                                        default='draft')

    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id',
                                       readonly=True)

    work_cost = fields.Monetary(string='Cost', readonly=True,
                                compute='_compute_amount', currency_field='company_currency')
    base_pay = fields.Monetary(string='hourly base rate', readonly=True,
                               compute='_compute_amount', currency_field='company_currency')

    def approve_all(self):
        for rec in self:
            rec.write({'attendance_state': 'approve'})

    @api.depends('check_in', 'check_out')
    def _compute_amount(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                attendance.work_cost = round(attendance.worked_hours, 2) * attendance.employee_id.base_pay_rate
                attendance.base_pay = attendance.employee_id.base_pay_rate
            else:
                attendance.work_cost = 0.0
                attendance.base_pay = attendance.employee_id.base_pay_rate

    def un_approve_all(self):
        for rec in self:
            rec.write({'attendance_state': 'un_approve'})

    """hide approve and unapprove from respective form views"""

    def fields_view_get(self, view_id=None, view_type='tree', toolbar=False,
                        submenu=False):
        res = super(HrAttendanceInherit, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        new_tree = 0
        tree_1 = self.env['ir.ui.view'].search([('model', '=', 'hr.attendance')])
        for tree in tree_1:
            if tree.xml_id == 'hr_attendance.hr_attendance_new_tree':
                new_tree = tree.id
        if view_id != new_tree:
            approve_button_id = self.env.ref('hr_attendance_extend.approve_all_server_action').id or False
            for button in res.get('toolbar', {}).get('action', []):
                if approve_button_id and button['id'] == approve_button_id:
                    res['toolbar']['action'].remove(button)
        if view_id == new_tree:
            un_approve_button_id = self.env.ref('hr_attendance_extend.un_approve_all_server_action').id or False
            for button in res.get('toolbar', {}).get('action', []):
                if un_approve_button_id and button['id'] == un_approve_button_id:
                    res['toolbar']['action'].remove(button)
        return res
