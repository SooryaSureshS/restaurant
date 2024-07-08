from odoo import api, fields, _, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_scrap_all(self):
        print("workinggg")
        self._check_company()
        stock_scrap = self.env['stock.scrap']
        scrap_location = self.env['stock.location'].search([('scrap_location', '=', True), ('usage', '=', 'inventory')])
        print(scrap_location, "scrap_location")
        for rec in self:
            for line in rec.move_line_ids_without_package:
                # print(line.product_id.name)
                # print(line.product_id.uom_name)
                # print(line.location_id.name)
                res = stock_scrap.create({
                    'product_id': line.product_id.id,
                    'scrap_qty': 1,
                    'product_uom_id': line.product_id.uom_id.id,
                    'location_id': line.location_id.id,
                    'scrap_location_id': scrap_location.id,
                    'picking_id': rec.id,
                    'date_done': fields.Datetime.now(),
                })
                res.name = self.env['ir.sequence'].next_by_code('stock.scrap') or _('New')
                res.state = 'done'
                # rec.date_done = fields.Datetime.now()
        return True
