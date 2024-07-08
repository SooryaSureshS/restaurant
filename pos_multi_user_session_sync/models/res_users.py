from odoo import models, fields
from odoo import models, fields, api, _
from odoo.exceptions import AccessError

class ResUsers(models.Model):
    _inherit = 'res.users'

    table_id = fields.Many2one('restaurant.table', string='Table')



class PosOrdersInheritsData(models.Model):
    _inherit = 'pos.order'

    parent_order = fields.Many2one('pos.order', string='Parent order')
    payment_initiation = fields.Many2one('hr.employee', string='Cahier Selected')
    payment_proceed = fields.Boolean(default=False, string='Payment Passed')
    uid_name = fields.Char(string='uid')


    def _order_fields(self, ui_order):
        order = super(PosOrdersInheritsData, self)._order_fields(ui_order)
        if ui_order['payment_initiation'] and ui_order['payment_proceed']:
            order['payment_initiation'] = ui_order['payment_initiation']
            order['payment_proceed'] = ui_order['payment_proceed']
            order['uid_name'] = ui_order['uid']
        return order

    @api.model
    def create_from_ui(self, orders, draft=False):
        draft = True
        order_ids = super(PosOrdersInheritsData, self).create_from_ui(orders, draft)

        print("orderssss", orders, draft,order_ids)
        # d
        # for order in self.sudo().browse([o['id'] for o in order_ids]):
        #     if order.loyalty_points != 0 and order.partner_id:
        #         order.partner_id.loyalty_points += order.loyalty_points
        return order_ids