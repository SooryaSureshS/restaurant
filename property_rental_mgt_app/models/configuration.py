# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PropertyFacility(models.Model):
    _name = 'property.facility'
    _description = 'Property Facility Service'

    name = fields.Char("Name", required=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)

class PartialPayment(models.Model):
    _name = 'partial.payment'
    _description = 'Partial Payment'

    name = fields.Char("Name", required=True)
    number_of_pay = fields.Integer("#Partial Payment", required=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)

    @api.model
    def create(self, vals):
        if vals['number_of_pay'] <= 0:
            raise UserError(_("Please enter valid # Payments"))
        res = super(PartialPayment, self).create(vals)
        return res


class DelayFine(models.Model):
    _name = 'delay.fine'
    _description = 'Delay Fine Payment'

    name = fields.Char("Name", required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    allow_fine = fields.Boolean("Allow Fine on Delay Payment?")
    after_days = fields.Integer("Delay Fine After Days")
    fine_on_property_price = fields.Float("Fine on Property Price")

    @api.model
    def create(self, vals):
        if vals['allow_fine'] == True:
            if vals['after_days'] <= 0 or vals['fine_on_property_price'] <=0:
                raise UserError(_("Please enter valid Days or Payment Delay Fine (%)..?"))
        res = super(DelayFine, self).create(vals)
        return res

    def write(self, vals):
        res = super(DelayFine, self).write(vals)
        if self.allow_fine == True:
            if self.after_days <= 0 or self.fine_on_property_price <=0:
                raise UserError(_("Please enter valid Days or Payment Delay Fine (%)..?"))
        return res

class PropertyType(models.Model):
    _name = 'property.type'
    _description = 'Property Type'

    name = fields.Char("Name", required=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
