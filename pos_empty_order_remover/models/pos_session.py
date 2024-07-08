from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _check_if_no_draft_orders(self):
        print('shek here')
        print(self)
        draft_orders = self.order_ids.filtered(lambda order: order.state == 'draft')
        for order in draft_orders:
            order.state = 'cancel'
        return True
        # try:
        #     res = super(PosSession, self).action_pos_session_closing_control()
        # except:
        #     pass
