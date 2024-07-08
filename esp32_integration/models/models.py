# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from psycopg2 import sql

from odoo import tools
from odoo import api, fields, models, _


class EspRfid(models.Model):
    _name = "rfid.container"
    _description = "Rfid Config"
    # _auto = False
    _order = 'id desc'

    # company_id = fields.Many2one('res.company', 'Company', readonly=True)
    # vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', readonly=True)
    name = fields.Char(string='Container Name', required=True, readonly=True, default=lambda self: _('New'), copy=False)
    barcode = fields.Char('Barcode Code')
    weight = fields.Float('Total Weight')
    product_ids = fields.One2many('rfid.container.line','rfid_id', string="Product Lines")
    partner_id = fields.Many2one('res.partner', 'Responsible', readonly=True)
    ssid = fields.Char('ssid')
    password = fields.Char('password')
    # date_start = fields.Date('Date', readonly=True)
    # vehicle_type = fields.Selection([('car', 'Car'), ('bike', 'Bike')], readonly=True)
    #
    # cost = fields.Float('Cost', readonly=True)

    @api.model
    def create(self, vals):
        print("ssssss", vals)
        print("sdsdsd",self.env['ir.sequence'].next_by_code('rfid.container'))
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('rfid.container') or _('New')
        return super(EspRfid, self).create(vals)
    # @api.model
    # def create(self, vals):
    #     print("ssssss",vals)
    #     print("ssssss",self.env['ir.sequence'].next_by_code('seq_rfid_container_order') )
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('seq_rfid_container_order') or _('New')
    #     result = super(EspRfid, self).create(vals)
    #     return result

    def check_connection(self):
        return True
class ProductInheritView(models.Model):

    _name = "rfid.container.line"

    rfid_id = fields.Many2one('rfid.container', string="Rfid")
    product_id = fields.Many2one('product.template', string="Product")
    rfid_code = fields.Char(string="Rfid Code")
    product_weight = fields.Char(string="Product weight")
    dynamic_ip = fields.Char(string="dynamic ip")
    status = fields.Selection([
        ('active', 'Active'),
        ('deactivate', 'Deactivate'),
        ('not_found', 'Not Found'),
        ('blocked', 'Blocked'),
    ], string='status', default='blocked')