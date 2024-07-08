from odoo import fields, models
import requests
import base64


class ShipAnyWaybill(models.TransientModel):
    _name = "shipany.waybill"
    _description = "WayBill Type"

    shipany_trk_no = fields.Char(string="Tracking Number")
    stock_picking_id = fields.Many2one('stock.picking')
    waybill_url = fields.Char(string="Waybill URL")
    waybill = fields.Binary(string="Way Bill")

    # Add Waybill as an attachment in DO
    def action_print_report(self):
        if self.waybill_url:
            url = "%s" % self.waybill_url
            response = requests.get(url)
            obj = response.content
            myObj = [base64.b64encode(obj)]
            attachment = self.env['ir.attachment'].create({'name': 'Waybill',
                                                           'datas': myObj[0],
                                                           'store_fname': 'Waybill',
                                                           'res_model': 'stock.picking',
                                                           'res_id': self.stock_picking_id.id, })
