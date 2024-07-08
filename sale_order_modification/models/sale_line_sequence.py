from odoo import fields, models, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    seq = fields.Float(string="SEQ", related='')

    def _compute_seq(self):

        for rec in self:
            sale = rec.order_id
            sec_seq = 0.00
            sub_seq = 0.0
            for lines in sale.order_line:

                if sec_seq > 0.00:
                    print("line_seq")
                    lines.seq = sec_seq + sub_seq
                    sub_seq += 0.01

                else:
                    print("else_line")
                    lines.seq = sec_seq + 1
                    sec_seq += 1.00


