# -*- coding: utf-8 -*-
from datetime import datetime
import pytz
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class SafeCountReportLogin(models.TransientModel):
    _name = 'safe.count.report.login'
    _description = 'Safe Count Report Login'

    user_id = fields.Many2one('res.users', string='Login User',
                              domain="[('safe_screen_user', 'in', ('user', 'manager'))]")

    login_pin = fields.Integer(string="Pin")
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    get_all_safe_count_report = fields.Boolean(string="Get All Safe Counts")

    def get_safe_details(self, docs):
        safe_count_ids = self.env['safe.count']
        if docs.user_id and not docs.get_all_safe_count_report:
            safe_count_ids = self.env['safe.count'].search(
                [('manager_name', '=', docs.user_id.id), ('date', '>=', docs.start_date),
                 ('date', '<=', docs.end_date)])
        elif docs.get_all_safe_count_report:
            safe_count_ids = self.env['safe.count'].search([('date', '>=', docs.start_date),
                                                            ('date', '<=', docs.end_date)])
        lst = []
        for safe_count in safe_count_ids:
            sub_lst = [safe_count.manager_name.name, safe_count.hundred_dollar, safe_count.fifty_dollar,
                       safe_count.twenty_dollar, safe_count.ten_dollar, safe_count.five_dollar, safe_count.two_dollar,
                       safe_count.one_dollar, safe_count.fifty_cent, safe_count.twenty_cent, safe_count.ten_cent,
                       safe_count.five_cent, safe_count.safe_amount,safe_count.date.strftime("%m-%d-%Y"),safe_count.petty_cash]
            lst.append(sub_lst)
        return lst

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError(_('Start Date cannot be greater than  End Date'))

    def get_safe_count_report(self):
        safe_count_ids = self.env['safe.count']
        if self.user_id and not self.get_all_safe_count_report:
            safe_count_ids = self.env['safe.count'].search(
                [('manager_name', '=', self.user_id.id), ('date', '>=', self.start_date),
                 ('date', '<=', self.end_date)])
        elif self.get_all_safe_count_report:
            safe_count_ids = self.env['safe.count'].search([('date', '>=', self.start_date),
                                                            ('date', '<=', self.end_date)])
        if len(safe_count_ids) <= 0:
            raise ValidationError(_('No data found'))
        if self.get_all_safe_count_report:
            return self.env.ref('safe_count.safe_count_report_record').report_action(self)
        if self.user_id and not self.login_pin:
            raise ValidationError(_('Please Enter Pin'))
        if self.user_id and self.login_pin != self.user_id.safe_login_pin:
            raise ValidationError(_('Pin entered is wrong'))
        if self.user_id and self.get_all_safe_count_report:
            raise ValidationError(_('Cannot give both Login User or Get All Employees Sale Data'))
        elif not self.user_id and not self.get_all_safe_count_report:
            raise ValidationError(_('Please give Login User or Get Safe count Reports'))

        return self.env.ref('safe_count.safe_count_report_record').report_action(self)


    def get_cash_collection_report(self):
        if self.user_id and not self.login_pin:
            raise ValidationError(_('Please Enter Pin'))
        if self.user_id and self.login_pin != self.user_id.safe_login_pin:
            raise ValidationError(_('Pin entered is wrong'))
        elif not self.user_id or not self.start_date or not self.end_date:
            raise ValidationError(_('Please provide Login User, Start date, End date'))
        datas = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

        return self.env.ref('pos_summary_backend.action_report_cashcollection').report_action(self, datas)


class SafeCountLogin(models.TransientModel):
    _name = 'safe.count.login'
    _description = 'Safe Count Login'

    user_id = fields.Many2one('res.users', string='Login User',
                              domain="[('safe_screen_user', '=', 'manager')]", required=True)
    login_pin = fields.Integer(string="Pin", required=True)

    def open_safe_count_view(self):
        if self.login_pin != self.user_id.safe_login_pin:
            raise ValidationError(_('Incorrect Login Pin'))
        view_id = self.env.ref('safe_count.safe_count_form').id
        most_recent_safe_count = self.env['safe.count'].search([('manager_name', '=', self.user_id.id)],
                                                               order='create_date desc', limit=1)
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)], limit=1)
        if most_recent_safe_count:
            exp_safe_amt = most_recent_safe_count.safe_amount
            expenses = self.env['hr.expense'].search(
                [('create_date', '>', most_recent_safe_count.date), ('state', '=', 'done'),('employee_id','=',employee_id.id)])
            petty_cash = sum(expenses.mapped('total_amount'))
        else:
            expenses = self.env['hr.expense'].search(
                [('state', '=', 'done'),
                 ('employee_id', '=', employee_id.id)])
            petty_cash = sum(expenses.mapped('total_amount'))
            exp_safe_amt = 0

        return {
            'name': 'Report',
            'view_type': 'form',
            'view_mode': 'from',
            'views': [(view_id, 'form')],
            'res_model': 'safe.count',
            'view_id': view_id,
            'context': {'default_manager_name': self.user_id.id, 'default_expected_safe_amount': exp_safe_amt,'default_petty_cash':petty_cash},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }


class SafeCount(models.Model):
    _name = 'safe.count'
    _description = 'Safe Count'

    manager_name = fields.Many2one('res.users', string="Manager Name",domain="[('safe_screen_user', 'in', ('user', "
                                                                             "'manager'))]", required=True,readonly=True)
    name = fields.Char(string='Order Reference', default=lambda self: _('New'))

    def _default_time_set(self):
        return datetime.now()

    date = fields.Datetime(string="Date", required=True,default=_default_time_set)
    expected_safe_amount = fields.Float(string="Expected Safe Amount", readonly=True)
    safe_amount = fields.Float(string="Safe Amount", readonly=True)
    variance = fields.Float(string="Variance",readonly=True)
    hundred_dollar = fields.Integer(string="$100")
    total_hundred_dollar = fields.Float(string='=',readonly=True)
    fifty_dollar = fields.Integer(string="$50")
    total_fifty_dollar = fields.Float(string="=",readonly=True)
    twenty_dollar = fields.Integer(string="$20")
    total_twenty_dollar = fields.Float(string="=",readonly=True)
    ten_dollar = fields.Integer(string="$10")
    total_ten_dollar = fields.Float(string="=",readonly=True)
    five_dollar = fields.Integer(string="$5")
    total_five_dollar = fields.Float(string="=",readonly=True)
    two_dollar = fields.Integer(string="$2")
    total_two_dollar = fields.Float(string="=",readonly=True)
    one_dollar = fields.Integer(string="$1")
    total_one_dollar = fields.Float(string="=",readonly=True)
    fifty_cent = fields.Integer(string="50c")
    total_fifty_cent = fields.Float(string="=",readonly=True)
    twenty_cent = fields.Integer(string="20c")
    total_twenty_cent = fields.Float(string="=",readonly=True)
    ten_cent = fields.Integer(string="10c")
    total_ten_cent = fields.Float(string="=",readonly=True)
    five_cent = fields.Integer(string="5c")
    total_five_cent = fields.Float(string="=",readonly=True)
    make_readonly = fields.Boolean('Enable Readonly', default=False)
    petty_cash = fields.Float('Petty Cash',readonly=True)

    @api.model
    def create(self,vals):
        most_recent_safe_count = self.env['safe.count'].search([('manager_name', '=', self._context.get('default_manager_name'))],
                                                               order='create_date desc', limit=1)
        res = super(SafeCount,self).create(vals)
        res.name = "Safe Count "+ str(res.id)
        res.expected_safe_amount = most_recent_safe_count.safe_amount
        employee_id = self.env['hr.employee'].search([('user_id', '=', self._context.get('default_manager_name'))], limit=1)
        expenses = self.env['hr.expense'].search([('create_date', '>', most_recent_safe_count.date), ('state', '=', 'done'),('employee_id','=',employee_id.id)])
        res.petty_cash = sum(expenses.mapped('total_amount'))
        res.variance = abs(res.safe_amount - res.expected_safe_amount)
        res.make_readonly = True
        return res

    @api.onchange('hundred_dollar')
    def onchange_hundred_dollar(self):
        if self.hundred_dollar:
            self.total_hundred_dollar = 100 * self.hundred_dollar
        else:
            self.total_hundred_dollar = 0

    @api.onchange('fifty_dollar')
    def onchange_fifty_dollar(self):
        if self.fifty_dollar:
            self.total_fifty_dollar = 50 * self.fifty_dollar
        else:
            self.total_fifty_dollar = 0

    @api.onchange('twenty_dollar')
    def onchange_twenty_dollar(self):
        if self.twenty_dollar:
            self.total_twenty_dollar = 20 * self.twenty_dollar
        else:
            self.total_twenty_dollar = 0

    @api.onchange('ten_dollar')
    def onchange_ten_dollar(self):
        if self.ten_dollar:
            self.total_ten_dollar = 10 * self.ten_dollar
        else:
            self.total_ten_dollar = 0

    @api.onchange('five_dollar')
    def onchange_five_dollar(self):
        if self.five_dollar:
            self.total_five_dollar = 5 * self.five_dollar
        else:
            self.total_five_dollar = 0

    @api.onchange('two_dollar')
    def onchange_two_dollar(self):
        if self.two_dollar:
            self.total_two_dollar = 2 * self.two_dollar
        else:
            self.total_two_dollar = 0

    @api.onchange('one_dollar')
    def onchange_one_dollar(self):
        if self.one_dollar:
            self.total_one_dollar = 1 * self.one_dollar
        else:
            self.total_one_dollar = 0

    @api.onchange('fifty_cent')
    def onchange_fifty_cent(self):
        if self.fifty_cent:
            self.total_fifty_cent = 50 * self.fifty_cent
        else:
            self.total_fifty_cent = 0

    @api.onchange('twenty_cent')
    def onchange_twenty_cent(self):
        if self.twenty_cent:
            self.total_twenty_cent = 20 * self.twenty_cent
        else:
            self.total_twenty_cent = 0

    @api.onchange('ten_cent')
    def onchange_ten_cent(self):
        if self.ten_cent:
            self.total_ten_cent = 10 * self.ten_cent
        else:
            self.total_ten_cent = 0

    @api.onchange('five_cent')
    def onchange_five_cent(self):
        if self.five_cent:
            self.total_five_cent = 5 * self.five_cent
        else:
            self.total_five_cent = 0

    @api.onchange('total_hundred_dollar', 'total_fifty_dollar', 'total_twenty_dollar', 'total_ten_dollar',
                  'total_five_dollar', 'total_two_dollar', 'total_one_dollar', 'total_fifty_cent', 'total_twenty_cent',
                  'total_ten_cent', 'total_five_cent')
    def total_safe_amount(self):
        self.safe_amount = self.total_hundred_dollar + self.total_fifty_dollar + self.total_twenty_dollar + self.total_ten_dollar + self.total_five_dollar + self.total_two_dollar + self.total_one_dollar + (
                0.01 * self.total_fifty_cent) + (0.01 * self.total_twenty_cent) + (0.01 * self.total_ten_cent) + (
                                   0.01 * self.total_five_cent)

    @api.onchange('safe_amount')
    def calc_variance(self):
        most_recent_safe_count = self.env['safe.count'].search([('manager_name', '=', self.manager_name.id)],
                                                               order='create_date desc', limit=1)
        self.expected_safe_amount = most_recent_safe_count.safe_amount
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.manager_name.id)], limit=1)
        expenses = self.env['hr.expense'].search([('create_date','>',most_recent_safe_count.date),('state','=','done'),('employee_id','=',employee_id.id)])
        self.petty_cash = sum(expenses.mapped('total_amount'))
        self.variance = abs(self.safe_amount - self.expected_safe_amount)


class ResUsers(models.Model):
    _inherit = 'res.users'

    safe_login_pin = fields.Integer(string="Safe Count Login Pin")
    safe_screen_user = fields.Selection([('manager', 'Manager'), ('user', 'User')],
                                        string="Safe Count Screen User")









