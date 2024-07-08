from odoo import models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def set_orders_printed(self):
        sale_objs = self.env['sale.order'].sudo().search([('order_line.order_printed', '=', False)])
        pos_objs = self.env['pos.order'].sudo().search([('lines.order_printed', '=', False)])
        for s in sale_objs:
            for l in s:
                l.order_printed = True
                self.env.cr.commit()
        for p in pos_objs:
            for l in p:
                l.order_printed = True
                self.env.cr.commit()
