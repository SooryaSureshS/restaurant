# -*- coding: utf-8 -*-
import hashlib

from odoo import api, models, _, fields
from odoo.exceptions import UserError




class employeeInherit(models.Model):
    _inherit = 'hr.employee'

    employee_pin = fields.Integer(
        string='POS Pin')

    def get_barcodes_and_pin_hashed(self):

        employee_data = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)])
        data =0
        for x in employee_data:
            data=x.employee_pin
        return data











    # @api.model
    # def get_employee(self):
    #     uid = self.session.uid
    #
    #     data = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)])
    #     employee = self.env['res.users'].sudo().search_read([('id', '=', uid)], limit=1)
    #     print(data,"data")
    #     print(data.pin,"datappp")
    #     print(employee,"datappp")
    #     print(employee.pin,"datappp")
    #     return employee.pin


