from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class POSProgram(models.Model):
    _inherit = 'pos.order'

    delivery_type = fields.Selection([('dine_in','Dine In'),('takeway','Takeaway'),
                                      ('woosh','Woosh'),('uber','Uber Eats'),('door','Door Dash'),('menulog','Menulog'),('deliveroo','Deliveroo')])
    table_name = fields.Char()
    delivery_note = fields.Char()

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(POSProgram, self)._order_fields(ui_order)
        order_fields['delivery_type'] = ui_order.get('delivery_type', False)
        order_fields['table_name'] = ui_order.get('table_name', False)
        order_fields['delivery_note'] = ui_order.get('delivery_note', False)
        order_fields['note'] = ui_order.get('pos_order_note_payment', False)
        print("kjhgfd", ui_order.get('pos_order_note_payment', False))
        return order_fields



